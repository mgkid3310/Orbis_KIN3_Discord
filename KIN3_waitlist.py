import KIN3_Esi
import KIN3_database

class server_list:
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

		def add_dps(self, eve_char_id):
			character = KIN3_Esi.get_character_object(eve_char_id)
			self.waitlist_dps.append(character)
			self.waitcount_dps += 1

		def add_snp(self, eve_char_id):
			character = KIN3_Esi.get_character_object(eve_char_id)
			self.waitlist_snp.append(character)
			self.waitcount_snp += 1

		def add_logi(self, eve_char_id):
			character = KIN3_Esi.get_character_object(eve_char_id)
			self.waitlist_logi.append(character)
			self.waitcount_logi += 1

		def remove_user(self, member):
			self.waitlist_dps = [x for x in self.waitlist_dps if not x.discord_id == member.id]
			self.waitcount_dps = len(self.waitlist_dps)
			self.waitlist_snp = [x for x in self.waitlist_snp if not x.discord_id == member.id]
			self.waitcount_snp = len(self.waitlist_snp)
			self.waitlist_logi = [x for x in self.waitlist_logi if not x.discord_id == member.id]
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

		def remove_request(self, member):
			self.request_list = [x for x in self.request_list if x[0].discord_id != member.id]

		def reset_request(self):
			self.request_list = []

		def check_requests(self):
			for index in range(len(self.request_list)):
				request = self.request_list[index]
				return_users = self.request_users(request[1], request[2], request[3])

				if return_users is not None:
					del self.request_list[index]
					return request[0], return_users[0], return_users[1], return_users[2]

		def request_announcement(self, announce_list):
			notice_text = f'@{announce_list[0].discord_id}의 모집이 완료되었습니다:'
			for user in announce_list[1]:
				notice_text += f' @{user.discord_id}(DPS),'
			for user in announce_list[2]:
				notice_text += f' @{user.discord_id}(SNP),'
			for user in announce_list[3]:
				notice_text += f' @{user.discord_id}(LOGI),'
			return notice_text[:-1]

		def update_billboard(self):
			width_dps = 5 + len(str(self.waitcount_dps))
			width_snp = 5 + len(str(self.waitcount_snp))
			if self.waitcount_dps > 0:
				width_dps_list = [len(x.discord_member.display_name) for x in self.waitlist_dps]
				width_dps_list.append(width_dps)
				width_dps = max(width_dps_list)
			if self.waitcount_snp > 0:
				width_snp_list = [len(x.discord_member.display_name) for x in self.waitlist_snp]
				width_snp_list.append(width_snp)
				width_snp = max(width_snp_list)
			width_dps += 4
			width_snp += 4

			text = '```markdown'
			text += '\n# KIN3 Waitlist'
			text += f'\nDPS({self.waitcount_dps})' + ' ' * (width_dps - len(str(self.waitcount_dps)) - 5)
			text += f'SNP({self.waitcount_snp})' + ' ' * (width_snp - len(str(self.waitcount_snp)) - 5)
			text += f'LOGI({self.waitcount_logi})'
			for index in range(max((self.waitcount_dps, self.waitcount_snp, self.waitcount_logi))):
				dps_name, snp_name, logi_name = '', '', ''
				dps_white, snp_space = ' ' * width_dps, ' ' * width_snp
				if index < self.waitcount_dps:
					dps_name = self.waitlist_dps[index].discord_member.display_name
					dps_white = ' ' * (width_dps - len(dps_name))
				if index < self.waitcount_snp:
					snp_name = self.waitlist_snp[index].discord_member.display_name
					snp_space = ' ' * (width_snp - len(snp_name))
				if index < self.waitcount_logi:
					logi_name = self.waitlist_logi[index].discord_member.display_name
				text += '\n' + dps_name + dps_white + snp_name + snp_space + logi_name
			text += '\n\n----------------'
			for request in self.request_list:
				text += f'\n{request[0].discord_member.display_name}이(가)'
				if request[1] > 0:
					text += f' {request[1]} DPS,'
				if request[2] > 0:
					text += f' {request[2]} SNP,'
				if request[3] > 0:
					text += f' {request[3]} LOGI,'
				text = text[:-1]
				text += ' 모집중'
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
