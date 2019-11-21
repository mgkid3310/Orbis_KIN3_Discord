import asyncio
import discord
import KIN3_waitlist

token_file = open('./bot_token.txt', 'r')
lines = token_file.readlines()
token = lines[0].strip()

keywords_dps = ['dps', 'vindi', 'vindicator', '디피', '빈디', '빈디케이터']
keywords_snp = ['snp', 'sniper', 'nightmare', 'machariel', '스나', '나메', '나이트메어', '마차', '마차리엘']
keywords_logi = ['logi', '로지']
keywords_cancel = ['cancel', '취소']

bot = discord.Client()
server_list = KIN3_waitlist.server_list()

@bot.event
async def on_ready():
	print('Bot logged in as')
	print(f'name : {bot.user.name}')
	print(f'id : {bot.user.id}')

	await bot.change_presence(activity = discord.Game(name = 'KIN3', type = 1))
	bot.loop.create_task(event_periodic())

@bot.event
async def on_message(message):
	global keywords_dps
	global keywords_snp
	global keywords_logi
	global server_list

	waitlist = server_list.get_waitlist(message.guild.id)

	if message.content == '':
		return None

	if message.author.bot:
		if message.content == 'init_billboard':
			waitlist.billboard_message = message
			await message.edit(content = waitlist.billboard_text)

		return None

	prefix = message.content[0].lower()

	if prefix not in ['c', 'x', 'z', 'ㅊ', 'ㅌ', 'ㅋ']:
		return None

	if len(message.content) > 1:
		if message.content[1] == ' ':
			command = message.content[2:].lower()
		else:
			command = message.content[1:].lower()
	else:
		command = ''
	channel = message.channel

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

		if command in ['reset', '리셋', '초기화']:
			waitlist.reset_waitlist()
			waitlist.reset_request()
			await waitlist.xup_channel.send('대기열 초기화')

	# x up
	if prefix in ['x', 'ㅌ']:
		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			roles = command.split(' ')

			for role in roles:
				if role in keywords_dps:
					waitlist.add_dps(message.author)
					await waitlist.xup_channel.send(f'DPS로 x up, 대기번호 {waitlist.waitcount_dps}번')

				if role in keywords_snp:
					waitlist.add_snp(message.author)
					await waitlist.xup_channel.send(f'SNP로 x up, 대기번호 {waitlist.waitcount_snp}번')

				if role in keywords_logi:
					waitlist.add_logi(message.author)
					await waitlist.xup_channel.send(f'LOGI로 x up, 대기번호 {waitlist.waitcount_logi}번')

				if role in keywords_cancel:
					waitlist.remove_user(message.author)
					await waitlist.xup_channel.send('대기열에서 퇴장')

	# z pull
	if prefix in ['z', 'ㅋ']:
		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			items = command.split(' ')

			if len(set(keywords_cancel).intersection(items)) > 0:
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
					await waitlist.xup_channel.send(f'{message.author.display_name}이(가) DPS {request_dps}명, SNP {request_snp}명, LOGI {request_logi}명을 모집')
					request_return = waitlist.request_users(request_dps, request_snp, request_logi)
					if request_return is not None:
						notice_text = waitlist.request_announcement((message.author,) + request_return)
						await waitlist.xup_channel.send(notice_text)
					else:
						waitlist.add_request(message.author, request_dps, request_snp, request_logi)
						await waitlist.xup_channel.send('대기중인 인원 부족, 인원이 차면 알림이 갑니다')

async def event_periodic():
	while True:
		for waitlist in server_list.waitlists:
			# check request list
			request_return = waitlist.check_requests()
			if request_return is not None:
				notice_text = waitlist.request_announcement(request_return)
				await waitlist.xup_channel.send(notice_text)

			# update billboard
			waitlist.update_billboard()
			if waitlist.billboard_message is not None:
				await waitlist.billboard_message.edit(content = waitlist.billboard_text)

		await asyncio.sleep(1)

bot.run(token)
