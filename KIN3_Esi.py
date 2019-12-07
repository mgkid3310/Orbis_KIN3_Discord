class eve_character:
	def __init__(self, esi_latest, input, esi_v2 = None, member = None):
		name, char_id, refresh_token, discord_id = input

		if esi_v2 is None:
			esi_v2 = esi_latest

		self.esi_latest = esi_latest
		self.esi_v2 = esi_v2
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
		app, security, client = self.esi_latest

		if not is_server_online(self.esi_latest):
			return True

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})

		try:
			token = security.refresh()
			return True
		except:
			return False

	def is_online(self):
		app, security, client = self.esi_latest

		if not self.is_valid():
			return False

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_online'](character_id = self.char_id)

		try:
			is_online = client.request(operation).data['online']
			return is_online
		except:
			return False

	def get_location(self):
		app, security, client = self.esi_latest

		if not self.is_valid():
			return {'error' : 'Character is not valid'}

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_location'](character_id = self.char_id)

		try:
			location_data = client.request(operation).data
			return location_data
		except:
			return {'error' : 'Esi operation failed'}

	def get_fitting(self):
		app, security, client = self.esi_latest

		if not self.is_valid():
			return {'error' : 'Character is not valid'}

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_fittings'](character_id = self.char_id)

		try:
			location = client.request(operation).data
			return location
		except:
			return {'error' : 'Esi operation failed'}

	def get_fleet(self):
		app, security, client = self.esi_v2

		if not self.is_valid():
			return {'error' : 'Character is not valid'}

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_fleet'](character_id = self.char_id)

		try:
			fleet_data = client.request(operation).data
			return fleet_data
		except:
			return {'error' : 'Esi operation failed'}

	def fleet_invite(self, characters):
		app, security, client = self.esi_latest

		if not self.is_valid():
			return {'error' : 'Character is not valid'}

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
				invitation = {
					"character_id": character.char_id,
					"role": "squad_member"
				}
				operation = app.op['post_fleets_fleet_id_members'](fleet_id = fleet_id, invitation = invitation)
				invite_return = client.request(operation)

def check_server_status(esi):
	app, security, client = esi

	operation = app.op['get_status']()

	try:
		status_data = client.request(operation).data
		return status_data
	except:
		return {'error' : 'Esi operation failed'}

def is_server_online(esi):
	status_data = check_server_status(esi)
	online_status = 'players' in status_data

	return online_status
