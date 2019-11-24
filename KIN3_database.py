import KIN3_Esi

def add_token(esi_objects, code, member_id, file_path = './esi_tokens.txt'):
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
		file.write(f'{eve_char_name}:{eve_char_id}:{refresh_token}:{member_id}\n')

	return ''

def filter_vailid_tokens(esi_objects, file_path = './esi_tokens.txt'):
	with open(file_path, 'r') as file:
		lines = file.readlines()

	with open(file_path, 'w') as file:
		for line in lines:
			if KIN3_Esi.eve_character(esi_objects, line.strip().split(":")).is_valid():
				file.write(line)

	return None

def auth_count(member, file_path = './esi_tokens.txt'):
	count = 0

	with open(file_path, 'r') as file:
		for line in file.readlines():
			if member.id == int(line.strip().split(":")[3]):
				count += 1

	return count

def get_eve_characters(discord_id, file_path = './esi_tokens.txt'):
	return_list = []

	with open(file_path, 'r') as file:
		for line in file.readlines():
			if discord_id == int(line.strip().split(":")[3]):
				return_list.append(line.strip().split(":"))

	return return_list

def xup_selection_info(member, file_path = './esi_tokens.txt'):
	text = '```markdown\n'
	eve_characters = get_eve_characters(member.id)

	for index in range(len(eve_characters)):
		text += f'x{index} : {eve_characters[index][0]}\n'

	text += '```'

	return text

def get_character_object(esi_objects, member, char_index = 0):
	if char_index is None:
		char_index = 0

	characters_list = get_eve_characters(member.id)
	if len(characters_list) > char_index:
		return KIN3_Esi.eve_character(esi_objects, characters_list[char_index], member)

	return None
