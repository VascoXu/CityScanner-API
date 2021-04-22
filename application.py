import os
import sys
import csv
from io import StringIO, BytesIO
from redis import Redis
import rq

from flask import Flask, flash, redirect, render_template, request, session, make_response, jsonify, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from mongo.mongo import *
from s3 import upload_file,create_presigned_url
from helpers import *

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Setup Redis
REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
conn = Redis.from_url(REDIS_URL)
task_queue = rq.Queue('scl-tasks', connection=conn)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure MongoDB
MONGO_URL = os.environ.get("MONGO_URL")
MONGO_DB = os.environ.get("MONGO_DB")
mongodb = MongoConnection(url=MONGO_URL, db=MONGO_DB)


def export_csv(params):
    """Generate CSV from MongoDB data and upload it to Amazon S3"""

    # Unpack parameters
    collection = params['collection']
    timezone = params['timezone']
    limit = params['limit']
    start = params['start']
    end = params['end']

    # Query MongoDB
    rows = list(mongodb.find(collection=collection, timezone=timezone, limit=limit, start=start, end=end))

    # Return error message if not data is available
    if len(rows) == 0:
        return jsonify({'error': "Error! Not data available."})

    # Convert rows to StringIO and upload to Amazon S3
    filename = f"{collection}.csv"
    data = StringIO()
    writer = csv.writer(data, delimiter=",")
    writer.writerow(dict(rows[0]).keys())
    for row in rows:
        writer.writerow(dict(row).values())
    upload_file(data, "scl-api", filename)

    # Create presigned url
    url = create_presigned_url("scl-api", filename)

    return url


@app.route("/", methods=["GET"])
def index():
    """Home page for interacting with the API"""

    summaries = list(mongodb.summary())
    return render_template("index.html", summaries=summaries)


@app.route("/docs", methods=["GET"])
def docs():
    """Home page for API documentation"""
    return render_template("swaggerui.html")


@app.route("/api/datasets/", methods=["GET"])
def datasets():
    """Gets a list of all available datasets.

    :return: List of datasets
    :rtype: JSON
    """

    # Retrieving datasets must be via GET
    if request.method != "GET":
        return make_response(jsonify({"error": "GET request required."}), 400)

    # Query Mongo for all available datasets
    all_collections = list(mongodb.list_collections())
    response = {"results": all_collections}

    # Return a JSON response
    return jsonify(response)


@app.route("/api/latest/", methods=["GET", "POST"])
def latest():
    """Gets latest data from MongoDB.

    :param dataset: Dataset to retrieve from
    :type dataset: str, required

    :param limit: Number of entries to retrieve
    :type limit: int, optional

    :param timezone: 
    :type timezone: str, optional

    :param start: Start date in format YYYY-MM-DDT20HH:MM:SS
    :type start: str, optional  

    :param end: End date in format YYYY-MM-DDT20HH:MM:SS
    :type end: str, optional  

    :return: List of data
    :rtype: JSON
    """

    # Parse GET parameters
    params = request.args
    collection = params.get("dataset", None)
    timezone = params.get("timezone", None)
    limit = params.get("limit", None)
    start = params.get("start", None)
    end = params.get("end", None)

    # Pack parameters into a dict
    params = {'collection': collection, 'timezone': timezone, 'limit': limit, 'start': start, 'end': end}

    # Ensure start and end date are valid
    if start and end:
        first_date = list(mongodb.get_start_date(collection=collection))[0]['time']
        last_date = list(mongodb.get_end_date(collection=collection))[0]['time']

        unix_start = int(string_to_datetime(start, timezone).timestamp())
        unix_end =  int(string_to_datetime(end, timezone).timestamp())

        if unix_start == unix_end:
            return make_response(jsonify({"error": "Start date must be larger than end date."}), 400)

        if unix_start > unix_end:
            return make_response(jsonify({"error": "Start date is larger than end date."}), 400)

        if unix_start > last_date or unix_start < first_date:
            return make_response(jsonify({"error": "Start date is invalid."}), 400)

        if unix_end < first_date:
            return make_response(jsonify({"error": "End date is invalid."}), 400)

    # Ensure a collection is provided
    if not collection:
        return make_response(jsonify({
            "error": "Collection required."
        }), 400)

    # Query MongoDB
    rows = mongodb.find(collection=collection, timezone=timezone, limit=limit, start=start, end=end)
    

    # Convert rows to StringIO and upload to Amazon S3
    filename = f"{collection}.csv"
    data = StringIO()
    writer = csv.writer(data, delimiter=",")
    writer.writerow(dict(rows[0]).keys())
    for row in rows:
        writer.writerow(dict(row).values())
    
    """
    # Create response from StringIO output
    res = make_response(data.getvalue())
    res.headers['Content-Disposition'] = "attachment; filename=test.csv"
    res.headers['Content-type'] = "text/csv"
    """

    # Launch background task to export CSV 
    rq_job = task_queue.enqueue_call(func=export_csv,
                                    args=(params,)
                                    )

    # Return job id to client
    return jsonify({'job_id': rq_job.get_id()})


@app.route("/api/latest/<job_id>", methods=["GET"])
def latest_results(job_id):
    """ """

    # Check if job is finished
    rq_job = task_queue.fetch_job(job_id)
    if rq_job.is_finished:
        url = rq_job.result
        return jsonify({'url': url}) 
    else:
        return jsonify({'result': rq_job.is_finished}) 


@app.route("/api/summary/", methods=["GET"])
def summary():
    """Gets a summary of MongoDB collections.

    :return: Summary of data
    :rtype: JSON
    """

    # Parse GET parameters
    params = request.args
    collection = params.get("collection", None)

    result = mongodb.summary(collection)
    response = {"results": result}
    return jsonify(response)


@app.route("/api/AQ-hotspots/", methods=["GET"])
def aq_hotspots():
    """Gets locations of air pollution hotspots for a given city and a given timeframe.

    :param dataset: Dataset to retrieve from
    :type dataset: str, required

    :return: Location of air pollution hotspots
    :rtype: JSON
    """

    return jsonify(response)


@app.route("/api/AQ-averages/", methods=["GET"])
def averages():
    """Gets air quality hourly/daily/monthly/yearly averages for a given street segment in a city and a given timeframe.

    :param dataset: Dataset to retrieve from
    :type dataset: str, required

    :return: Air quality averages
    :rtype: JSON
    """

    return jsonify(response)


@app.route("/api/Noise-averages/", methods=["GET"])
def noise_hotspots():
    """Gets locations of noise pollution hotspots for a given street segment in city and a given timeframe.

    :param dataset: Dataset to retrieve from
    :type dataset: str, required

    :return: Location of noise pollution hotspots
    :rtype: JSON
    """

    return jsonify(response)


@app.template_filter("format_unix")
def format_unix(date):
    """Format UNIX timestamp"""

    monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    date = datetime.utcfromtimestamp(date)
    month = date.month
    day = date.day
    year = date.year
    hour = date.hour
    minutes = date.minute
    seconds = date.second
    return f"{day} {monthNames[month - 1]} {year}, {hour}:{minutes}:{seconds}"


# def errorhandler(e):
#     """Handle error"""
#     if not isinstance(e, HTTPException):
#         e = InternalServerError()
#     return make_response(jsonify({"error": "Sorry, an error has occured."}), 400)


# # Listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)
