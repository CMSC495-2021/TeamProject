document.addEventListener('DOMContentLoaded', () => {
    // Connect to websocket
   var socket = io();

    //MESSAGE HANDLER
    socket.on('message', data => {
        const p = document.createElement('p');
        p.innerHTML = data;
        document.querySelector('#message-area').append(p);

        console.log(`Message Sent From Browser: ${data}`)
    });


    //event listener for send button
    document.querySelector('#send-message').onclick = () => {
        socket.send(document.querySelector('#user-message').value);
        };
});