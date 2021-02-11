document.addEventListener('DOMContentLoaded', () => {
var socket = io();

socket.on('connect', () => {
        socket.send('A User Connected!');
});

socket.on('message', data => {
    const p = document.createElement('p');
    //const brk = document.createElement('brk');
    p.innerHTML = data;
    document.querySelector('#display-area').append(p);
});



document.querySelector('#send_message_button').onclick = () => {

    socket.send(document.querySelector('#message_box').value);
}


})