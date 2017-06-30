/**
 * carriagadad
 */
var inst = $('[data-remodal-id=modal]').remodal();
//inst.open();

$(document).on('confirm', '.remodal', function () {
    console.log($('#email').val());
});

$('#show-login').click(function(){
	$('#register').hide('fast');
	$('#login').show('fast');
});

$('#show-register').click(function(){
	$('#login').hide('fast');
	$('#register').show('fast');
});

$('#slider-id').liquidSlider();