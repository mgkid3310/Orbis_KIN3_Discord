import KIN3_Esi

def add_token(esi, code, member_id, file_path = './esi_tokens.txt'):
	app, security, client = esi

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

def remove_auth(eve_char_object, file_path = './esi_tokens.txt'):
	with open(file_path, 'r') as file:
		readRines = file.readlines()

	writeLines = []

	for line in readRines:
		if int(line.strip().split(":")[1]) != eve_char_object.char_id:
			writeLines.append(line)

	with open(file_path, 'w') as file:
		for line in writeLines:
			file.write(line)

	return None

def filter_vailid_tokens(esi, file_path = './esi_tokens.txt'):
	with open(file_path, 'r') as file:
		readRines = file.readlines()

	writeLines = []

	for line in readRines:
		if KIN3_Esi.eve_character(esi, line.strip().split(":")).is_valid():
			writeLines.append(line)

	with open(file_path, 'w') as file:
		for line in writeLines:
			file.write(line)

	return None

def get_auth_count(member, file_path = './esi_tokens.txt'):
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

def get_character_object(esi_latest, esi_v2, member, char_index = 0):
	if char_index is None:
		char_index = 0

	characters_list = get_eve_characters(member.id)
	if len(characters_list) > char_index:
		return KIN3_Esi.eve_character(esi_latest, characters_list[char_index], esi_v2, member)

	return None

async def process_char_index(esi_latest, esi_v2, member, char_index, channel, display_name, auth_embed):
	eve_char_object = None

	auth_count = get_auth_count(member)
	if not auth_count > 0:
		await channel.send(f'{display_name}, 계정이 등록되지 않은 유저입니다, 계정 인증이 필요합니다')
		await channel.send(embed = auth_embed)
		return None
	else:
		if auth_count > 1 and char_index is None:
			await channel.send(f'{display_name}, 등록된 계정이 두개 이상입니다. 계정을 특정해주세요')
			await channel.send(xup_selection_info(member))
			return None

		eve_char_object = get_character_object(esi_latest, esi_v2, member, char_index)
		if eve_char_object is None:
			await channel.send(f'{display_name}, 에러가 발생했습니다. 관리자에게 문의해주세요\n에러코드: KIN3_database 101, character object init fail')
			return None

	return eve_char_object
