class eve_character:
	def __init__(self, esi_objects, input, member = None):
		name, char_id, refresh_token, discord_id = input

		self.esi_objects = esi_objects
		self.name = name
		self.char_id = char_id
		self.refresh_token = refresh_token
		self.discord_id = discord_id
		self.discord_member = member

	def __str__(self):
		return f'character object, id: {self.char_id}'

	def set_member(member):
		self.discord_member = member

	def is_valid(self):
		app, security, client = self.esi_objects

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
		app, security, client = self.esi_objects

		if not self.is_valid():
			return None

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_online'](character_id = self.char_id)
		is_online = client.request(operation).data['online']

		return is_online

	def get_location(self):
		app, security, client = self.esi_objects

		if not self.is_valid():
			return None

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_location'](character_id = self.char_id)
		location = client.request(operation).data

		return location

	def get_fitting(self):
		app, security, client = self.esi_objects

		if not self.is_valid():
			return None

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_fittings'](character_id = self.char_id)
		location = client.request(operation).data

		return location

	def get_fleet(self):
		app, security, client = self.esi_objects

		if not self.is_valid():
			return None

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_fleet'](character_id = self.char_id)
		fleet_data = client.request(operation).data

		return fleet_data

	def fleet_invite(self, characters):
		app, security, client = self.esi_objects

		if not self.is_valid():
			return None

		fleet_data = self.get_fleet()
		if 'fleet_id' not in fleet_data:
			return None
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
