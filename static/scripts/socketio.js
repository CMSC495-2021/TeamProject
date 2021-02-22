document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect('http://' + document.domain + ':' + document.port);

    document.querySelector('#send').onclick = () => {
        socket.send(document.querySelector('#message').value);
        };

    socket.on('message', data => {
        console.log(`Message Rx'd: ${data}`)

        const p = document.createElement('p');
        const br = document.createElement('br');
        p.innerHTML = data;

        document.querySelector('#chat-view').append(p);
        });

    socket.on('some-event', data => {
        console.log(data)
    });

});