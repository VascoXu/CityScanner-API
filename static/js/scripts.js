$(document).ready(function() {

    var summaries = null;

    // Send data to API
    $.ajax({
        url: '/api/summary',
        type: 'GET',
        async: false,
        success: function(data) {
            summaries = data['results'];
        },
    });

    // Update summary on load
    update_summary(summaries);

    // Highlight selected page in navbar
    $(".navbar-nav .nav-link").each(function() {
        if (window.location.href == this.href) {
            $(".navbar-nav .nav-item").removeClass("active");
            $(this).addClass("active");
        }
    });

    // Update summary when timezone is changed
    $("#timezones").on('change', function() {
        update_summary(summaries);
    });

    // Update summary when selection is changed
    $("#datasets").on('change', function() {
        update_summary(summaries);
    });

    // Open the date selector on toggle
    $("#options").on('change', function() {
        $("#between-dates").toggle();
    });

    // Download City Scanner data based on user selections
    $("#download-button").on('click', function() {
        // Load spinner
        load_spinner();

        // Package data
        var dataset = $("#datasets").val();
        var timezone = $("#timezones").val();
        var data = {
            'dataset': dataset,
            'timezone': timezone,
        };
        
        var download_between = $("#download-between").is(":checked");
        if (download_between) {
            var start_time = $("#start-time").val();
            var end_time = $("#end-time").val();
            data['start'] = start_time;
            data['end'] = end_time;
        }

        // Send data to API
        var filename = $("#filename").val();
        if ($.trim(filename) == "") {
            // Assign default value to filename is none is provided
            filename = dataset;
        } 
        filename = `${filename}.csv`;

        // Send request for latest data
        $.ajax({
            url: '/api/latest',
            type: 'GET',
            data: data,
            success: function(data) {  
                if (!('error' in data)) {
                    var job_id = data['job_id'];

                    // Poll the status of the download
                    function pollLatestData() {
                        $.ajax({
                            url: `/api/latest/${job_id}`,
                            type: 'GET',
                            async: false,
                            success: function(data) {
                                if ('url' in data) {
                                    var url = data['url'];
                                    // Download CSV from Amazon S3
                                    var download_link = document.createElement('a');
                                    download_link.setAttribute('href', url);
                                    download_link.setAttribute('download', filename);
                                    download_link.click();
                                    download_link.remove();
                                    
                                    // Display success message
                                    hide_spinner();
                                    display_success();
                                }
                                else {
                                    setTimeout(pollLatestData, 2000);
                                }
                            },
                        });
                    }
                    pollLatestData();
                }
                else {
                    // Display error message
                    display_error("No data available.");
                }
            },
            error: function(xhr, status, error) {
                hide_spinner();

                // Display error message
                var error_message = xhr.responseJSON['error'] || "Download failed!";
                display_error(error_message);
            }
        });
    })
})

function display_error(error_message)
{
    $("#success").hide();
    $("#warning").show();
    $(".warning-text").text(error_message);
    window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'smooth'
    });
}

function display_success()
{
    $("#warning").hide();
    $("#success").show();
    window.scrollTo({
        top: 0,
        left: 0,
        behavior: 'smooth'
    });
}

function load_spinner()
{
    $("#download-spinner").css('display', "inline-block");
    $("#download-text").text("Downloading...");
}

function hide_spinner()
{
    $("#download-spinner").css('display', "none");
    $("#download-text").text("Download");
}

function update_summary(summaries)
{
    var timezone = $("#timezones").val();
    var dataset = $("#datasets").val();
    var result = summaries.find(summary => {
        return summary.dataset == dataset
    });
    var timezone_text = $("#timezones option:selected").text();
    $(".timezone").text(timezone_text);
    $("#datapoints").text(result['count']);
    $("#devices").text(result['devices']);
    $("#start").text(format_date(result['start'], timezone));
    $("#end").text(format_date(result['end'], timezone));    
    $("#filename").val(dataset);
}

function download_csv(data, filename)
{
    /*
    // Error checking
    if (data.length == 0) {
        return false;
    }

    // Object to CSV
    var headers = Object.keys(data[0]);
    var csv = [
        headers.join(','),
        ...data.map(row => headers.map(field => JSON.stringify(row[field])).join(','))
    ].join('\r\n');
    */
    
    // Download CSV
    var link = document.createElement("a");
    var blob = new Blob([data], {type: "data:file/csv;charset=utf-8;"})
    link.setAttribute("href", URL.createObjectURL(blob));
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    return true;
}

function format_date(unix_date, timezone=null)
{
    // Format UNIX date
    var date = new Date(unix_date * 1000)
    if (timezone) {
        date = new Date(date.toLocaleString("en-US", {timeZone: timezone}));
    }
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    let month = monthNames[date.getMonth()];
    let day = date.getDate();
    let year = date.getFullYear();
    let hour = date.getHours();
    let min = date.getMinutes();
    let sec = date.getSeconds();
    return day + " " + month + " " + year + ", " + hour + ":" + min + ":" + sec;
}