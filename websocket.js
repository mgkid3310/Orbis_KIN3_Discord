function useModule(url, callback, parameter) {
	var script = $w.Document.createElement('script');
	script.src = url;
	script.onload = callback;
	script.parameter = parameter;
	$w.Document.getElementsByTagName('head')[0].appendChild(script);
}

function useSocket(callback, parameter) {
	useModule('https://cdn.socket.io/socket.io-1.0.0.js', callback, parameter);
}

var send_tcp = function() {
	var socket = io.connect('https://118.33.133.53:2306/', {transports: ['websocket']});
	if(socket !== null && socket !== undefined){
		socket.emit('sMsg', this.parameter);
	}
}

useSocket(send_tcp, 'test send message');
