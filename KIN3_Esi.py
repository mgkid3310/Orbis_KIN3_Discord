import asyncio
import discord

from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity

def add_token(app, security, client, code, discord_id = -1, file_path = './esi_tokens.txt'):
	try:
		token = security.auth(code)
	except Exception as error:
		return str(error)
	refresh_token = token['refresh_token']

	api_info = security.verify()
	eve_char_id = api_info['sub'].split(':')[-1]
	operation = app.op['get_characters_character_id'](character_id = eve_char_id)
	name = client.request(operation).data['name']

	with open(file_path, 'r') as file:
		lines = file.readlines()

	with open(file_path, 'w') as file:
		for line in lines:
			read_name = line.strip().split(":")[0]
			if read_name != name:
				file.write(line)
		file.write(f'{name}:{eve_char_id}:{refresh_token}:{discord_id}\n')

	return ''

def get_refresh_token(eve_char_id):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	for line in lines:
		if eve_char_id == int(line.strip().split(":")[1]):
			refresh_token = line.strip().split(":")[2]
			return refresh_token

	return None

def is_token_valid(app, security, client, refresh_token):
	security.update_token({
		'access_token': '',
		'expires_in': -1,
		'refresh_token': refresh_token
	})
	try:
		token = security.refresh()
		return True
	except:
		return False

def is_char_valid(app, security, client, eve_char_id):
	refresh_token = get_refresh_token(eve_char_id)
	if refresh_token is None:
		return False

	return is_token_valid(app, security, client, refresh_token)

def filter_vailid_tokens(app, security, client, file_path = './esi_tokens.txt'):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	with open(file_path, 'w') as file:
		for line in lines:
			refresh_token = line.strip().split(":")[2]
			if is_token_valid(app, security, client, refresh_token):
				file.write(line)

	return None

def get_eve_characters(discord_id):
	return_list = []

	with open(file_path, 'r') as file:
		lines = file.readlines()

	for line in lines:
		if discord_id == int(line.strip().split(":")[3]):
			return_list.append((line.strip().split(":")[0], int(line.strip().split(":")[1])))

	return return_list

def is_online(app, security, client, eve_char_id):
	refresh_token = get_refresh_token(eve_char_id)
	if refresh_token is None:
		return None

	security.update_token({
		'access_token': '',
		'expires_in': -1,
		'refresh_token': refresh_token
	})
	token = security.refresh()
	operation = app.op['get_characters_character_id_online'](character_id = eve_char_id)
	is_online = client.request(operation).data['online']
	return is_online

def get_fleet(app, security, client, eve_char_id):
	refresh_token = get_refresh_token(eve_char_id)
	if refresh_token is None:
		return None

	security.update_token({
		'access_token': '',
		'expires_in': -1,
		'refresh_token': refresh_token
	})
	token = security.refresh()
	operation = app.op['get_characters_character_id_fleet'](character_id = eve_char_id)
	fleet_id = client.request(operation).data
	return fleet_id
