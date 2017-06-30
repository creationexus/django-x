$(document).ready(function(){
var $container=$('.items'),input=$('input#s'),divInput=$('div.input'),width=divInput.width();
var outerWidth=divInput.parent().width()-(divInput.outerWidth()-width)-28;
var submit=$('#searchSubmit'),txt=input.val();
input.bind('focus',function(){
    if(input.val()===txt){input.val('');}
    $(this).animate({color:'#000'},300);
    $(this).css('color','#000');
    $(this).parent().animate({
        width:outerWidth+'px',
        backgroundColor:'#fff',
        paddingRight:'43px'
    },300,function(){
        if(!(input.val()===''||input.val()===txt)){
            if(!($.browser.msie&&$.browser.version<9)){submit.fadeIn(300);
            }else{submit.css({display:'block'});}
        }
    }).addClass('focus');
}).bind('blur',function(){
    $(this).animate({color:'#b4bdc4'},300);
    $(this).css('color','#b4bdc4');
    $(this).parent().animate({
        width: width + 'px',
        backgroundColor: '#e8edf1',
        paddingRight: '15px'
    },300,function(){
        if(input.val()===''){
            input.val(txt);
        }
    }).removeClass('focus');
    if(!($.browser.msie && $.browser.version<9)){
        submit.fadeOut(100);
    } else {
        submit.css({display:'none'});
    }
}).keyup(function(e){
    if(e.keyCode==13){
        $(this).trigger("enterKey");
    }
/*if(input.val()===''){
    if(!($.browser.msie && $.browser.version < 9)) {
        submit.fadeOut(300);
    } else {
        submit.css({display: 'none'});
    }
    $container.isotope({
   	 itemSelector:'.item',
   	 filter:'.item',
   	 layoutMode:'masonry',
   	 animationEngine:'jquery',
   	 animationOptions:{
   	  duration:750,
   	  easing:'linear'
   	 }
     });
}else{
    if(!($.browser.msie&&$.browser.version<9)){
        submit.fadeIn(300);
    } else {
        submit.css({display:'block'});
    }
    if(input.val().length>0&&input.val()!='item'){$container.isotope({
	 itemSelector:'.item',
	 filter:'.'+input.val()+'*',
	 layoutMode:'masonry',
	 animationEngine:'jquery',
	 animationOptions:{
	  duration:750,
	  easing:'linear'
	 }
    });}
}*/
}).bind("enterKey",function(e){
	if($('#s').val()!=''){
        if(!($.browser.msie&&$.browser.version<9)){
        	$('#searchSubmit').fadeIn(300);
        }else{
        	$('#searchSubmit').css({display: 'block'});
        }
    }
	if($('#s').val()!=''){
		window.location.href="http://oclck.com/events/search/"+$('#type').text()+"/?q="+$("#s").val();
	}
});
});