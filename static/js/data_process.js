$('document').ready(function(){

NProgress.start();


var slide_pos = 1;

$('#random-right').click(function(){
  if(slide_pos < 3){
    $('#random-slider').css('left', parseInt($('#random-slider').css('left')) - parseInt($('.random-container').width()) -28 + 'px') ;
    slide_pos += 1;
  }
});

$('#random-left').click(function(){
  if(slide_pos > 1){
    $('#random-slider').css('left', parseInt($('#random-slider').css('left')) + parseInt($('.random-container').width()) +28 + 'px') ;
        slide_pos -= 1;
      }
    });


  });


  $(window).load(function () {
    NProgress.done();
  });

  $(window).resize(function(){
    jquery_sticky_footer();
  });


  $(window).bind("load", function() {    
    jquery_sticky_footer();
  });

  function jquery_sticky_footer(){
    var footer = $("#footer");
var pos = footer.position();
var height = $(window).height();
height = height - pos.top;
height = height - footer.outerHeight();
if (height > 0) {
  footer.css({'margin-top' : height+'px'});
    }
  }

  /********** Mobile Functionality **********/

  var mobileSafari = '';

  $(document).ready(function(){
    $('.mobile-menu-toggle').click(function(){
  $('.mobile-menu').toggle();
  $('body').toggleClass('mobile-margin').toggleClass('body-relative');
  $('.navbar').toggleClass('mobile-margin');
});


// Assign a variable for the application being used
var nVer = navigator.appVersion;
// Assign a variable for the device being used
    var nAgt = navigator.userAgent;
    var nameOffset,verOffset,ix;
   
   
    // First check to see if the platform is an iPhone or iPod
if(navigator.platform == 'iPhone' || navigator.platform == 'iPod'){
  // In Safari, the true version is after "Safari" 
  if ((verOffset=nAgt.indexOf('Safari'))!=-1) {
    // Set a variable to use later
    mobileSafari = 'Safari';
      }
    }
   
    // If is mobile Safari set window height +60
if (mobileSafari == 'Safari') { 
  // Height + 60px
  $('.mobile-menu').css('height', (parseInt($(window).height())+ 60) + 'px' );
} else {
  // Else use the default window height
  $('.mobile-menu').css('height', $(window).height()); 
    };

  });

  $(window).resize(function(){
    // If is mobile Safari set window height +60
if (mobileSafari == 'Safari') { 
  // Height + 60px
  $('.mobile-menu').css('height', (parseInt($(window).height())+ 60) + 'px' );
} else {
  // Else use the default window height
  $('.mobile-menu').css('height', $(window).height()); 
    };
  });

  /********** End Mobile Functionality **********/