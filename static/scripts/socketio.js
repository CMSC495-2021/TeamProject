// jquery stuff for SocketIO
$(document).ready(function() {

    // Set the namespace in case we want to have multiples
    namespace = '/chatmain';
    var socket = io(namespace);

    // Sends the connection event to show logon in chat
    // Can this be used for status?
    socket.on('connect', function() {
        socket.emit('broadcast_event', {data: 'connected to the SocketServer...'});
    });

    // Creates response element from app for display in chat main window...
    socket.on('response', function(msg, cb) {
        $('#chat-view').append('<br><div class="message received"><span class="avatar">'+msg.initials+'</span><p>'+msg.data+'</p></div>');
        if (cb)
            cb();
    });

    // bound to send button to send a brodcasted message from input to app
    // If nothing in input, don't broadcast
    $('form#chatSend').submit(function(event) {
        if ($('#message_data').val()){
            socket.emit('broadcast_event', {data: $('#message_data').val()});
            $(' #message_data ').val('').focus();
        }
        return false;
    });
    
    // implement for logout button
    $('#logout').click(function(event) {
        socket.emit('disconnect_event');
        $(location).attr('href', '/login');
        return false;
    });
});