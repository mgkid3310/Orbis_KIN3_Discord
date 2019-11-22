import KIN3_Esi

def add_token(esi_objects, code, discord_member, file_path = './esi_tokens.txt'):
	app, security, client = esi_objects

	try:
		token = security.auth(code)
	except Exception as error:
		return str(error)
	refresh_token = token['refresh_token']

	api_info = security.verify()
	eve_char_id = api_info['sub'].split(':')[-1]
	operation = app.op['get_characters_character_id'](character_id = eve_char_id)
	eve_char_name = client.request(operation).data['name']

	with open(file_path, 'r') as file:
		lines = file.readlines()

	with open(file_path, 'w') as file:
		for line in lines:
			read_name = line.strip().split(":")[0]
			if read_name != eve_char_name:
				file.write(line)
		file.write(f'{eve_char_name}:{eve_char_id}:{refresh_token}:{discord_member.id}\n')

	return ''

def has_auth(discord_id):
	with open(file_path, 'r') as file:
		for line in file.readlines():
			if discord_id == int(line.strip().split(":")[3]):
				return True

	return False

def filter_vailid_tokens(file_path = './esi_tokens.txt'):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	with open(file_path, 'w') as file:
		for line in lines:
			if KIN3_Esi.eve_character(line.strip().split(":")).is_valid():
				file.write(line)

	return None

def get_eve_characters(discord_id):
	return_list = []

	with open(file_path, 'r') as file:
		lines = file.readlines()

	for line in lines:
		if discord_id == int(line.strip().split(":")[3]):
			return_list.append(KIN3_Esi.eve_character(esi_objects, line.strip().split(":")))

	return return_list
