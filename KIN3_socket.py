import socket

import KIN3_common
import KIN3_Esi
import KIN3_database
import KIN3_waitlist

def start_tcp_server(loop, tcp_server_online = False):
	print(f'{KIN3_common.timestamp()} : Starting TCP server')

	if tcp_server_online:
		print(f'{KIN3_common.timestamp()} : Server already existing')
		print(f'{KIN3_common.timestamp()} : --------')
		return tcp_server_online

	print(f'{KIN3_common.timestamp()} : No server existing')
	with open('./tcp_setup.txt', 'r') as file:
		readRines = file.readlines()

	server_ip = readRines[0].strip().split(':')
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((server_ip[0], int(server_ip[1])))
	server_socket.listen()

	print(f'{KIN3_common.timestamp()} : Server started on {server_ip[0]}:{server_ip[1]}')
	print(f'{KIN3_common.timestamp()} : Request handling started')
	print(f'{KIN3_common.timestamp()} : --------')

	loop.create_task(tcp_server_loop(loop, server_socket))

	tcp_server_online = True
	return tcp_server_online

def tcp_server_loop(loop, server_socket):
	while True:
		client_socket, client_addr = server_socket.accept()
		loop.create_task(tcp_handle_inbound(client_socket, client_addr))

def tcp_handle_inbound(client_socket, client_addr):
	while True:
		message = client_socket.recv(1024).decode('ascii')
		print(f'{client_addr} >> {message}')
		client_socket.send(f'{KIN3_common.timestamp()} : message inbound check'.encode('ascii'))

	client_socket.close()
