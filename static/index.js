document.addEventListener("DOMContentLoaded", function() { 
    var textWrapper = document.querySelector('#text-wrapper');
    
    document.querySelector('#form').addEventListener('submit', event => {
        event.preventDefault();
    });

    document.querySelector('#reconnect').addEventListener('click', event => {
        window.location.reload(false); 
    });

    // Connect to websockets
    var send_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/send');
    var user_creation_socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + '/adduser');

    // sending messages socket handler 
    send_socket.on('connect', () => {
        console.log('connected');
        document.querySelector('#form').addEventListener('submit', () => { 
                var inputText = document.querySelector('#text');
                send_socket.emit('send_msg', {'msg': inputText.value});
                inputText.value = '';
        }, false);
    });
    

    send_socket.on('broadcasting_text', data => {
        newP = document.createElement('p');
        newP.innerHTML = data.selection;
        textWrapper.append(newP);
    });

    send_socket.on('change_turn', data => {
        document.querySelector('#turn').innerHTML = 'Your turn';
        document.querySelector('#submit').disabled = false;

    });

    send_socket.on('finish_texting', data => {
        document.querySelector('#turn').innerHTML = 'Your friend turn';
        document.querySelector('#submit').disabled = true;
    });

    //user creation socket handlers

    user_creation_socket.on('connect', () => {
        console.log('connected');

        document.querySelector('#send_username').addEventListener('click', event => {
            event.preventDefault();
            var usernameInput = document.querySelector('#username');
            if(usernameInput.value.match(/^[A-Za-z]+/i)){
                document.querySelector('#your-name').innerHTML = usernameInput.value
                document.querySelector('#send-user-form').classList.add('d-none');
                user_creation_socket.emit('username',usernameInput.value);
            } else {
                usernameInput.classList.add('error-input');
            }
        });
    });

    user_creation_socket.on('disconnect', () => {
        console.log('disconect');
    });

    user_creation_socket.on('partnerLeft', data => {
        document.querySelector('#reconnect').classList.remove('d-none');
        document.querySelector('#partnerName').classList.add('d-none');
        document.querySelector('#send_username').classList.add('d-none');
        document.querySelector('#turn').innerHTML = 'Your friend <bold>left</bold>';
    });

    user_creation_socket.on('partnerOK', data => {
        document.querySelector('#partnerName').innerHTML = 'Your friend is: ' + data.newPartner;
        document.querySelector('#turn').innerHTML = 'Your friend turn';
    });

    user_creation_socket.on('startTexting', data => {
        document.querySelector('#turn').innerHTML = 'Your turn';
        document.querySelector('#partnerName').innerHTML = 'Your friend is: ' + data.newPartner;
        document.querySelector('#submit').disabled = false;
    });

    user_creation_socket.on('waitingForPartner', data => {
        document.querySelector('#partnerName').innerHTML = 'Waiting for partner...';
    });

});