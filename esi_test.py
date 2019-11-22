from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
import KIN3_Esi

app = EsiApp().get_latest_swagger

security = EsiSecurity(
	headers = {'User-Agent':'something'},
	redirect_uri = 'http://localhost:65432/callback/',
	client_id = 'f5681b8bf37b4454911f42c53af1f22b',
	secret_key = 'CTJ5dPxofM2Q0uVuDB4Gy43hzsdloK5C3Eriw7wn'
)

client = EsiClient(
	headers = {'User-Agent':'something'},
	retry_requests = True,
	header = {'User-Agent': 'Something CCP can use to contact you and that define your app'},
	security = security
)

esi_scopes = [
	'esi-location.read_location.v1',
	'esi-fleets.read_fleet.v1',
	'esi-fleets.write_fleet.v1',
	'esi-fittings.read_fittings.v1',
	'esi-characters.read_chat_channels.v1',
	'esi-location.read_online.v1'
]
print(security.get_auth_uri(state = 'KIN3_FC_Auth', scopes = esi_scopes))

#%%
code = input()
token = security.auth(code)
token

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
