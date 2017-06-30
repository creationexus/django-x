var nrx=0; 
function syot(){
	$('#ortz').hide();
	$.ajax({
		cache:true,timeout:20000,async:true,dataType:"json",
		data:{language:'en_us'},
		url:'/api_v2/activities/',
		type:'post',
		beforeSend:function(){$('#lst_ntf').empty().append($('<div id="ld_nf" style="text-align:center;margin-top:10px;"><img src="/images/ld_nf.GIF"/></div>'));},
		success:function(r){
			$('#ld_nf').hide();
			 for(var idx in r['r']){
				nf=r['r'][idx];
				if(nf.users_image==null&&nf.users_name==null){
					$('#lst_ntf').append($('<li><a href="/'+nf.events_title_id+'" style="margin-left:5px;width:220px;"><img src="'+nf.users_image+'" style="width:60px;height:60px;margin-right:4px;vertical-align:top;"/><span style="font-size:12px;display:inline-block;width:150px;">'+nf.events_type+' '+nf.language_value+' '+'</span></a></li>'));
				}else{
					if(nf.activities_read==0){
						$('#lst_ntf').append($('<li style="background-color:#EA9;"><a href="/'+nf.events_title_id+'" style="margin-left:5px;width:220px;"><img src="'+nf.users_image+'" style="width:60px;height:60px;margin-right:4px;vertical-align:top;"/><span style="font-size:12px;display:inline-block;width:150px;"><b>'+nf.users_name+'</b> '+nf.language_value+' '+nf.events_type+'</span></a></li>'));
					}else{
						$('#lst_ntf').append($('<li><a href="/'+nf.events_title_id+'" style="margin-left:5px;width:220px;"><img src="'+nf.users_image+'" style="width:60px;height:60px;margin-right:4px;vertical-align:top;"/><span style="font-size:12px;display:inline-block;width:150px;"><b>'+nf.users_name+'</b> '+nf.language_value+' '+nf.events_type+'</span></a></li>'));
					}
				}
				if(r['n']=='0'){}else{}
			}
			if(nrx>0){rnit();}
		},  
		error:function(x,t,m){if(t==="timeout"){}else{alert(t);}}
	});
}
function rnit(){
	$.ajax({
		cache:false,timeout:20000,async:true,dataType:"json",
		data:{},
		url:'/api_v2/events/read/',
		type:'get',
		beforeSend:function(){},
		success:function(r){
			$('#ortz').remove();nrx=0;
		},  
		error:function(x,t,m){$('#ortz').show();if(t==="timeout"){}else{alert(t);}}
	});
}
function sync_notif(d){
	nrx++;
	if(nrx==1){
		$('#i_notif').before($('<span id="ortz" style="background-color: rgba(150,232,65,0.9);border-radius:50%;min-width: 15px;height: 15px;float: left;position: absolute;text-align: center;color: black;font-weight: bold;margin-left: 10px;padding: 4px;font-size: 10px;">'+nrx+'</span>'));
	}else{
		$('#ortz').text(nrx);
	}
}
$(document).ready(function(){
 pubnub.subscribe({
    channel:"userch_"+$('#uic').text(),
    message:function(d){sync_notif(d);},
    connect:function(){}
 });
 $.ajax({
		cache:true,timeout:20000,async:true,dataType:"json",
		data:{language:'en_us'},
		url:'/api_v2/activities/',
		type:'post',
		beforeSend:function(){$('#lst_ntf').empty();},
		success:function(r){
			for(var idx in r['r']){
				nf=r['r'][idx];
				if(nf.activities_read==0){nrx++}if(r['n']=='0'){}else{}
			}
			if(nrx>0){$('#i_notif').before($('<span id="ortz" style="background-color:rgba(150,232,65,0.9);border-radius:50%;min-width: 15px;height: 15px;float: left;position: absolute;text-align: center;color: black;font-weight: bold;margin-left: 10px;padding: 4px;font-size: 10px;">'+nrx+'</span>'));}
		},  
		error:function(x,t,m){if(t==="timeout"){}else{alert(t);}}
  });
});