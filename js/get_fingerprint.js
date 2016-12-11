$(document).ready(function() {
    var fp = new Fingerprint2().get(function(result, components) {
        sendDataToServer(result, components, function(data) { console.log(data); console.log("complete"); });
        console.log(result);
        console.log(components);
    });
});

function sendDataToServer(result, components, callback)
{
    var ajax = $.ajax({
        type: 'POST', 
        url: 'store_fingerprint',
        contentType: 'application/json',
        data: JSON.stringify({
                              'fingerprint': result,
                              'components': components
                            }),
        success: function(data) { callback(data) },
        error: function(err) { console.log(err); },
        dataType: 'json'
    });
}