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
	operation = app.op['get_characters_character_id'](character_id = api_info['sub'].split(':')[-1])
	name = client.request(operation).data['name']

	with open(file_path, 'r') as file:
		lines = file.readlines()

	with open(file_path, 'w') as file:
		for line in lines:
			read_name = line.strip().split(":")[0]
			if read_name != name:
				file.write(line)
		file.write(f'{name}:{refresh_token}:{discord_id}\n')

	return ''

def has_auth(discord_id, name = '', file_path = './esi_tokens.txt'):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	for line in lines:
		read_name = line.strip().split(":")[0]
		read_id = line.strip().split(":")[2]

		if discord_id == int(read_id) and (name == '' or name == read_name):
			return True

	return False
