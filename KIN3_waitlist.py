class  server_list:
	class waitlist:
		def __init__(self, server_id):
			self.xup_channel = None
			self.billboard_message = None
			self.billboard_text = 'starting_billboard'
			self.waitlist_dps = []
			self.waitcount_dps = 0
			self.waitlist_snp = []
			self.waitcount_snp = 0
			self.waitlist_logi = []
			self.waitcount_logi = 0
			self.request_list = []

		def add_dps(self, user):
			self.waitlist_dps.append(user)
			self.waitcount_dps += 1

		def add_snp(self, user):
			self.waitlist_snp.append(user)
			self.waitcount_snp += 1

		def add_logi(self, user):
			self.waitlist_logi.append(user)
			self.waitcount_logi += 1

		def remove_user(self, user):
			self.waitlist_dps = [i for i in self.waitlist_dps if not i == user]
			self.waitcount_dps = len(self.waitlist_dps)
			self.waitlist_snp = [i for i in self.waitlist_snp if not i == user]
			self.waitcount_snp = len(self.waitlist_snp)
			self.waitlist_logi = [i for i in self.waitlist_logi if not i == user]
			self.waitcount_logi = len(self.waitlist_logi)

		def reset_waitlist(self):
			self.waitlist_dps = []
			self.waitcount_dps = 0
			self.waitlist_snp = []
			self.waitcount_snp = 0
			self.waitlist_logi = []
			self.waitcount_logi = 0
			self.request_list = []

		def is_ready(self, dps = 0, snp = 0, logi = 0):
			return self.waitcount_dps >= dps and self.waitcount_snp >= snp and self.waitcount_logi >= logi

		def request_users(self, dps = 0, snp = 0, logi = 0):
			if self.waitcount_dps >= dps and self.waitcount_snp >= snp and self.waitcount_logi >= logi:
				return_list = self.waitlist_dps[:dps], self.waitlist_snp[:snp], self.waitlist_logi[:logi]

				self.waitlist_dps = self.waitlist_dps[dps:]
				self.waitcount_dps -= dps
				self.waitlist_snp = self.waitlist_snp[snp:]
				self.waitcount_snp -= snp
				self.waitlist_logi = self.waitlist_logi[logi:]
				self.waitcount_logi -= logi

				return return_list
			else:
				return None

		def add_request(self, fc, dps = 0, snp = 0, logi = 0):
			self.request_list.append((fc, dps, snp, logi))

		def check_requests(self):
			for index in range(len(self.request_list)):
				request = self.request_list[index]
				return_users = self.request_users(request[1], request[2], request[3])

				if return_users is not None:
					del self.request_list[index]
					return request[0], return_users[0], return_users[1], return_users[2]

		def update_billboard(self):
			text = '```markdown'
			text += '\n# KIN3 Waitlist'
			text += f'\nDPS({self.waitcount_dps})' + ' ' * (15 - len(str(self.waitcount_dps)))
			text += f'SNP({self.waitcount_snp})' + ' ' * (15 - len(str(self.waitcount_snp)))
			text += f'LOGI({self.waitcount_logi})'
			for index in range(max((self.waitcount_dps, self.waitcount_snp, self.waitcount_logi))):
				dps_name, snp_name, logi_name = '', '', ''
				dps_white, snp_space = ' ' * 20, ' ' * 20
				if index < self.waitcount_dps:
					dps_name = self.waitlist_dps[index].name
					dps_white = ' ' * (20 - len(dps_name))
				if index < self.waitcount_snp:
					snp_name = self.waitlist_snp[index].name
					snp_space = ' ' * (20 - len(snp_name))
				if index < self.waitcount_logi:
					logi_name = self.waitlist_logi[index].name
				text += '\n' + dps_name + dps_white + snp_name + snp_space + logi_name
			text += '```'
			self.billboard_text = text

	def __init__(self):
		self.servers = []
		self.waitlists = []

	def add_waitlist(self, server_id):
		self.servers.append(server_id)
		self.waitlists.append(self.waitlist(server_id))

	def get_waitlist(self, server_id):
		if server_id not in self.servers:
			self.add_waitlist(server_id)

		index = self.servers.index(server_id)
		return self.waitlists[index]
