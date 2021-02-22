document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Send messages
    document.querySelector('#send_message').onclick = () => {
        socket.emit('incoming-msg', {'msg': document.querySelector('#user_message').value,
            'username': username, 'room': room});

        document.querySelector('#user_message').value = '';
    };

    // Display all incoming messages
    socket.on('message', data => {

        // Display current message

        const p = document.createElement('p');
        const br = document.createElement('br')
        // Display user's own message

        p.setAttribute("class", "my-msg");

        //Append
        document.querySelector('#display-message-section').append(p);

        // Display other users' messages
        p.setAttribute("class", "others-msg");

        //Append
        document.querySelector('#display-message-section').append(p);

    });
});