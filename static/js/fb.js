$('#sh_fb').click(function(){
	share("fm");
});

function oxs(){
if($(window).height()<=480||$.browser.mobile){
	share("fm");
}else{
	/*FB.ui({
	    method:'share',
	    href:document.URL,
	  	},function(response){
	    if (response && !response.error_code){
	      share("f");
	    }else{
	    }
	});*/
	window.fbAsyncInit=function(){
	FB.init({appId:'407223625967266',xfbml:true,version:'v2.1'});
	FB.ui({
		 method:'feed',
		 name:$('#e_tit').text(),
		 link:document.URL,
		 picture:$('#i_id').text(),
		 caption:'O’Clock Inc.',
		 description:$('#e_des').text(),
		 message:$('#e_tit').text(),
		 display:'popup'
		 },function(response){
		  if(response&&response.post_id){
		   share("f");
		 } else {
		   //console.log('Post was not published.');
		 }
	});
	};
	(function(d,s,id){
	 var js, fjs = d.getElementsByTagName(s)[0];
	 if (d.getElementById(id)) {return;}
	 js = d.createElement(s); js.id = id;
	 js.src = "//connect.facebook.net/en_US/sdk.js";
	 fjs.parentNode.insertBefore(js, fjs);
	}(document,'script','facebook-jssdk'));
}
}