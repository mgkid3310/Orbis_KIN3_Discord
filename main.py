import asyncio
import discord

from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity

import KIN3_Esi
import KIN3_database
import KIN3_waitlist
import KIN3_socket

# load bot
bot = discord.Client()

# define event & functions
@bot.event
async def on_ready():
	global tcp_server

	await bot.change_presence(activity = discord.Game(name = 'KIN3', type = 1))
	print('Bot logged in as')
	print(f'name : {bot.user.name}')
	print(f'id : {bot.user.id}')

	# start periodic bot loop
	bot.loop.create_task(event_periodic_1s())
	bot.loop.create_task(event_periodic_60s())
	print('Periodic bot loop started')
	print('--------')

	# start tcp server
	tcp_server = await KIN3_socket.start_tcp_server(bot, tcp_server)

	# tcp connection test
	# await KIN3_socket.test_tcp_server()

@bot.event
async def on_message(message):
	global keywords_auth
	global keywords_dps
	global keywords_snp
	global keywords_logi
	global keywords_cancel
	global auth_embed
	global server_list
	global esi_objects
	global auth_url

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

	if message.guild is None:
		words = command.split(' ')
		if words[0] in keywords_auth:
			if len(words) > 1:
				code = command_cap.split(' ')[1]
				return_message = KIN3_database.add_token(esi_objects, code, message.author.id)

				if return_message == '':
					await message.channel.send(f'{display_name}, 등록이 완료되었습니다')
				else:
					await message.channel.send(f'에러가 발생했습니다, 관리자에게 문의해주세요\n에러코드: {return_message}')
			else:
				await message.channel.send(embed = auth_embed)
				return None

		return None

	waitlist = server_list.get_waitlist(message.guild.id)

	channel = message.channel
	display_name = message.author.display_name

	# channel management
	if waitlist.xup_channel is None:
		waitlist.xup_channel = channel

	# c command
	if prefix in ['c', 'ㅊ']:
		if command in ['bot_exit', '봇_종료']:
			#for server in server_list.waitlists:
			#	if server.billboard_message is not None:
			#		await server.billboard_message.delete()

			await bot.logout()
			await bot.close()

		if command in ['billboard', '빌보드', '전광판']:
			if waitlist.billboard_message is not None:
			#	await waitlist.billboard_message.delete()
				waitlist.billboard_message = None

			#await message.delete()
			await channel.send('init_billboard')

		if command in ['xup', '엑스업']:
			waitlist.xup_channel = channel
			await waitlist.xup_channel.send('현재 채널을 엑스업 채널로 지정')

		if command in ['reset', '리셋', '초기화']:
			waitlist.reset_waitlist()
			waitlist.reset_request()
			await waitlist.xup_channel.send('대기열 초기화')

		words = command.split(' ')
		if words[0] in keywords_auth:
			if len(words) > 1:
				code = command_cap.split(' ')[1]
				return_message = KIN3_database.add_token(esi_objects, code, message.author.id)

				if return_message == '':
					await message.channel.send(f'{display_name}, 등록이 완료되었습니다')
				else:
					await message.channel.send(f'에러가 발생했습니다, 관리자에게 문의해주세요\n에러코드: {return_message}')
			else:
				await message.channel.send(embed = auth_embed)
				return None

	# x up
	if prefix in ['x', 'ㅌ']:
		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			auth_count = KIN3_database.auth_count(message.author)
			if not auth_count > 0:
				await waitlist.xup_channel.send(f'{display_name}, 계정이 등록되지 않은 유저입니다, 계정 인증이 필요합니다')
				await waitlist.xup_channel.send(embed = auth_embed)
				return None
			else:
				if auth_count > 1 and char_index is None:
					await waitlist.xup_channel.send(f'{display_name}, 등록된 계정이 두개 이상입니다. 계정을 특정해주세요')
					await waitlist.xup_channel.send(KIN3_database.xup_selection_info(message.author))
					return None

				eve_char_object = KIN3_database.get_character_object(esi_objects, message.author, char_index)
				if eve_char_object is None:
					await waitlist.xup_channel.send(f'{display_name}, 에러가 발생했습니다. 관리자에게 문의해주세요\n에러코드: KIN3_database 101, character object init fail')
					return None

			roles = command.split(' ')

			if len(keywords_dps.intersection(roles)) > 0:
				result = waitlist.add_dps(eve_char_object)
				if result > 0:
					await waitlist.xup_channel.send(f'{display_name} DPS로 x up, 대기번호 {waitlist.waitcount_dps}번')
				else:
					await waitlist.xup_channel.send(f'{eve_char_object.name}은 이미 대기열에 있는 캐릭터입니다')

			if len(keywords_snp.intersection(roles)) > 0:
				result = waitlist.add_snp(eve_char_object)
				if result > 0:
					await waitlist.xup_channel.send(f'{display_name} SNP로 x up, 대기번호 {waitlist.waitcount_snp}번')
				else:
					await waitlist.xup_channel.send(f'{eve_char_object.name}은 이미 대기열에 있는 캐릭터입니다')

			if len(keywords_logi.intersection(roles)) > 0:
				result = waitlist.add_logi(eve_char_object)
				if result > 0:
					await waitlist.xup_channel.send(f'{display_name} LOGI로 x up, 대기번호 {waitlist.waitcount_logi}번')
				else:
					await waitlist.xup_channel.send(f'{eve_char_object.name}은 이미 대기열에 있는 캐릭터입니다')

			if len(keywords_cancel.intersection(roles)) > 0:
				waitlist.remove_user(eve_char_object)
				await waitlist.xup_channel.send(f'{display_name} 대기열에서 퇴장')

	# z pull
	if prefix in ['z', 'ㅋ']:
		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			auth_count = KIN3_database.auth_count(message.author)
			if not auth_count > 0:
				await waitlist.xup_channel.send(f'{display_name}, 계정이 등록되지 않은 유저입니다, 계정 인증이 필요합니다')
				await waitlist.xup_channel.send(embed = auth_embed)
				return None
			else:
				if auth_count > 1 and char_index is None:
					await waitlist.xup_channel.send(f'{display_name}, 등록된 계정이 두개 이상입니다. 계정을 특정해주세요')
					await waitlist.xup_channel.send(KIN3_database.xup_selection_info(message.author))
					return None

				eve_char_object = KIN3_database.get_character_object(esi_objects, message.author, char_index)
				if eve_char_object is None:
					await waitlist.xup_channel.send(f'{display_name}, 에러가 발생했습니다, 관리자에게 문의해주세요\n에러코드: KIN3_database 101, character object init fail')
					return None

			items = command.split(' ')

			if len(keywords_cancel.intersection(items)) > 0:
				waitlist.remove_request(message.author)
				await waitlist.xup_channel.send('모집 취소')
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
					await waitlist.xup_channel.send(f'{display_name}이(가) DPS {request_dps}명, SNP {request_snp}명, LOGI {request_logi}명을 모집')
					request_return = waitlist.request_users(request_dps, request_snp, request_logi)
					if request_return is not None:
						notice_text = waitlist.request_announcement((eve_char_object,) + request_return)
						await waitlist.xup_channel.send(notice_text)

						# eve_char_object.fleet_invite(request_return[0] + request_return[1] + request_return[2])
					else:
						waitlist.add_request(eve_char_object, request_dps, request_snp, request_logi)
						await waitlist.xup_channel.send('대기중인 인원 부족, 인원이 차면 알림이 갑니다')

