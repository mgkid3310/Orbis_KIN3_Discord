import wixLocation from 'wix-location';
import { fetch, getJSON } from 'wix-fetch';
import { session } from 'wix-storage';
import FormData from 'form-data';

$w.onReady(function () {
	$w('#html1').onMessage((event) => {
		$w('#text6').text = event.data
	});

	$w('#html1').postMessage('req_update');

	if (wixLocation.query.code) {
		const accessCode = wixLocation.query.code;
		const data = new FormData();

		data.append('client_id', '648002090127327245');
		data.append('client_secret', 'secret');
		data.append('grant_type', 'authorization_code');
		data.append('redirect_uri', 'https://mgkid3310.wixsite.com/kin3/waitlist');
		data.append('scope', 'identify');
		data.append('code', accessCode);

		fetch('https://discordapp.com/api/oauth2/token', {
				method: 'POST',
				body: data
			})
			.then(res => res.json())
			.then(info => getJSON('https://discordapp.com/api/users/@me', {
					headers: {
						authorization: `${info.token_type} ${info.access_token}`,
					},
				})
				.then(data => {
					session.setItem('discord_id', String(data.id));
					if (session.getItem('auth_code')) {
						$w('#text8').text = session.getItem('auth_code') + ':' + String(data.id)
						session.removeItem('auth_code')
					}
				})
			)
	}

	if (session.getItem('auth_code') && session.getItem('discord_id')) {
		$w('#text8').text = session.getItem('auth_code') + ':' + session.getItem('discord_id');
		session.removeItem('auth_code');
	}
});

export function button2_click(event) {
	$w('#text8').text = session.getItem('auth_code') + ':' + session.getItem('discord_id');
}

export function button6_click(event) {
	$w('#html1').postMessage('req_update');
}
