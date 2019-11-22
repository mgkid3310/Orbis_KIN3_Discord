class eve_character:
	def __init__(self, esi_objects, input):
		name, char_id, refresh_token, discord_id = input

		self.esi_objects = esi_objects
		self.name = name
		self.char_id = char_id
		self.refresh_token = refresh_token
		self.discord_id = discord_id

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