async def event_periodic_1s():
	global server_list

	while True:
		for waitlist in server_list.waitlists:
			# check token validities
			waitlist.filter_vailid_members()

			# check request list
			check_return = waitlist.check_requests()
			if check_return is not None:
				notice_text = waitlist.request_announcement(check_return)
				await waitlist.xup_channel.send(notice_text)

				# check_return[0].fleet_invite(check_return[1] + check_return[2] + check_return[3])

			# update billboard
			waitlist.update_billboard()
			if waitlist.billboard_message is not None:
				await waitlist.billboard_message.edit(content = waitlist.billboard_text)

		await asyncio.sleep(1)

async def event_periodic_60s():
	global esi_objects

	while True:
		# check token validities
		KIN3_database.filter_vailid_tokens(esi_objects)

		await asyncio.sleep(60)

# setup main
app = EsiApp().get_latest_swagger
print('EsiApp loaded')

auth_key_file = open('./esi_auth_key.txt', 'r')
auth_key_lines = auth_key_file.readlines()
redirect_uri = auth_key_lines[0].strip()
client_id = auth_key_lines[1].strip()
secret_key = auth_key_lines[2].strip()

security = EsiSecurity(
	headers = {'User-Agent':'something'},
	redirect_uri = redirect_uri,
	client_id = client_id,
	secret_key = secret_key
)
print('EsiSecurity loaded')

client = EsiClient(
	headers = {'User-Agent':'something'},
	retry_requests = True,
	header = {'User-Agent': 'Something CCP can use to contact you and that define your app'},
	security = security
)
print('EsiClient loaded')
print('--------')

esi_objects = (app, security, client)

bot_token_file = open('./bot_token.txt', 'r')
bot_token_lines = bot_token_file.readlines()
bot_token = bot_token_lines[0].strip()

keywords_auth = {'auth', '인증', '등록'}
keywords_dps = {'dps', 'vindi', 'vindicator', '디피', '빈디', '빈디케이터'}
keywords_snp = {'snp', 'sniper', 'nightmare', 'machariel', '스나', '나메', '나이트메어', '마차', '마차리엘'}
keywords_logi = {'logi', '로지'}
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
tcp_server = None

print('Starting bot')
bot.run(bot_token)
