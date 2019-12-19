import wixLocation from 'wix-location';
import { session } from 'wix-storage';

$w.onReady(function () {
	if (wixLocation.query.code) {
		let code = wixLocation.query.code;
		session.setItem('auth_code', code)
		if (session.getItem('discord_id')) {
			wixLocation.to('https://mgkid3310.wixsite.com/kin3/waitlist')
		} else {
			$w('#text6').text = 'ㅊ 인증 ' + code;
		}
	} else {
		$w('#text6').text = '오류가 발생했습니다, 다시 시도해주세요';
	}
});
