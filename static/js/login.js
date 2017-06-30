/**
 * 
 */
var images = ['01.jpg', '02.jpg', '03.jpg', '04.jpg', '05.jpg', '06.jpg', '07.jpg', '08.jpg', '09.jpg', '10.jpg'];

$(document).ready(function(){
    //images[Math.floor(Math.random() * images.length)]
    $.backstretch('/static/images/' + images[Math.floor(Math.random() * images.length)] );
    position_elements();
});

$(window).resize(function(){
    position_elements();
});

function position_elements(){
    $('#overlay').css('height', $(window).height());
    if($(window).height() > $('.form-signin').height() + 100){
        $('.form-signin').css('top', ( ($(window).height()/2) - ($('.form-signin').height()/2) ) - $('header').height() + 'px' );
    } else {
        $('.form-signin').css('top', '0px');
    }
    $('.backstretch, #main, .form-signin').fadeIn();
}