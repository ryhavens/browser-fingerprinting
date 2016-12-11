GLOBALS = {};
SEND_BUFFER = [];
IS_SENDING_BUFFER = false;

$(document).ready(function() {
    initEventHandlers();
    initFingerprint();
});

function defaultCallback(data) {
    console.log("Request complete.");
    console.log(data);
}

function sendAllDataInBuffer(data) {
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
}

function initFingerprint() {
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

function sendActivityLogToServer(activity, callback) {
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
        success: function(data) { callback(data) },
        error: function(err) { console.log(err); },
        dataType: 'json'
    });   
}