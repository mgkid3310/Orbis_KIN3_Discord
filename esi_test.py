from esipy import EsiApp
from esipy import EsiSecurity
from esipy import EsiClient
import KIN3_common
import KIN3_Esi

auth_key_file = open('./esi_auth_key.txt', 'r')
auth_key_lines = auth_key_file.readlines()
redirect_uri = auth_key_lines[0].strip()
client_id = auth_key_lines[1].strip()
secret_key = auth_key_lines[2].strip()

app_latest = EsiApp().get_latest_swagger
print(f'{KIN3_common.timestamp()} : EsiApp latest loaded')

# app_v1 = EsiApp().get_v1_swagger
# print(f'{KIN3_common.timestamp()} : EsiApp v1 loaded')

app_v2 = EsiApp().get_v2_swagger
print(f'{KIN3_common.timestamp()} : EsiApp v2 loaded')

security = EsiSecurity(
	redirect_uri = redirect_uri,
	client_id = client_id,
	secret_key = secret_key,
	headers = {'User-Agent' : 'something'}
)
print(f'{KIN3_common.timestamp()} : EsiSecurity loaded')

client = EsiClient(
	security = security,
	retry_requests = True,
	headers = {'User-Agent' : 'something'},
	header = {'User-Agent' : 'something'}
)
print(f'{KIN3_common.timestamp()} : EsiClient loaded')

esi_latest = (app_latest, security, client)
# esi_v1 = (app_v1, security, client)
esi_v2 = (app_v2, security, client)
print(f'{KIN3_common.timestamp()} : --------')

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
operation = app_latest.op['get_status']()
client.request(operation).data

#%%
server_status = KIN3_Esi.check_server_status(esi_objects)
'players' in server_status

#%%
operation = app_latest.op['get_characters_character_id_fittings'](character_id = '97199391')
client.request(operation).data

#%%
operation = app_v2.op['get_characters_character_id_fleet'](character_id = '97199391')
fleet_id = client.request(operation).data['fleet_id']
fleet_id

#%%
invitation = {
	'character_id': 2112354154,
	'role': 'squad_member'
}
operation = app_latest.op['post_fleets_fleet_id_members'](fleet_id = fleet_id, invitation = invitation)
client.request(operation)
