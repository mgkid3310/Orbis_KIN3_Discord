import time
import asyncio
import discord
import logging

import esipy
from esipy import EsiApp
from esipy import EsiSecurity
from esipy import EsiClient

import KIN3_common
import KIN3_Esi
import KIN3_database
import KIN3_waitlist
import KIN3_socket

# load bot
bot = discord.Client()
print(f'{KIN3_common.timestamp()} : Bot client loaded')
print(f'{KIN3_common.timestamp()} : --------')

# set logger
esipy.client.LOGGER.setLevel(logging.CRITICAL)

'''logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord_kin3.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(f'{KIN3_common.timestamp()} : %(levelname)s : %(name)s : %(message)s'))
logger.addHandler(handler)'''

# define event & functions
@bot.event
async def on_ready():
	global periodic_5s_running
	global periodic_60s_running
	global tcp_server_online

	await bot.change_presence(activity = discord.Game(name = 'KIN3', type = 1))
	print(f'{KIN3_common.timestamp()} : Bot logged in as')
	print(f'{KIN3_common.timestamp()} : name : {bot.user.name}')
	print(f'{KIN3_common.timestamp()} : id : {bot.user.id}')

	# start periodic bot loop
	if not periodic_5s_running:
		periodic_5s_running = True
		bot.loop.create_task(event_periodic_5s())
		print(f'{KIN3_common.timestamp()} : 5s periodic bot event added')

	if not periodic_60s_running:
		periodic_60s_running = True
		bot.loop.create_task(event_periodic_60s())
		print(f'{KIN3_common.timestamp()} : 60s periodic bot event added')

	print(f'{KIN3_common.timestamp()} : --------')

	# start tcp server
	tcp_server_online = await KIN3_socket.start_tcp_server(bot.loop, tcp_server_online)

