var socket;
$(document).ready(function () {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function () {
        socket.emit('joined', {});
    });
    socket.on('status', function (data) {
        $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    socket.on('message', function (data) {
        $('#chat').val($('#chat').val() + data.msg + '\n');
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });
    $('#input_area').keypress(function (e) {
        var code = e.keyCode; //|| e.which;
        if (code == 13) {
            text = $('#input_area').val();
            $('#input_area').val('');
            socket.emit('text', { 'msg': text });
        }
    });
});
function leave_room() {
    socket.emit('left', {}, function () {
        socket.disconnect();

        window.location.href = "{{ url_for('main.index') }}";
    });
}