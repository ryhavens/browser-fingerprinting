GLOBALS = {};
SEND_BUFFER = [];
IS_SENDING_BUFFER = false;

$(document).ready(function() 
{
    initEventHandlers();
    initFingerprint();
});

function defaultCallback(data) 
{
    console.log("Request complete.");
    console.log(data);
}

function sendAllDataInBuffer(data) 
{
    console.log("Request complete.");
    console.log(data);
    if (!IS_SENDING_BUFFER) {
        IS_SENDING_BUFFER = true;
        for (var i = 0; i < SEND_BUFFER.length; i++) {
            SEND_BUFFER[0]();
            SEND_BUFFER.shift();
        }
    }
    IS_SENDING_BUFFER = false;
}

function initEventHandlers() 
{
    $('#clickme').on('click', function(e) {
        // wait for fingerprint
        if (GLOBALS['fingerprint']) {
            sendActivityLogToServer("Clickme clicked", defaultCallback);
        }
        else {
            SEND_BUFFER.push(function() { sendActivityLogToServer("Clickme clicked", defaultCallback)});
        }
    });

    $('#data').on('click', 'a', function(e) {
        e.preventDefault();
        if (GLOBALS['fingerprint']) {
            $('#results').html('<p>Loading...</p>');
            getFingerprintData(GLOBALS['fingerprint'], function(data) {
                var parsedData = JSON.parse(data);
                $('#results').append($('<h3>').text('Your fingerprint: ' + parsedData['fingerprint']));
                $('#results').append($('<p>').text('Created at: ' + new Date(parsedData['created_at']['$date'])));
                $('#results').append($('<p>').text('Updated at: ' + new Date(parsedData['updated_at']['$date'])));
                $('#results').append($('<h3>').text('Your activity log:'));
                parsedData['activity_log'].sort(function(a, b) {
                    return (b['time']['$date'] - a['time']['$date']);
                });
                for (var i = 0; i < parsedData['activity_log'].length; i++) {
                    $('#results').append($('<p>').text(parsedData['activity_log'][i]['activity']));
                    $('#results').append($('<p>').text(new Date(parsedData['activity_log'][i]['time']['$date'])));
                }
                $('#results').append($('<h3>').text('Information used to compute your fingerprint:'));
                parsedData['components'] = JSON.parse(parsedData['components']);
                for (var i = 0; i < parsedData['components'].length; i++) {
                    $('#results').append($('<p>').text(parsedData['components'][i]['key']));
                    $('#results').append($('<p>').text(parsedData['components'][i]['value']));
                }
            });
        }
    });
}

function initFingerprint() 
{
    var fp = new Fingerprint2().get(function(result, components) {
        sendDataToServer(result, components, sendAllDataInBuffer);
        console.log(result);
        console.log(components);
        GLOBALS['fingerprint'] = result;
        GLOBALS['components'] = components;
    });
}

function sendDataToServer(result, components, callback)
{
    var ajax = $.ajax({
        type: 'POST', 
        url: 'store_fingerprint',
        contentType: 'application/json',
        data: JSON.stringify({
                              'action': 'check',
                              'fingerprint': result,
                              'components': components
                            }),
        success: function(data) { callback(data) },
        error: function(err) { console.log(err); },
        dataType: 'json'
    });
}

function sendActivityLogToServer(activity, callback) 
{
    var ajax = $.ajax({
        type: 'POST', 
        url: 'store_fingerprint',
        contentType: 'application/json',
        data: JSON.stringify({
                              'action': 'activity',
                              'fingerprint': GLOBALS['fingerprint'],
                              'components': GLOBALS['components'],
                              'activity': activity
                            }),
        success: function(data) { callback(data); },
        error: function(err) { console.log(err); },
        dataType: 'json'
    });   
}

function getFingerprintData(fingerprint, callback) 
{
    var ajax = $.ajax({
        type: 'GET',
        url: 'view_fingerprint/'+fingerprint,
        contentType: 'application/json',
        data: JSON.stringify({
                              'action': 'view',
                              'fingerprint': GLOBALS['fingerprint'],
                          }),
        success: function(data) { callback(data); },
        error: function(err) { alert("Sorry, something went wrong."); for (var key in data) { alert(key + " " + data[key]); } },
    });
}