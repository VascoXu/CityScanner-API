import os, json, boto3
from io import StringIO, BytesIO
from botocore.exceptions import ClientError

from datetime import datetime,timedelta

def create_presigned_url(bucket_name, object_name, file_name, expiration=3600):
    """Generate a presigned URL to share an S3 object"""
    
    S3_BUCKET = os.environ.get('S3_BUCKET')
    s3_client = boto3.client('s3')

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name,
                                                            'ResponseContentDisposition': f"attachment; filename = {file_name}"},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def upload_file(stream, bucket, object_name=None):
    """Upload a stream to an S3 bucket"""

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Convert StringIO to BytesIO
    buffer = BytesIO(stream.getvalue().encode('utf-8'))

    # Upload the file
    s3_client = boto3.client('s3')

    # Set expiration of object to 30 minutes
    expiration = datetime.utcnow() + timedelta(minutes=30)
    try:
        response = s3_client.upload_fileobj(buffer, bucket, object_name,
                                            ExtraArgs={'Expires': expiration})
    except ClientError as e:
        logging.error(e)
        return False
    return True
