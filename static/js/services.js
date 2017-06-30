function linkify(text){return text.autoLink({target:"_blank",rel:"nofollow",class:"l_ext"});}
function del_comm(x){
$.ajax({
dataType:"json",data:{id:x},
url:'/comment/delete/',type:'post',
beforeSend:function(){$('#'+x).text('deleting...');},
success:function(r,st){$('#'+x).parent().parent().remove();},
error:function(data,errorThrown){},
statusCode:{
  200:function(){$('#'+x).parent().parent().remove();nx_co=parseInt($('#co_num').text())-1;$('#co_num').text(nx_co);if(nx_co<=0){$('#g_comm').css('background-color','rgba(255,255,255,0.3)');}}
 }
});
}
function get_comm(){
$.ajax({
cache:true,timeout:20000,async:true,
dataType:"json",data:{},
url:'/api_v2/userswritescomments/'+$('#e_id').text()+'/'+'0',type:'get',
beforeSend:function(){},
success:function(r){
 for(var idx in r['r']){
  co=r['r'][idx];
  duration=moment.duration(parseInt(co.secs)*1000);
  if($('#u_id').text()==co.u_id){$('#ccc').prepend($('<div style="background-color: rgba(255,255,255,1);padding:8px;border-bottom-color:#888;border-bottom-width:1px;border-bottom-style: solid;"><div style=""> <div style="display: inline-block;width: 30px; height: 30px; border-radius: 50%;background-image: url(\''+co.u_photo+'\');background-size: cover;margin: 4px;vertical-align:middle;float: left;"></div> <div id="cont_msg"><a style="font-weight:bold;color: #333;" href="/user/'+co.u_name_id+'/">'+co.u_name+'</a><br><label class="mess_txt" style="text-align: right;">'+linkify(co.msg)+'</label></div><div style="float: right;margin-top: 11px;"><label style="font-size: 10px;color: #888;"><span style="font-weight:bold;">Θ</span>'+duration.humanize()+'</label></div></div><div style="clear:both"></div><div style="text-align:right;"><a id="'+co.comment_id+'" class="delete" onClick="del_comm('+co.comment_id+')" href="javascript:void(0)">delete</a></div></div>'));
  }else{$('#ccc').prepend($('<div style="background-color: rgba(255,255,255,1);padding:8px;border-bottom-color:#888;border-bottom-width:1px;border-bottom-style: solid;"><div style=""> <div style="display: inline-block;width: 30px; height: 30px; border-radius: 50%;background-image: url(\''+co.u_photo+'\');background-size: cover;margin: 4px;vertical-align:middle;float: left;"></div> <div id="cont_msg"><a style="font-weight:bold;color: #333;" href="/user/'+co.u_name_id+'/">'+co.u_name+'</a><br><label class="mess_txt" style="text-align: right;">'+linkify(co.msg)+'</label></div><div style="float: right;margin-top: 11px;"><label style="font-size: 10px;color: #888;"><span style="font-weight:bold;">Θ</span>'+duration.humanize()+'</label></div></div><div style="clear:both"></div></div>'));}
  if(r['n']=='0'){}else{}
  }
},
error:function(data, errorThrown){}});
$('#co').animate({scrollTop:$('#ccc').height()},50);return;
}
function sync_comm(obj){
duration=moment.duration(parseInt(obj['secs'])*1000);
if($('#u_id').text()==obj['u_id']){$('#ccc').append($('<div style="background-color: rgba(255,255,255,1);padding:8px;border-bottom-color:#888;border-bottom-width:1px;border-bottom-style: solid;"><div style=""> <div style="display: inline-block;width: 30px; height: 30px; border-radius: 50%;background-image: url(\''+obj['u_photo']+'\');background-size: cover;margin: 4px;vertical-align:middle;float: left;"></div> <div id="cont_msg"><a style="font-weight:bold;color: #333;" href="/user/'+obj['u_name_id']+'/">'+obj['u_name']+'</a><br><label class="mess_txt" style="text-align: right;">'+linkify(obj['msg'])+'</label></div><div style="float: right;margin-top: 11px;"><label style="font-size: 10px;color: #888;"><span style="font-weight:bold;">Θ</span>'+duration.humanize()+'</label></div></div><div style="clear:both"></div><div style="text-align:right;"><a id="'+obj['comment_id']+'" class="delete" onClick="del_comm('+obj['comment_id']+')" href="javascript:void(0)">delete</a></div></div>'));
}else{$('#ccc').append($('<div style="background-color: rgba(255,255,255,1);padding:8px;border-bottom-color:#888;border-bottom-width:1px;border-bottom-style: solid;"><div style=""> <div style="display: inline-block;width: 30px; height: 30px; border-radius: 50%;background-image: url(\''+obj['u_photo']+'\');background-size: cover;margin: 4px;vertical-align:middle;float: left;"></div> <div id="cont_msg"><a style="font-weight:bold;color: #333;" href="/user/'+obj['u_name_id']+'/">'+obj['u_name']+'</a><br><label class="mess_txt" style="text-align: right;">'+linkify(obj['msg'])+'</label></div><div style="float: right;margin-top: 11px;"><label style="font-size: 10px;color: #888;"><span style="font-weight:bold;">Θ</span>'+duration.humanize()+'</label></div></div><div style="clear:both"></div></div>'));}
$('#co_num').text(parseInt($('#co_num').text())+1);
$('#co').animate({ scrollTop:$('#ccc').height()},50);
$('#g_comm').css('background-color','rgba(253,70,74,1)');
return;
}
function set_comm(){
var msg=document.getElementById("co_t").value;
$.ajax({
cache:true,timeout:20000,async:true,dataType:"json",data:{e_id:$('#e_id').text(),comm:$('#co_t').val()},url:'/events/set_co/',type:'post',
beforeSend:function(){$('#co_t').val('');},
success:function(r){
if(r['r']=='w'){
 mixpanel.track("clock commented",{"clock_id":$('#e_id').text()});
 $('#co_t').val('');
 $('#co').animate({ scrollTop: $('#ccc').height()},50);
 $('#g_comm').css('background-color','rgba(253,70,74,1)');
}else{alert('Error');}
},
error:function(x,t,m){if(t==="timeout"){}else{alert(t);}}
});
return;}
function follow(){
$.ajax({
dataType:"json",
data:{},url:'/api_v2/events/like/'+$('#e_id').text(),type:'get',beforeSend:function(){$('#xe_al').attr('src','/images/ld_ng.GIF');},
success:function(r){$('#xe_al').attr('src','/images/like.png');
if(r['r']=='f'){
	document.getElementById('fo').innerHTML=r['n'];
	document.getElementById("a_fo").style.backgroundColor="rgba(253,70,74,1)";
	mixpanel.track("clock liked",{"clock_id":$('#e_id').text()});
}else if(r['r']=='n_f'){
	document.getElementById('fo').innerHTML=r['n'];
	document.getElementById("a_fo").style.backgroundColor="rgba(255,255,255,0.3)";
}$('#a_fo').attr('disabled',false);},
error:function(data, errorThrown){}
});return;
}
function share(n_t){
$.ajax({
dataType: "json",url:'/api_v2/events/share/'+$('#e_id').text()+'/',type:'get',
beforeSend:function(){},
success:function(r){
n_s=parseInt($('#shed_num').text());
if(r['r']=='s'){
if(n_t=="t"){
  window.location.href="https://twitter.com/share?url=http://oclck.com/"+$('#e_tit_id').text()+"&text="+$('#e_tit').text()+". Follow this "+$('#crono_type').text()+" at www.oclck.com&hashtags=oclock";
}else if(n_t=="g"){
  window.location.href="https://plus.google.com/share?url=http://oclck.com/"+$('#e_tit_id').text()+"";
}else if(n_t=="fm"){
  window.location.href="https://www.facebook.com/dialog/share?app_id=407223625967266&display=popup&href=http://oclck.com/"+$('#e_tit_id').text()+"/?"+$('#unixtime_coming_0').text()+"&redirect_uri=http://oclck.com/"+$('#e_tit_id').text()+"/";
}
$('#shed_num').text(n_s+1);
//"When":"Inmediatly after creation or when viewing",
mixpanel.track("clock shared",{
"When":"when viewing",
"clock_id":$('#e_id').text()
});}},
error:function(data, errorThrown){}
});
} 
$(document).ready(function(){
  var e_sk=$('#e_sk').text();$('#dda').addClass(e_sk);$('#ddb').addClass(e_sk);$('#ddc').addClass(e_sk);$('#ddd').addClass(e_sk);
  $('.red-social').hover(
    function(){$(".opcion-social").fadeIn().css("display","block");},
    function(){$(".opcion-social").fadeOut("slow").css("display","none");}
  );$(".main").backstretch([$('#i_id').text(),"http://storage.googleapis.com/oclock-images/fallground.png"],{duration:5000,fade:850});
 $('#a_fo').click(function(){$('#a_fo').attr('disabled',true);follow();});
 if(parseInt($id("co_num").innerHTML)>0){get_comm();}
 if(parseInt($id("co_num").innerHTML)>0&&$(window).width()>640){$('#co').removeClass("off").addClass("on");}
 pubnub.subscribe({
    channel:"comm_"+document.getElementById("e_id").innerHTML,
    message:function(m){sync_comm(m);},
    connect:function(){}
 });
 $('#g_comm').click(function(){
   if($('#co').width()>0){$('#co').removeClass("on").addClass("off").animate({scrollTop:$('#ccc').height()},20);}
   else{$('#co').removeClass("off").addClass("on");}
 });

});