@bot.event
async def on_message(message):
	global server_list
	global admin_id
	global auth_embed
	global auth_url

	global keywords_auth
	global keywords_auth_cancel
	global keywords_dps
	global keywords_snp
	global keywords_logi
	global keywords_cancel

	if message.content == '':
		return None

	if message.author.bot:
		if message.content == 'init_billboard':
			waitlist = server_list.get_waitlist(message.guild.id)
			waitlist.billboard_message = message
			await message.edit(content = waitlist.billboard_text)

		return None

	# message breakdown
	prefix = message.content[0].lower()
	char_index = None
	if len(message.content) > 1:
		if message.content[1] == ' ':
			command_cap = message.content[2:]
		else:
			command_cap = message.content[1:]

		if command_cap[0].isdigit():
			for index in range(1, len(command_cap)):
				if not command_cap[index].isdigit():
					char_index = int(command_cap[:index])
					command_cap = command_cap[len(str(char_index)):]
					break

		if command_cap[0] == ' ':
			command_cap[1:]
	else:
		command_cap = ''

	command = command_cap.lower()

	if prefix not in ['c', 'x', 'z', 'ㅊ', 'ㅌ', 'ㅋ']:
		return None

	if command_cap == '':
		return None

	author = message.author
	channel = message.channel
	display_name = author.display_name

	if message.guild is None:
		words = command.split()
		if words[0] in keywords_auth:
			if len(words) > 1:
				code = command_cap.split()[1]
				return_message = KIN3_database.add_token(code, author.id)

				if return_message == '':
					await channel.send(f'{display_name}, 등록이 완료되었습니다')
				else:
					await channel.send(f'에러가 발생했습니다, 관리자에게 문의해주세요\n에러코드: {return_message}')
			else:
				await channel.send(embed = auth_embed)
				return None

		return None

	waitlist = server_list.get_waitlist(message.guild.id)

	# channel management
	if waitlist.xup_channel is None:
		waitlist.xup_channel = channel

	# c command
	if prefix in ['c', 'ㅊ']:
		if command == 'shutdown':
			if author.id == admin_id:
				await channel.send(f'Bot is now shutting down')
				await bot.logout()
				await bot.close()
			else:
				await channel.send(f'Shutdown can only be done by admin')

			return None

		if command in ['billboard', '빌보드', '전광판']:
			if waitlist.billboard_message is not None:
			#	await waitlist.billboard_message.delete()
				waitlist.billboard_message = None

			#await message.delete()
			await channel.send('init_billboard')
			return None

		if command in ['xup', '엑스업']:
			waitlist.xup_channel = channel
			await channel.send('현재 채널을 엑스업 채널로 지정')
			return None

		if command in ['reset', '리셋', '초기화']:
			waitlist.reset_waitlist()
			waitlist.reset_request()
			await channel.send('대기열 초기화')
			return None

		words = command.split()
		if words[0] in keywords_auth:
			if len(words) > 1:
				code = command_cap.split()[1]
				return_message = KIN3_database.add_token(code, author.id)

				if return_message == '':
					await channel.send(f'{display_name}, 등록이 완료되었습니다')
				else:
					await channel.send(f'에러가 발생했습니다, 관리자에게 문의해주세요\n에러코드: {return_message}')
			else:
				await channel.send(embed = auth_embed)

			return None

		if len(keywords_auth_cancel.intersection(words)) > 0:
			eve_char_object = await KIN3_database.process_char_index(author, char_index, channel, display_name, auth_embed)
			if eve_char_object is not None:
				KIN3_database.remove_auth(eve_char_object)
				await channel.send(f'{display_name}, 등록내역({eve_char_object.name})이 삭제되었습니다')

			return None

		if words[0] == 'hotcode':
			if author.id == admin_id:
				lines = command_cap.split('\n')
				if len(lines) == 1:
					lines = [' '.join(command_cap.split(' ')[1:])]

					if lines[0][:3] == '```':
						lines[0] = lines[0][3:]
					elif lines[0][:1] == '`':
						lines[0] = lines[0][1:]

					if lines[0][-3:] == '```':
						lines[0] = lines[0][:-3]
					elif lines[0][-1:] == '`':
						lines[0] = lines[0][:-1]
				else:
					lines = lines[1:]

					if lines[0][:3] == '```':
						lines[0] = lines[0][3:]
					elif lines[0][:1] == '`':
						lines[0] = lines[0][1:]

					if lines[-1][-3:] == '```':
						lines[-1] = lines[-1][:-3]
					elif lines[-1][-1:] == '`':
						lines[-1] = lines[-1][:-1]

				hotcode = 'def hotfunc():'
				for line in lines:
					hotcode += '\n\t' + line
				hotcode += '\nKIN3_common.hotcode_return = hotfunc()'

				try:
					KIN3_common.hotcode_return = None
					exec(hotcode)
					await channel.send(f'Code run complete, return: {KIN3_common.hotcode_return}')
				except Exception as error:
					await channel.send(f'Code run fail, error: {error}')
			else:
				await channel.send(f'Hotcode can only be run by admin')

			return None

		return None

	# x up
	if prefix in ['x', 'ㅌ']:
		roles = command.split()
		if not len((keywords_dps | keywords_snp | keywords_logi | keywords_cancel).intersection(roles)) > 0:
			return None

		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			eve_char_object = await KIN3_database.process_char_index(author, char_index, channel, display_name, auth_embed)
			if eve_char_object is None:
				return None

			if len(keywords_dps.intersection(roles)) > 0:
				result = waitlist.add_dps(eve_char_object)
				if result > 0:
					await channel.send(f'{display_name}({eve_char_object.name}) DPS로 x up, 대기번호 {waitlist.waitcount_dps}번')
				elif result == -1:
					await channel.send(f'{eve_char_object.name}은(는) 이미 대기열에 있는 캐릭터입니다')
				elif result == -2:
					await channel.send(f'{eve_char_object.name}은(는) 이미 플릿에 소속된 캐릭터입니다')

			if len(keywords_snp.intersection(roles)) > 0:
				result = waitlist.add_snp(eve_char_object)
				if result > 0:
					await channel.send(f'{display_name}({eve_char_object.name}) SNP로 x up, 대기번호 {waitlist.waitcount_snp}번')
				elif result == -1:
					await channel.send(f'{eve_char_object.name}은(는) 이미 대기열에 있는 캐릭터입니다')
				elif result == -2:
					await channel.send(f'{eve_char_object.name}은(는) 이미 플릿에 소속된 캐릭터입니다')

			if len(keywords_logi.intersection(roles)) > 0:
				result = waitlist.add_logi(eve_char_object)
				if result > 0:
					await channel.send(f'{display_name}({eve_char_object.name}) LOGI로 x up, 대기번호 {waitlist.waitcount_logi}번')
				elif result == -1:
					await channel.send(f'{eve_char_object.name}은(는) 이미 대기열에 있는 캐릭터입니다')
				elif result == -2:
					await channel.send(f'{eve_char_object.name}은(는) 이미 플릿에 소속된 캐릭터입니다')

			if len(keywords_cancel.intersection(roles)) > 0:
				waitlist.remove_user(eve_char_object)
				await channel.send(f'{display_name}({eve_char_object.name}) 대기열에서 퇴장')

		return None

	# z pull
	if prefix in ['z', 'ㅋ']:
		items = command.split()
		roles = [''.join([x for x in item if not x.isdigit()]) for item in items]
		if not len((keywords_dps | keywords_snp | keywords_logi | keywords_cancel).intersection(roles)) > 0:
			return None

		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			eve_char_object = await KIN3_database.process_char_index(author, char_index, channel, display_name, auth_embed)
			if eve_char_object is None:
				return None

			if len(keywords_cancel.intersection(items)) > 0:
				waitlist.remove_request(author)
				await channel.send(f'{display_name}({eve_char_object.name}) 모집 취소')
			else:
				request_dps, request_snp, request_logi = 0, 0, 0

				for index in range(len(items)):
					item = items[index]
					request_number = -1
					pure_command = ''.join([x for x in item if not x.isdigit()])
					command_number = ''.join([x for x in item if x.isdigit()])

					if pure_command != '':
						if command_number != '':
							request_number = int(command_number)
						else:
							if index < len(items) - 1:
								command_number_next = ''.join([x for x in items[index + 1] if x.isdigit()])
								if command_number_next == items[index + 1]:
									request_number = int(command_number_next)
								else:
									request_number = 1
							else:
								request_number = 1

					if request_number > 0:
						if pure_command in keywords_dps:
							request_dps += request_number

						if pure_command in keywords_snp:
							request_snp += request_number

						if pure_command in keywords_logi:
							request_logi += request_number

				if request_dps + request_snp + request_logi > 0:
					await channel.send(f'{display_name}({eve_char_object.name})이(가) DPS {request_dps}명, SNP {request_snp}명, LOGI {request_logi}명을 모집')
					request_return = waitlist.request_users(request_dps, request_snp, request_logi)
					if request_return is not None:
						notice_text = waitlist.request_announcement((eve_char_object,) + request_return)
						await channel.send(notice_text)

						# eve_char_object.fleet_invite(request_return[0] + request_return[1] + request_return[2])
					else:
						waitlist.add_request(eve_char_object, request_dps, request_snp, request_logi)
						await channel.send('대기중인 인원 부족, 인원이 차면 알림이 갑니다')

		return None

