import time
import asyncio

import KIN3_Esi
import KIN3_database
import KIN3_waitlist

async def start_tcp_server(bot, tcp_server = None):
	print(f'{round(time.time(), 4)} : Starting TCP server')

	if tcp_server is not None:
		print(f'{round(time.time(), 4)} : Server already existing')
		print(f'{round(time.time(), 4)} : --------')
		return tcp_server

	print(f'{round(time.time(), 4)} : No server existing')
	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	tcp_server_ip = readRines[0].strip().split(':')
	tcp_server = await asyncio.start_server(handle_tcp_inbound, tcp_server_ip[0], tcp_server_ip[1])
	tcp_addr = tcp_server.sockets[0].getsockname()
	print(f'{round(time.time(), 4)} : Server started on {tcp_addr}')
	print(f'{round(time.time(), 4)} : Request handling started')
	print(f'{round(time.time(), 4)} : --------')

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

	print(f'{round(time.time(), 4)} : [S]Received {message!r} from {addr!r}')
	print(f'{round(time.time(), 4)} : [S]Echoing: {message!r}')
	writer.write(data)
	await writer.drain()

	print(f'{round(time.time(), 4)} : [S]Close the connection')
	writer.close()
	await writer.wait_closed()

async def test_tcp_server():
	print(f'{round(time.time(), 4)} : Testing TCP server')

	message = 'hello world apple banana'
	fs = [asyncio.ensure_future(start_tcp_test_client(word)) for word in message.split()]
	await asyncio.wait(fs, timeout = 4)
	print(f'{round(time.time(), 4)} : TCP server test complete')
	print(f'{round(time.time(), 4)} : --------')

async def start_tcp_test_client(message: str):
	reader: asyncio.StreamReader
	writer: asyncio.StreamWriter

	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	tcp_server_ip = readRines[0].strip().split(':')
	reader, writer = await asyncio.open_connection(tcp_server_ip[0], tcp_server_ip[1])

	print(f'{round(time.time(), 4)} : [C]Connected')
	writer.write(message.encode())
	await writer.drain()
	print(f'{round(time.time(), 4)} : [C]Send: {message!r}')

	data = await reader.read(100)
	print(f'{round(time.time(), 4)} : [C]Received: {data.decode()!r}')

	print(f'{round(time.time(), 4)} : [C]Closing...')
	writer.close()
	await writer.wait_closed()
