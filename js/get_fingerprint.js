GLOBALS = {}

$(document).ready(function() {
    initEventHandlers();
    initFingerprint();
});

function defaultCallback(data) {
    console.log("Request complete.");
    console.log(data);
}

function initEventHandlers() 
{
    $('#clickme').on('click', function(e) {
        sendActivityLogToServer("Clickme clicked", defaultCallback);
    });
}

function initFingerprint() {
    var fp = new Fingerprint2().get(function(result, components) {
        sendDataToServer(result, components, defaultCallback);
        console.log(result);
        console.log(components);
        GLOBALS['result'] = result;
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
                              'activity': activity
                            }),
        success: function(data) { callback(data) },
        error: function(err) { console.log(err); },
        dataType: 'json'
    });   
}