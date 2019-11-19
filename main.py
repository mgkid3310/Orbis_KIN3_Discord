import asyncio
import discord
import KIN3_waitlist as KIN3

token_file = open('C:/Users/PowerUser/Documents/GitHub/Orbis_KIN3_Discord/bot_token.txt', 'r')
lines = token_file.readlines()
token = lines[0].strip()

keywords_dps = ['dps', 'vindi', 'vindicator', '디피', '빈디']
keywords_snp = ['snp', 'sniper', 'nightmare', '스나', '나메']
keywords_logi = ['logi', '로지']
keywords_cancel = ['cancel', '취소']

bot = discord.Client()
server_list = KIN3.server_list()

@bot.event
async def on_ready():
	print('logging in as')
	print(f'name : {bot.user.name}')
	print(f'id : {bot.user.id}')

	await bot.change_presence(activity = discord.Game(name = 'KIN3', type = 1))

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
	command = message.content[2:].lower()
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
					await waitlist.xup_channel.send('대기열에서 퇴갤')

	# z pull
	if prefix in ['z', 'ㅋ']:
		if waitlist.xup_channel is None:
			waitlist.xup_channel = channel

		if channel == waitlist.xup_channel:
			items = command.split(' ')
			request_dps, request_snp, request_logi = 0, 0, 0

			for index in range(len(items)):
				item = items[index]
				request_number = -1
				pure_command = ''.join([i for i in item if not i.isdigit()])
				command_number = ''.join([i for i in item if i.isdigit()])

				if pure_command != '':
					if command_number != '':
						request_number = int(command_number)
					else:
						if index < len(items) - 1:
							command_number_next = ''.join([i for i in items[index + 1] if i.isdigit()])
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
				waitlist.add_request(message.author, request_dps, request_snp, request_logi)
				await waitlist.xup_channel.send(f'{message.author}가 DPS {request_dps}명, SNP {request_snp}명, LOGI {request_logi}명 모집')
				if not waitlist.is_ready(request_dps, request_snp, request_logi):
					await waitlist.xup_channel.send('대기중인 인원 부족, 인원 차면 알림이 갑니다')

	# check request list
	request_return = waitlist.check_requests()
	if request_return is not None:
		notice_text = f'{request_return[0].mention}, 모집이 완료되었습니다:'
		for user in request_return[1]:
			notice_text += f' {user.mention}(DPS),'
		for user in request_return[2]:
			notice_text += f' {user.mention}(SNP),'
		for user in request_return[3]:
			notice_text += f' {user.mention}(LOGI),'
		notice_text = notice_text[:-1]

		await waitlist.xup_channel.send(notice_text)

	# update billboard
	waitlist.update_billboard()
	if waitlist.billboard_message is not None:
		await waitlist.billboard_message.edit(content = waitlist.billboard_text)

bot.run(token)
