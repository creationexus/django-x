var velocity=parseInt(document.getElementById("crono_velocity").innerHTML,10);
var op=document.getElementById("crono_type").innerHTML;
var count=Number($('#unixtime_coming_0').text()),counter=0,days=0,hours=0,minutes=0,seconds=0;
function timer(){
	if(op=='timer'){count=count+1;}else{count=count-1;}
	if(count>=0){
		days=Math.floor(count/86400);hours=Math.floor(count/3600)%24;minutes=Math.floor(count/60)%60;seconds=count%60;
		$id("d_day").innerHTML=days;
		$id("d_hour").innerHTML=hours;
		$id("d_minute").innerHTML=minutes;
		$id("d_second").innerHTML=seconds;
	}else{if($('#e_aft').text()!=""){$("#timer_coming_0").hide();$('#pp_o').html($('<a id="msg_sp" href="javascript:void(0)"><img id="rd_x" src="https://storage.googleapis.com/oclock-images/read-wishes.png"/></a>'));$('#msg_sp').click(function(){$('#e_tit').hide();$('.hy_oq').hide();if($(window).height()<=480){$('#pp_o').css('overflow','auto').css('height','100px');} $('#pp_o').html($('#e_aft').text());});}else if($('#e_id').text()=='8661'){$("#timer_coming_0").html('<a href="https://play.google.com/store/apps/details?id=com.ibex.oclckapp">Download</a>');}else{$("#timer_coming_0").text("Finalized");}clearInterval(counter);}
	if(days==0){
		$id("ddd").style.display="none";
		if(hours==0){
			$id("ddc").style.display="none";
			if(minutes==0){
				$id("ddb").style.display="none";
				if(seconds==0){
					$id("dda").style.display="none";return;
				}
			}
		}
	}
	if(seconds>0){
		$id("dda").style.display="block";
		if(minutes>0){
			$id("ddb").style.display="block";
			if(hours>0){
				$id("ddc").style.display="block";
				if(days>0){$id("ddd").style.display="block";}
			}
		}
	}
}
$(document).ready(function(){counter=setInterval(timer,velocity);});