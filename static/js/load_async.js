var agx=1,b=0,items=[],bloq=false,load_ci=0;
var $=jQuery.noConflict(),$container=$('.items');
function img_loaded(i){
  if(items[i].hasClass("stamp")){$('.items').append(items[i]);$container.isotope('stamp',items[i]);$('.stamp').css('position','absolute').css('left','0px').css('top','0px').css('background-color','rgba(253,188,70,1)');}else{insert(items[i]);}
  btn=items[i].children().children('.ax_pk').children().children().children();$container.isotope('layout');
  if(btn!=undefined){
	  $(btn).easyconfirm({locale:{title:'Delete confirmation',text:'Are you sure?',button:['Cancel','Confirm'],closeText:'oClock'}});
		$(".del_obj").click(function(e){
			  objis=$(this).parent().parent().parent().parent().parent();
			  $.ajax({
				  dataType:"text",data:{id:$(this).parent()[0].id},url:'/event/delete/',type:'post',beforeSend:function(){},
				  success:function(response){
				   if(response=="ok"){$container.isotope('remove',objis).isotope('layout');}}
				});e.stopPropagation();
		});
  }load_ci++;if(agx<=2&&load_ci>=30){$('.items').animate({opacity:1},750)}
  if(agx<=2&&load_ci>=items.length){$('.items').animate({opacity:1},750)}
}
function go_url(u){window.location=u;}
function insert(e){$container.isotope('insert',e);/*$container.isotope('updateSortData').isotope();*/}
function get_more_items(){
var type=$('#type').text(),search=$('#search').text();
$('#get_more').attr('disabled',true);bloq=true;
$.ajax({
  dataType:"json",data:{page:agx,type:type,id:$('#ui').text(),search:search},
  url:'/api_v2/events/',type:'post',beforeSend:function(){$('#get_more_img').show();},
  success:function(response){
  $('#get_more').attr('disabled',false);
  for (var idx in response['r']){
	ev=response['r'][idx];hashtags='';
	for(var idz in ev['events_hashtags']){z=ev['events_hashtags'][idz];
      hashtags+='<div style="margin:3px 0;background-color:rgba(0,0,0,0.5);font-size:1.2em;font-weight:bold;padding:5px;display: inline-table;float: right;clear: right;"><a style="color:#FFA;" href="/hashtag/?q='+z['hashtags_value_str'].trim()+'&id='+z['hashtags_id']+'">#'+z['hashtags_value_str'].trim()+'&nbsp;</a></div>';
     }
	 if(type=="draft"){
		 dateq=null;if(ev.events_start!=undefined){dateq=ev.events_start.split(' ')[0];}
		 if(ev.events_finish!=undefined){dateq=ev.events_finish.split(' ')[0];}
		 if(dateq!=null){
			 items.push(content=$('<div class="item running"><div style="float:right;margin:10px 10px;color:gray;">'+ev.events_seconds+'</div><div style="padding: 10px;margin:5px 5px 0 5px;background-color:white;"><div><h1 style="margin:0;">'+ev.events_title+'</h1><h3 style="margin: 0px;color:gray;display:table;">'+ev.events_type+' pre-created by <a style="color:#E33" href="/user/'+ev.fk_users.users_name_id+'/">'+ev.fk_users.users_name+'</a></h3></div></div><span class="likes" style="display:none;">'+ev.events_sort+'</span><div class="view view-first"><img id="e_img'+b+'" class="e_img" onload="img_loaded('+b+')" src="'+ev.events_image+'" alt="" /><div class="mask" onclick="document.getElementById(\'f'+ev.events_id+'\').submit();"> <div class="top-post" style="width:100%;text-align:right;"><div style="width:auto;display:inline-block;">'+hashtags+'<div style="clear:both;"></div></div></div> <div class="bottom-post"> <span id="'+ev.fk_users.users_id+'" class="creator" style=""><span id="'+ev.events_id+'" class="event" style=""></span></span> <form id="f'+ev.events_id+'" action="/events/draft/" method="post"><input type="text" name="title" value="'+ev.events_title+'" style="display:none;"/><input type="text" name="img_bg" value="'+ev.events_image+'" style="display:none;"/><input type="text" name="type" value="'+ev.events_type+'" style="display:none;"/><input type="text" name="dateq" value="'+dateq+'" style="display:none;" /><input type="text" name="hashtag" value="'+ev.hashtags+'" style="display:none;"/><input type="text" name="e_id" value="'+ev.events_id+'" style="display:none;"/><input type="submit" value="Draft" style="border-radius:50px;height:50px;" class="fa fa-arrow-right"/></form> </div></div></div></div>'));
		 }else{
			 items.push(content=$('<div class="item running"><div style="float:right;margin:10px 10px;color:gray;">'+ev.events_seconds+'</div><div style="padding: 10px;margin:5px 5px 0 5px;background-color:white;"><div><h1 style="margin:0;">'+ev.events_title+'</h1><h3 style="margin: 0px;color:gray;display:table;">'+ev.events_type+' pre-created by <a style="color:#E33" href="/user/'+ev.fk_users.users_name_id+'/">'+ev.fk_users.users_name+'</a></h3></div></div><span class="likes" style="display:none;">'+ev.events_sort+'</span><div class="view view-first"><img id="e_img'+b+'" class="e_img" onload="img_loaded('+b+')" src="'+ev.events_image+'" alt="" /><div class="mask" onclick="document.getElementById(\'f'+ev.events_id+'\').submit();"> <div class="top-post" style="width:100%;text-align:right;"><div style="width:auto;display:inline-block;">'+hashtags+'<div style="clear:both;"></div></div></div> <div class="bottom-post"> <span id="'+ev.fk_users.users_id+'" class="creator" style=""><span id="'+ev.events_id+'" class="event" style=""></span></span> <form id="f'+ev.events_id+'" action="/events/draft/" method="post"><input type="text" name="title" value="'+ev.events_title+'" style="display:none;"/><input type="text" name="img_bg" value="'+ev.events_image+'" style="display:none;"/><input type="text" name="type" value="'+ev.events_type+'" style="display:none;"/><input type="text" name="hashtag" value="'+ev.hashtags+'" style="display:none;"/><input type="text" name="e_id" value="'+ev.events_id+'" style="display:none;"/><input type="submit" value="Draft" style="border-radius:50px;height:50px;" class="fa fa-arrow-right"/></form> </div></div></div></div>'));
		 }
	 }else{
	 if(parseInt(ev.events_seconds)<0){
		 if(ev.fk_users.users_id==parseInt($('#uic').text())){
			 items.push(content=$('<div class="item finalized"><div style="float:right;margin:10px 10px;color:gray;">ended</div><div style="padding: 10px;margin:5px 5px 0 5px;background-color:white;"><div><h1 style="margin:0;word-wrap:break-word;">'+ev.events_title+'</h1><h3 style="margin: 0px;color:gray;display:table;">'+ev.events_type+' created by <a style="color:#E33" href="/user/'+ev.fk_users.users_name_id+'/">'+ev.fk_users.users_name+'</a></h3></div></div>  <span class="likes" style="display:none;">'+ev.events_sort+'</span><div class="view view-first"><img style="-webkit-filter:sepia(1);-webkit-filter:sepia(100%);-moz-filter: sepia(100%);-ms-filter: sepia(100%);-o-filter: sepia(100%);filter: sepia(100%);" id="e_img'+b+'" class="e_img" onload="img_loaded('+b+')" src="'+ev.events_image+'" alt="" /><a href="/'+ev.events_title_id+'/" class="mask" ></a> <div class="top-post" style="right:0;text-align:right;"><div style="width:auto;display:inline-block;">'+hashtags+'<div style="clear:both;"></div></div></div> <div class="bottom-post"><a href="/'+ev.events_title_id+'"><i class="fa fa-arrow-right"></i></a></div> <div class="ax_pk" style="position:absolute;left:10px;bottom:10px;"> <span id="'+ev.fk_users.users_id+'" class="creator" style=""><span id="'+ev.events_id+'" class="event" style=""><a style="color:white" id="delete_'+b+'" class="del_obj" href="javascript:void(0)"><img id="dl_tr" src="/images/trash.png" style="width:32px;height:32px;"/></a></span></span> </div></div></div>'));
		 }else{
			 items.push(content=$('<div class="item finalized"><div style="float:right;margin:10px 10px;color:gray;">ended</div><div style="padding: 10px;margin:5px 5px 0 5px;background-color:white;"><div><h1 style="margin:0;word-wrap:break-word;">'+ev.events_title+'</h1><h3 style="margin: 0px;color:gray;display:table;">'+ev.events_type+' created by <a style="color:#E33" href="/user/'+ev.fk_users.users_name_id+'/">'+ev.fk_users.users_name+'</a></h3></div></div>  <span class="likes" style="display:none;">'+ev.events_sort+'</span><div class="view view-first"><img style="-webkit-filter:sepia(1);-webkit-filter:sepia(100%);-moz-filter: sepia(100%);-ms-filter: sepia(100%);-o-filter: sepia(100%);filter: sepia(100%);" id="e_img'+b+'" class="e_img" onload="img_loaded('+b+')" src="'+ev.events_image+'" alt="" /><a href="/'+ev.events_title_id+'/" class="mask" ></a> <div class="top-post" style="right:0;text-align:right;"><div style="width:auto;display:inline-block;">'+hashtags+'<div style="clear:both;"></div></div></div> <div class="bottom-post"> <span id="'+ev.fk_users.users_id+'" class="creator" style=""><span id="'+ev.events_id+'" class="event" style=""></span></span> <a href="/'+ev.events_title_id+'"><i class="fa fa-arrow-right"></i></a></div></div></div>'));
		 }
	 }else{
		 c="item ";if(ev.events_fixed==1){c="stamp ";}
		 if(ev.fk_users.users_id==parseInt($('#uic').text())){
			 items.push(content=$('<div class="'+c+'running"><div style="float:right;margin:10px 10px;color:gray;"><div style="text-align: center;"><div style="display:flex;"><img src="http://oclck.com/images/heart.png" style="width:16px;height:16px;margin-bottom:-4px;"></div><span style="font-size: 10px;margin: 0;padding: 0;color: red;">'+ev.events_like+'</span></div></div><div style="padding: 10px;margin:5px 5px 0 5px;background-color:white;"><div><h1 style="margin:0;word-wrap:break-word;">'+ev.events_title+'</h1><h3 style="margin: 0px;color:gray;display:table;">'+ev.events_type+' created by <a style="color:#E33" href="/user/'+ev.fk_users.users_name_id+'/">'+ev.fk_users.users_name+'</a></h3></div></div><span class="likes" style="display:none;">'+ev.events_sort+'</span><div class="view view-first"><img id="e_img'+b+'" class="e_img" onload="img_loaded('+b+')" src="'+ev.events_image+'" alt="" /><a href="/'+ev.events_title_id+'/" class="mask"></a> <div class="top-post" style="right:0;text-align:right;"><div style="width:auto;display:inline-block;">'+hashtags+'<div style="clear:both;"></div></div></div> <div class="bottom-post"><a href="/'+ev.events_title_id+'"><i class="fa fa-arrow-right"></i></a></div> <div class="ax_pk" style="position:absolute;left:10px;bottom:10px;"><span id="'+ev.fk_users.users_id+'" class="creator" style=""><span id="'+ev.events_id+'" class="event" style=""><a style="color:white" id="delete_'+b+'" class="del_obj" href="javascript:void(0)"><img id="dl_tr" src="/images/trash.png" style="width:32px;height:32px;"/></a></span></span></div> </div></div>'));
		 }else{
			 items.push(content=$('<div class="'+c+'running"><div style="float:right;margin:10px 10px;color:gray;"><div style="text-align: center;"><div style="display:flex;"><img src="http://oclck.com/images/heart.png" style="width:16px;height:16px;margin-bottom:-4px;"></div><span style="font-size: 10px;margin: 0;padding: 0;color: red;">'+ev.events_like+'</span></div></div><div style="padding: 10px;margin:5px 5px 0 5px;background-color:white;"><div><h1 style="margin:0;word-wrap:break-word;">'+ev.events_title+'</h1><h3 style="margin: 0px;color:gray;display:table;">'+ev.events_type+' created by <a style="color:#E33" href="/user/'+ev.fk_users.users_name_id+'/">'+ev.fk_users.users_name+'</a></h3></div></div><span class="likes" style="display:none;">'+ev.events_sort+'</span><div class="view view-first"><img id="e_img'+b+'" class="e_img" onload="img_loaded('+b+')" src="'+ev.events_image+'" alt="" /><a href="/'+ev.events_title_id+'/" class="mask"></a> <div class="top-post" style="right:0;text-align:right;"><div style="width:auto;display:inline-block;">'+hashtags+'<div style="clear:both;"></div></div></div> <div class="bottom-post"> <span id="'+ev.fk_users.users_id+'" class="creator" style=""><span id="'+ev.events_id+'" class="event" style=""></span></span> <a href="/'+ev.events_title_id+'"><i class="fa fa-arrow-right"></i></a></div></div></div>'));
		 }}}b++;
  }
  if(response['n']=='0'){$('#get_more').attr('disabled','disabled').hide();bloq=true;
  }else{ $('#get_more').show();bloq=false;}
  $('#get_more_img').hide();agx++;
  }
});
}
$(document).ready(function(){
  $('.items').css('overflow','hidden');
  var winDow=$(window);get_more_items();
  $('#get_more').click(function(){get_more_items();});
  var body=$('body');body.addClass('active');
  winDow.load(function(){
	  var mainDiv=$('#container'),preloader=$('.preloader');preloader.fadeOut(550);body.delay(1000).css('background','#FAEFEF');mainDiv.delay(1000).addClass('active');
  });
  $(window).scroll(function(){
    if((!bloq&&$(window).scrollTop()+$(window).height()+3)>=$(document).height()){get_more_items();}
  });
	(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	})(window,document,'script','//www.google-analytics.com/analytics.js','ga');
	ga('create','UA-55810606-1','auto');ga('send','pageview');
	$('#searchSubmit').click(function(){window.location='/events/search/'+$('#type').text()+'/'+$('#s').val()+'/';});
});
$(function(){
  if($('#type').text()=="hot"){
	  $container.isotope({itemSelector:'.item',filter:'*',getSortData:{number:'.likes parseInt'},sortBy:'number',masonry:{},sortAscending:false,layoutMode:'masonry',animationEngine:'jquery',animationOptions:{duration:750,easing:'linear'}});
  }else{
	  $container.isotope({itemSelector:'.item',filter:'*',layoutMode:'masonry',masonry:{},animationEngine:'jquery',animationOptions:{duration:750,easing:'linear'}});
  }
  ox=$('<div id="_rx_q" class="stamp running" ><a href="/in/new/" style="display: block;background-color: rgb(80,80,80);padding: 50px; margin: 5px 5px 0 5px;text-align: center;color: white;font-weight: bold;font-size: 16px;"><img src="http://storage.googleapis.com/oclock-images/add.png" style=""><span style="display: block;">Create a new Clock</span></a></div>');
  $('.items').append(ox);$container.isotope('stamp',ox);$('.stamp').css('position','absolute').css('left','0px').css('top','0px').css('height','200px');
});