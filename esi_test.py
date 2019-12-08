from esipy import EsiApp
from esipy import EsiSecurity
from esipy import EsiClient
import KIN3_Esi

app = EsiApp().get_latest_swagger
print('EsiApp loaded')

auth_key_file = open('./esi_auth_key.txt', 'r')
auth_key_lines = auth_key_file.readlines()
redirect_uri = auth_key_lines[0].strip()
client_id = auth_key_lines[1].strip()
secret_key = auth_key_lines[2].strip()

security = EsiSecurity(
	headers = {'User-Agent':'something'},
	redirect_uri = redirect_uri,
	client_id = client_id,
	secret_key = secret_key
)
print('EsiSecurity loaded')

client = EsiClient(
	headers = {'User-Agent':'something'},
	retry_requests = True,
	header = {'User-Agent': 'Something CCP can use to contact you and that define your app'},
	security = security
)
print('EsiClient loaded')

esi_objects = (app, security, client)
print('--------')

#%%
if token['expires_in'] < 1200:
	security.update_token({
		'access_token': '',
		'expires_in': -1,
		'refresh_token': token['refresh_token']
	})
	token = security.refresh()

token

#%%
security.update_token({
	'access_token': '',
	'expires_in': -1,
	'refresh_token': 'Pc4C1iK6p0evpU3dBSkSwg=='
})
token = security.refresh()

#%%
operation = app.op['get_status']()
client.request(operation).data

#%%
server_status = KIN3_Esi.check_server_status(esi_objects)
'players' in server_status

#%%
operation = app.op['get_characters_character_id_fittings'](character_id = '97199391')
client.request(operation).data

#%%
operation = app.op['get_characters_character_id_fleet'](character_id = '97199391')
'fleet_id' in client.request(operation).data

#%%
import KIN3_common

input = '''c command return 5'''

prefix = input[0].lower()
char_index = None
if len(input) > 1:
	if input[1] == ' ':
		command_cap = input[2:]
	else:
		command_cap = input[1:]

	if command_cap[0].isdigit():
		for index in range(1, len(command_cap)):
			if not command_cap[index].isdigit():
				char_index = int(command_cap[:index])
				command_cap = command_cap[len(str(char_index)):]
				break

	if command_cap[0] == ' ':
		command_cap[1:]
else:
	command_cap = ''

command = command_cap.lower()

lines = command_cap.split('\n')
if len(lines) == 1:
	lines = [' '.join(command_cap.split(' ')[1:])]

	if lines[0][:3] == '```':
		lines[0] = lines[0][3:]
	elif lines[0][:1] == '`':
		lines[0] = lines[0][1:]

	if lines[0][-3:] == '```':
		lines[0] = lines[0][:-3]
	elif lines[0][-1:] == '`':
		lines[0] = lines[0][:-1]
else:
	lines = lines[1:]

	if lines[0][:3] == '```':
		lines[0] = lines[0][3:]
	elif lines[0][:1] == '`':
		lines[0] = lines[0][1:]

	if lines[-1][-3:] == '```':
		lines[-1] = lines[-1][:-3]
	elif lines[-1][-1:] == '`':
		lines[-1] = lines[-1][:-1]

hotcode = 'def hotfunc():'
for index in range(len(lines)):
	hotcode += '\n\t' + lines[index]
hotcode += '\nKIN3_common.hotcode_return = hotfunc()'

KIN3_common.hotcode_return = None
exec(hotcode)
print(KIN3_common.hotcode_return)
