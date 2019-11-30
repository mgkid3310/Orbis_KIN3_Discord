import time
import asyncio

import KIN3_Esi
import KIN3_database
import KIN3_waitlist

async def start_tcp_server(bot, tcp_server = None):
	print(f'{time.time()} : Starting TCP server')

	if tcp_server is not None:
		print(f'{time.time()} : Server already existing')
		print(f'{time.time()} : --------')
		return tcp_server

	print(f'{time.time()} : No server existing')
	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	tcp_server_ip = readRines[0].strip().split(':')
	tcp_server = await asyncio.start_server(handle_tcp_inbound, tcp_server_ip[0], tcp_server_ip[1])
	tcp_addr = tcp_server.sockets[0].getsockname()
	print(f'{time.time()} : Server started on {tcp_addr}')
	print(f'{time.time()} : Request handling started')
	print(f'{time.time()} : --------')

	bot.loop.create_task(start_serve(tcp_server))

	return tcp_server

async def start_serve(tcp_server):
	async with tcp_server:
		await tcp_server.serve_forever()

async def handle_tcp_inbound(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
	addr = writer.get_extra_info('peername')
	print(addr)
	data = await reader.read(100)
	message = data.decode()
	# sock.getpeername()

	print(f'{time.time()} : [S]Received {message!r} from {addr!r}')
	print(f'{time.time()} : [S]Echoing: {message!r}')
	writer.write(data)
	await writer.drain()

	print(f'{time.time()} : [S]Close the connection')
	writer.close()
	await writer.wait_closed()

async def test_tcp_server():
	print(f'{time.time()} : Testing TCP server')

	message = 'hello world apple banana'
	fs = [asyncio.ensure_future(start_tcp_test_client(word)) for word in message.split()]
	await asyncio.wait(fs, timeout = 4)
	print(f'{time.time()} : TCP server test complete')
	print(f'{time.time()} : --------')

async def start_tcp_test_client(message: str):
	reader: asyncio.StreamReader
	writer: asyncio.StreamWriter

	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	tcp_server_ip = readRines[0].strip().split(':')
	reader, writer = await asyncio.open_connection(tcp_server_ip[0], tcp_server_ip[1])

	print(f'{time.time()} : [C]Connected')
	writer.write(message.encode())
	await writer.drain()
	print(f'{time.time()} : [C]Send: {message!r}')

	data = await reader.read(100)
	print(f'{time.time()} : [C]Received: {data.decode()!r}')

	print(f'{time.time()} : [C]Closing...')
	writer.close()
	await writer.wait_closed()
