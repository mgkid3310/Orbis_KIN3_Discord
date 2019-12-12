$w.onReady(function () {
	$w('#html1').onMessage((event) => {
		$w('#text6').text = event.data
	});

	$w('#html1').postMessage('req_update');
});

export function button2_click(event) {
	//Add your code for this event here:
}

export function button5_click(event) {
	//Add your code for this event here:
}

export function button6_click(event) {
	$w('#html1').postMessage('req_update');
}

export function button7_click(event) {
	//Add your code for this event here:
}
