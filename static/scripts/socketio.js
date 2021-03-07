// jquery stuff for SocketIO
$(document).ready(function() {

    namespace = '/chatmain';
    var socket = io(namespace);
    var usersOnline = [];


    socket.on('connect', function() {
        socket.emit('broadcast_event', {data: 'connected to the SocketServer...'});
    });

    socket.on('response', function(msg, cb) {
        if(msg.username == sessionStorage.username || sessionStorage.username == undefined){
            $('#chat-view').append('<br><div class="message sent"><span class="avatar">'+msg.initials+'</span><p>'+msg.data+'</p></div>');
        }
        else{
            $('#chat-view').append('<br><div class="message received"><span class="avatar">'+msg.initials+'</span><p>'+msg.data+'</p></div>');
        }
        if(usersOnline.indexOf(msg.username) == -1){
            usersOnline.push(msg.username);
            var li = document.createElement('li');
            li.className = "online";
            li.innerText = msg.username;
            document.getElementById('usersOnline').appendChild(li);
        }
        document.getElementById('chat-view').scrollTo(0,document.getElementById('chat-view').scrollHeight);
        if (cb)
            cb();
    });

    $('form#chatSend').submit(function(event) {
        sessionStorage.username = event.target.dataset.username;
        if ($('#message_data').val()){
            socket.emit('broadcast_event', {data: $('#message_data').val()});
            $(' #message_data ').val('').focus();
        }
        return false;
    });
    
    $('#logout').click(function(event) {
        socket.emit('disconnect_event');
        $(location).attr('href', '/login');
        return false;
    });
});