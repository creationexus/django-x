/*jshint jquery:true */
/*global $:true */

var $ = jQuery.noConflict();

$(document).ready(function($) {
	"use strict";

	
	/*-------------------------------------------------*/
	/* =  portfolio isotope
	/*-------------------------------------------------*/

	var winDow = $(window);
	// Needed variables
	var $container=$('.portfolio-box, .blog-box');
	var $filter=$('.filter');

	try{
		$container.imagesLoaded( function(){
			$container.show();
			$container.isotope({
				filter:'*',
				layoutMode:'masonry',
				animationOptions:{
					duration:750,
					easing:'linear'
				}
			});
		});
	} catch(err) {
	}

	winDow.bind('resize', function(){
		var selector = $filter.find('a.active').attr('data-filter');

		try {
			$container.isotope({ 
				filter	: selector,
				animationOptions: {
					duration: 750,
					easing	: 'linear',
					queue	: false,
				}
			});
		} catch(err) {
		}
		return false;
	});
	
	// Isotope Filter 
	$filter.find('a').click(function(){
		var selector = $(this).attr('data-filter');

		try {
			$container.isotope({ 
				filter	: selector,
				animationOptions: {
					duration: 750,
					easing	: 'linear',
					queue	: false,
				}
			});
		} catch(err) {

		}
		return false;
	});


	var filterItemA	= $('.filter li a');

	filterItemA.on('click', function(){
		var $this = $(this);
		if ( !$this.hasClass('active')) {
			filterItemA.removeClass('active');
			$this.addClass('active');
		}
	});

	/*-------------------------------------------------*/
	/* =  preloader function
	/*-------------------------------------------------*/
	var body = $('body');
	body.addClass('active');

	winDow.load( function(){
		var mainDiv = $('#container'),
			preloader = $('.preloader');

			preloader.fadeOut(400, function(){
				mainDiv.delay(400).addClass('active');
				body.delay(400).css('background', '#34495E');
			});
	});

	/*-------------------------------------------------*/
	/* =  header height fix
	/*-------------------------------------------------*/
	var content = $('#content');
	content.imagesLoaded( function(){
		var bodyHeight = $(window).outerHeight(),
		containerHeight = $('.inner-content').outerHeight(),
		headerHeight = $('header');

		if( bodyHeight > containerHeight ) {
			headerHeight.css('height',bodyHeight);
		} else {
			headerHeight.css('height',containerHeight);	
		}
	});

	winDow.bind('resize', function(){
		var bodyHeight = $(window).outerHeight(),
		containerHeight = $('.inner-content').outerHeight(),
		headerHeight = $('header');

		if( bodyHeight > containerHeight ) {
			headerHeight.css('height',bodyHeight);
		} else {
			headerHeight.css('height',containerHeight);	
		}
	});

	/* ---------------------------------------------------------------------- */
	/*	nice scroll
	/* ---------------------------------------------------------------------- */

	try {
		var HTMLcontainer = $("html");
		HTMLcontainer.niceScroll({
			cursorcolor:"#22313F"
		});
	} catch(err) {

	}

	/*-------------------------------------------------*/
	/* = skills animate
	/*-------------------------------------------------*/

	try {
		var animateElement = $(".meter > span");
		animateElement.each(function() {
			$(this)
				.data("origWidth", $(this).width())
				.width(0)
				.animate({
					width: $(this).data("origWidth")
				}, 1200);
		});
	} catch(err) {

	}

});