async def event_periodic_5s():
	global server_list

	while True:
		# check server status
		try:
			KIN3_Esi.is_server_online(True)
		except:
			pass

		for waitlist in server_list.waitlists:
			# check token validities
			try:
				waitlist.filter_vailid_members()
			except:
				pass

			# check fleet status
			try:
				infleet_characters = waitlist.filter_infleet_characters()
				for character in infleet_characters:
					await waitlist.xup_channel.send(f'{character.name}이(가) 플릿에 소속되어 대기열에서 제외되었습니다')
			except:
				pass

			# check request list
			check_return = waitlist.check_requests()
			if check_return is not None:
				notice_text = waitlist.request_announcement(check_return)
				await waitlist.xup_channel.send(notice_text)

				# check_return[0].fleet_invite(check_return[1] + check_return[2] + check_return[3])

			# update billboard
			try:
				waitlist.update_billboard()
			except:
				pass

			if waitlist.billboard_message is not None:
				try:
					await waitlist.billboard_message.edit(content = waitlist.billboard_text)
				except:
					pass

		await asyncio.sleep(5)

async def event_periodic_60s():
	while True:
		# check token validities
		try:
			KIN3_database.filter_vailid_tokens()
		except:
			pass

		await asyncio.sleep(60)

# setup main
auth_key_file = open('./esi_auth_key.txt', 'r')
auth_key_lines = auth_key_file.readlines()
redirect_uri = auth_key_lines[0].strip()
client_id = auth_key_lines[1].strip()
secret_key = auth_key_lines[2].strip()

# load esi objects
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

KIN3_Esi.esi_latest = (app_latest, security, client)
# KIN3_Esi.esi_v1 = (app_v1, security, client)
KIN3_Esi.esi_v2 = (app_v2, security, client)
KIN3_Esi.is_tranquility_online = 'players' in KIN3_Esi.check_server_status()
if KIN3_Esi.is_tranquility_online:
	print(f'{KIN3_common.timestamp()} : Tranquility server is online')
else:
	print(f'{KIN3_common.timestamp()} : Tranquility server is offline')
print(f'{KIN3_common.timestamp()} : --------')

bot_token_file = open('./bot_token.txt', 'r')
bot_token_lines = bot_token_file.readlines()
bot_token = bot_token_lines[0].strip()
admin_id = int(bot_token_lines[1].strip())

keywords_auth = {'auth', '인증', '등록'}
keywords_auth_cancel = {'auth_cancel', '인증취소', '등록취소'}
keywords_dps = {'dps', 'vindi', 'vindicator', '디피', '빈디', '빈디케이터'}
keywords_snp = {'snp', 'sniper', 'nightmare', 'machariel', '스나', '나메', '나이트메어', '마차', '마차리엘'}
keywords_logi = {'logi', 'scimitar', 'basilisk', '로지', '시미타', '바실리스크', '바실'}
keywords_cancel = {'cancel', '취소'}

esi_scopes = [
	'esi-location.read_location.v1',
	'esi-fleets.read_fleet.v1',
	'esi-fleets.write_fleet.v1',
	'esi-fittings.read_fittings.v1',
	'esi-characters.read_chat_channels.v1',
	'esi-location.read_online.v1'
]
auth_url = security.get_auth_uri(state = 'KIN3_FC_Auth', scopes = esi_scopes)
auth_description = 'EVE 계정과 KIN3 대기열 봇을 연결\n인증명령어: `ㅊ인증 코드`'
auth_embed = discord.Embed(title = '계정등록 링크', url = auth_url, description = auth_description)

server_list = KIN3_waitlist.server_list()
periodic_5s_running = False
periodic_60s_running = False
tcp_server_online = False

print(f'{KIN3_common.timestamp()} : Starting bot')
bot.run(bot_token)
