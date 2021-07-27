var summaries = null;

// Show loading spinner
$("#loading").show();
$("#hotspots").hide();
$("#content").hide();

// Send data to API
$.ajax({
    url: '/api/datasets',
    type: 'GET',
    async: true,
    success: function(data) {
        $("#loading").hide();
        $("#content").show();
        datasets = data['results'];

        // Load summary
        load_datasets(datasets);
    },
});

// Open the date selector on toggle
$("#options").on('change', function() {
    $("#between-dates").toggle();
});

$("#hotspots").on('click', function() {
    window.open("foliumHotspotMap.html", "_blank");
})

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

    var select_between = $("#select-between").is(":checked");
    if (select_between) {
        var start_time = $("#start-time").val();
        var end_time = $("#end-time").val();
        data['start'] = start_time;
        data['end'] = end_time;
    }

    // Send request for latest data
    $.ajax({
        url: '/api/hotspots/',
        type: 'POST',
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: 'json',
        success: function(data) { 
            $("#hotspots").show();
            console.log(data.redirect)
            window.location.href = data.redirect
            if (!('error' in data)) {
            }
            else {
                // Display error message
                display_error("No data available.");
            }
        },
        error: function(xhr, status, error) {
            hide_spinner();

            console.log(error)

            // Display error message
            var error_message = xhr.responseJSON['error'] || "Download failed!";
            display_error(error_message);
        }
    });
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
    $("#calculate-text").text("Calculating...");
}

function hide_spinner()
{
    $("#download-spinner").css('display', "none");
    $("#calculate-text").text("Calculated");
}

function load_datasets(datasets)
{
    for (let i = 0; i < datasets.length; i++) {
        $("#datasets").append(new Option(datasets[i], datasets[i]));
    }
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