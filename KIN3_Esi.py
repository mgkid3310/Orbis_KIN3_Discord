from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity

def add_token(app, security, client, code, user_id = -1, file = './esi_tokens.txt'):
	try:
		token = security.auth(code)
	except Exception as error:
		return str(error)
	refresh_token = token['refresh_token']

	api_info = security.verify()
	operation = app.op['get_characters_character_id'](character_id = api_info['sub'].split(':')[-1])
	name = client.request(operation).data['name']

	with open(file, 'a') as file:
		file.write(f'{name}:{refresh_token}:{user_id}\n')

	return ''
