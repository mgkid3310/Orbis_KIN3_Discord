class eve_character:
	def __init__(self, input, member = None):
		name, char_id, refresh_token, discord_id = input

		self.name = name
		self.char_id = int(char_id)
		self.refresh_token = refresh_token
		self.discord_id = int(discord_id)
		self.discord_member = member

	def __str__(self):
		return f'character object, id: {self.char_id}'

	def set_member(member):
		self.discord_member = member

	def is_valid(self):
		global esi_latest
		app, security, client = esi_latest

		if not is_server_online(esi_latest):
			return True

		try:
			security.update_token({
				'access_token': '',
				'expires_in': -1,
				'refresh_token': self.refresh_token
			})
			token = security.refresh()
			return True
		except:
			return False

	def is_online(self):
		global esi_latest
		app, security, client = esi_latest

		if not is_server_online(esi_latest):
			return False

		try:
			security.update_token({
				'access_token': '',
				'expires_in': -1,
				'refresh_token': self.refresh_token
			})
			token = security.refresh()
		except:
			return False

		try:
			operation = app.op['get_characters_character_id_online'](character_id = self.char_id)
			is_online = client.request(operation).data['online']
			return is_online
		except:
			return False

	def get_location(self):
		global esi_latest
		app, security, client = esi_latest

		if not self.is_online():
			return {'error' : 'Character is not online'}

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()

		try:
			operation = app.op['get_characters_character_id_location'](character_id = self.char_id)
			location_data = client.request(operation).data
			return location_data
		except:
			return {'error' : 'Esi operation failed'}

	def get_fitting(self):
		global esi_latest
		app, security, client = esi_latest

		if not self.is_online():
			return {'error' : 'Character is not online'}

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()

		try:
			operation = app.op['get_characters_character_id_fittings'](character_id = self.char_id)
			location = client.request(operation).data
			return location
		except:
			return {'error' : 'Esi operation failed'}

	def get_fleet(self):
		global esi_v2
		app, security, client = esi_v2

		if not self.is_online():
			return {'error' : 'Character is not online'}

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()

		try:
			operation = app.op['get_characters_character_id_fleet'](character_id = self.char_id)
			fleet_data = client.request(operation).data
			return fleet_data
		except:
			return {'error' : 'Esi operation failed'}

	def fleet_invite(self, characters):
		global esi_latest
		app, security, client = esi_latest

		if not self.is_online():
			return {'error' : 'Character is not online'}

		fleet_data = self.get_fleet()
		if 'fleet_id' not in fleet_data:
			return {'error' : 'Character is not in fleet'}
		else:
			fleet_id = fleet_data['fleet_id']

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()

		for character in characters:
			if character.is_online():
				try:
					invitation = {
						"character_id": character.char_id,
						"role": "squad_member"
					}
					operation = app.op['post_fleets_fleet_id_members'](fleet_id = fleet_id, invitation = invitation)
					invite_return = client.request(operation)
				except:
					pass

def check_server_status(esi):
	app, security, client = esi

	try:
		operation = app.op['get_status']()
		status_data = client.request(operation).data
		return status_data
	except:
		return {'error' : 'Esi operation failed'}

def is_server_online(esi, force_check = False):
	global is_tranquility_online

	if (not is_tranquility_online) and (not force_check):
		return False

	status_data = check_server_status(esi)
	online_status = 'players' in status_data

	is_tranquility_online = online_status
	return online_status
