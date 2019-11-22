class eve_character:
	def __init__(self, esi_objects, input):
		name, eve_char_id, refresh_token, discord_id = input

		self.esi_objects = esi_objects
		self.name = name
		self.eve_char_id = eve_char_id
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

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_online'](character_id = self.eve_char_id)
		is_online = client.request(operation).data['online']

		return is_online

	def get_fleet(self):
		app, security, client = self.esi_objects

		security.update_token({
			'access_token': '',
			'expires_in': -1,
			'refresh_token': self.refresh_token
		})
		token = security.refresh()
		operation = app.op['get_characters_character_id_fleet'](character_id = self.eve_char_id)
		fleet_id = client.request(operation).data

		return fleet_id
