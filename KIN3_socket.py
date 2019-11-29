import asyncio

async def start_tcp_server():
	print('Starting TCP server')

	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	tcp_server_ip = readRines[0].strip().split(':')
	server = await asyncio.start_server(handle_tcp_inbound, tcp_server_ip[0], tcp_server_ip[1])
	addr = server.sockets[0].getsockname()
	print(f'Server started on {addr}')

	async with server:
		print(f'Request handling started')
		print('--------')
		await server.serve_forever()

async def test_tcp_server():
	print('Testing TCP server')

	message = 'hello world apple banana'
	fs = [asyncio.ensure_future(start_tcp_test_client(word)) for word in message.split()]
	await asyncio.wait(fs, timeout = 4)
	print(f'TCP server test complete')
	print('--------')

async def handle_tcp_inbound(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
	addr = writer.get_extra_info('peername')
	print(addr)
	data = await reader.read(100)
	message = data.decode()
	# sock.getpeername()

	print(f"[S]Received {message!r} from {addr!r}")
	print(f'[S]Echoing: {message!r}')
	writer.write(data)
	await writer.drain()

	print("[S]Close the connection")
	writer.close()
	await writer.wait_closed()

async def start_tcp_test_client(message: str):
	reader: asyncio.StreamReader
	writer: asyncio.StreamWriter

	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	tcp_server_ip = readRines[0].strip().split(':')
	reader, writer = await asyncio.open_connection(tcp_server_ip[0], tcp_server_ip[1])

	print('[C]Connected')
	writer.write(message.encode())
	await writer.drain()
	print(f'[C]Send: {message!r}')

	data = await reader.read(100)
	print(f'[C]Received: {data.decode()!r}')

	print('[C]Closing...')
	writer.close()
	await writer.wait_closed()
