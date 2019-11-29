from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
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
	'refresh_token': '+iZdEcao/UG+6Apx2R5xYA=='
})
token = security.refresh()

#%%
operation = app.op['get_characters_character_id_location'](character_id = '97199391')
client.request(operation).data

#%%
operation = app.op['get_characters_character_id_fittings'](character_id = '97199391')
client.request(operation).data

#%%
operation = app.op['get_characters_character_id_fleet'](character_id = '97199391')
'fleet_id' in client.request(operation).data
