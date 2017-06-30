(window.$wall || window.jQuery)(function($){

	// Masonry corner stamp modifications
	$.Mason.prototype.resize = function() {
		this._getColumns();
		this._reLayout();
	};

	$.Mason.prototype._reLayout = function( callback ) {
		var freeCols = this.cols,
			cornerStampHeight = 0,
			cornerStampCols = 0;

		if ( this.options.cornerStampSelector ) {
			var $cornerStamp = this.element.find( this.options.cornerStampSelector );
			if($cornerStamp.length){
				freeCols = Math.floor((
					$cornerStamp.offset().left - 
						(this.element.offset().left +
						this.offset.x +
						parseInt($cornerStamp.css('marginLeft')))) / this.columnWidth );

				cornerStampHeight = $cornerStamp.outerHeight(true);
				cornerStampCols = Math.ceil($cornerStamp.outerWidth(true) / this.columnWidth);
			}
		}

		// reset columns
		var i = this.cols,
			il = Math.min(freeCols + cornerStampCols, this.cols);

		this.colYs = [];
		while (i--) {
			this.colYs.push( this.offset.y );
		}

		for ( i = freeCols; i < il; i++ ) {
			this.colYs[i] = this.offset.y + cornerStampHeight;
		}

		// apply layout logic to all bricks
		this.layout( this.$bricks, callback );
	};
	//End Masonry modification

	var $container = $('#masonry-container'),
		isTouch = 'ontouchstart' in window && !(/hp-tablet/gi).test(navigator.appVersion),
		itemSelector = '.item';
		
	// no main masonry, detect aside masonry
	if (!$container.length) {
		$container = $('#aside .aside-inner:first');
		itemSelector = '.col';
	}
	
	if (!$container.length){
		return;
	}
	
	// force show scrollbar
	$('#bd').css ('min-height', $(window).height() + 10);
	
	// add a blank, invisible masonry block to get the base width
	if (!$('#base-blank-item').length) {
		$('<div id="base-blank-item" class="' + itemSelector.substr(1) + '" style="height:0;visibility:hidden" />').appendTo ($container);
	}
	
	var uwsid = 0,
		lastWndWidth = 0,
		reloadMasonry = function () {
			$(document.body).addClass ('masonry-relayout');
			$container.masonry('reload', function(){
				$(document.body).removeClass ('masonry-relayout');
			});
		},
		
		updateContainerWidth = function () {
			lastWndWidth = $(window).width();
			
			var cw = $('#base-blank-item').css('width', '').width(), // wrapper width
				mw = $container.width(), // wrap width
				cols = Math.round(mw / cw), //  detect number of columns by it's container
				cw_ = Math.floor(mw / cols), // update new width
				mw_ = cols * cw_;
			
			$('#base-blank-item').width(cw_);
			
			if ($container.data('basewidth') != cw_) {
				$container.data('basewidth', cw_);
				updateBrickWidth();
			}
			
			// reload layout
			reloadMasonry();
		},
		
		updateBrickWidth = function ($bricks) {
			if (!$bricks){
				$bricks = $container.find(itemSelector);
			}
			
			var cw_ = $container.data ('basewidth');
			if (!cw_){
				return;
			}
			
			// update width for items
			$bricks.width (cw_);
			$bricks.filter('.grid-double').width(cw_ * 2);
			$bricks.filter('.grid-triple').width(cw_ * 3);
			$container.find('.corner-stamp').each(function(){
				$(this).width(Math.ceil(cw_ * ($(this).hasClass('grid-triple') ? 3 : $(this).hasClass('grid-double') ? 2 : 1)) -1);
			});
		};

	// init masonry
	$container.masonry({
		itemSelector: itemSelector,
		isResizable: false,
		cornerStampSelector: '.corner-stamp',
		columnWidth: function() { 
			return $container.data ('basewidth')? $container.data ('basewidth') : $('#base-blank-item').width() 
		}
	});

	// reload masonry when image loaded
	$container.imagesLoaded(function(){
		lastWndWidth = -1; //force to reload
		updateContainerWidth();
	});

	// create your jQuery window resize method. The clearTimeout() method prevents 
	$(window).bind('resize orientationchange', function(e){
		clearTimeout(uwsid);
		if(lastWndWidth != $(window).width() || e.isTrigger){
			uwsid = setTimeout(updateContainerWidth, 400);
		}
	});	
	
	//fix gap when custom font loaded
	$(window).load(function(){
		updateContainerWidth();
		
		/* infinitive scroll for main masonry only */
		if ($container.length && $('#page-nav').length && $('#page-next-link').length) {
			var pathObject = {
				init: function(){
					this.path = ($('#page-next-link').attr('href') || '');
					var match = this.path.match(/((page|start)[=-])(\d*)(&*)/i);
					if(match){
						this.type = match[2].toLowerCase();
						this.number = match[3];
						this.limit = this.type == 'page' ? 1 : this.number;
						this.number = this.type == 'page' ? this.number : 1;
					} else {
						this.type = 'unk';
						this.number = 2;
						this.path = this.path + (this.path.indexOf('?') == -1 ? '?' : '') + 'page=';
					}
				},
				
				join: function(page){
					if(this.type == 'unk'){
						return this.path + this.number++;
					} else{
						return this.path.replace(/((page|start)[=-])(\d*)(&*)/i, '$1' + (this.limit * this.number++) + '$4');
					}
				}
			};
			
			pathObject.init();
			$container.infinitescroll({
				navSelector  : '#page-nav',    // selector for the paged navigation 
				nextSelector : '#page-next-link',  // selector for the NEXT link (to page 2)
				itemSelector : itemSelector,     // selector for all items you'll retrieve
				extraScrollPx: 100,
				pathParse: pathObject,
				loading: {
					finishedMsg: JADef.fmsg,
					img: JADef.tplurl + 'images/loader.gif',
					msgText: JADef.ltext
				}
			}, function( newElements ) {
				// hide new items while they are loading
				var $newElems = $( newElements ).css({ opacity: 0 });
				// ensure that images load before adding to masonry layout
				$newElems.imagesLoaded(function(){
					// show elems now they're ready
					$newElems.animate({ opacity: 1 });
					// update bricks width
					updateBrickWidth ($newElems);
					
					$(document.body).addClass ('masonry-relayout');
					
					$container.masonry( 'appended', $newElems, true ); 
					// trigger scroll again
					
					setTimeout(function(){
						$(document.body).removeClass ('masonry-relayout');
						$(window).trigger('scroll');
					}, 300);
				});
				// update image caption for Joomla images
				new JCaption('img.caption');
				
				// apply lazyload image
				if(typeof lazyloadinit != 'undefined') {
					lazyloadinit();
				}
			});
		} 

		if($.browser.msie && parseFloat($.browser.version) <= 8){
			lastWndWidth = -2; //force reload
			clearTimeout(uwsid);
			uwsid = setTimeout(updateContainerWidth, 1000);
		}
	
	});
	
	// popup preview
	if (!$(document.body).hasClass ('no-preview')) {
		
		//bind event
		$container.on('click', '.item-link', function (){
			return openPopup(this.href);
		});

		if(window.JawallMenu && JawallMenu.isTablet){
			$(document.body).removeClass('hoverable');
			$container.on('mouseenter', '.item', function(){
				$(this).addClass('hover');
			}).on('mouseleave', '.item', function(){
				$(this).removeClass('hover');
			});
		}
		
		// close
		$('#popup-view').click (function (e) {
			e.stopPropagation();
			
			if(window.popupIscroll){
				window.popupIscroll.destroy();
				window.popupIscroll = null;
			}
			var jiframe = $('#popup-content').find('iframe');
			
			if(jiframe.length){
				var ifmdoc = (jiframe[0].contentDocument) ? jiframe[0].contentDocument : window.frames[jiframe[0].id].document;
				
				$(ifmdoc).find('object').remove();
				
				if(isTouch){
					$(ifmdoc).unbind('touchmove.scroll');
				}
				
				if($.browser.mozilla && jiframe.length){
					$(ifmdoc).unbind('mousewheel.iscroll');
				}
			}
			
			//fix iframe IE9
			jiframe.attr('src', 'about:blank').css('visibility', 'hidden');
			setTimeout(function(){
				$('#popup-inner').remove();
				$(document.body).removeClass ('popupview popupview-loaded');
			}, 10);
			
			return false;
		});
		
		$('#popup-close').click(function(){
			$('#popup-view').trigger('click');
		});
		
		$('#popup-content').click (function (e) {
			e.stopPropagation();
		});
		
		window.iframeWheel = function(updown){
			if(window.popupIscroll){
				window.popupIscroll._wheel(updown);
			}
		};
		
		window.iframeResize = function(updown){
			if(window.popupIscroll){
				var jiframe = $('#popup-content').find('iframe:first');
			
				if(jiframe.length){
					var height = parseFloat(jiframe.attr('height')),
						ifmdoc = (jiframe[0].contentDocument) ? jiframe[0].contentDocument : window.frames[jiframe[0].id].document,
						scroll = window.popupIscroll.y,
						nheight = 0;

					//try
					jiframe.attr('height', '');
					window.popupIscroll.scrollTo(0, 0);
					nheight = $(ifmdoc).height();
					
					//restore
					jiframe.attr('height', nheight);

					if(height != nheight){
						window.popupIscroll.scrollTo(0, Math.max(scroll, -nheight + $('#popup-content').height()));
						window.popupIscroll.refresh();
					} else {
						window.popupIscroll.scrollTo(0, scroll);
					}
				}
			}
		};
		
		//function check iframe popup load to resize
		function ifmOnload(){
			if(this.src == 'about:blank'){
				return;
			}
			
			$(document.body).addClass ('popupview-loaded');
			
			var doc = this.contentDocument ? this.contentDocument : window.frames[this.id].document,
				ifm = this;
			
			if (doc.readyState && doc.readyState != 'complete'){
			   return;
			}

			if (doc.body && doc.body.innerHTML == "false"){
				return;
			}
			
			this.height = $(doc).height();
			
			if(window.popupIscroll){
				window.popupIscroll.destroy();
			}

			window.popupIscroll = new iScroll('popup-inner', {vScrollbar: true, hScrollbar: false, scrollbarClass: 'popupTracker', useTransform: false, scroller: (isTouch ? doc.getElementById('container') : null) });
			
			if(isTouch){
				$(doc).bind('touchmove.scroll', function(e){
					e.preventDefault();
				});
			} 

			if($.browser.opera || $.browser.mozilla || ($.browser.msie && $.browser.version >= 9)){
				$(doc).bind('mousewheel.iscroll', $.proxy(window.popupIscroll._wheel, window.popupIscroll));
			} else if($.browser.msie && $.browser.version < 9){
				
				var script = doc.createElement('script');
				script.src = JADef.tplurl + 'js/scrollevent.js';
				doc.body.appendChild(script);
			}
			
			$(doc.body).find('a').each(function(){
				if($(this).attr('target') != '_blank'){
					$(this).attr('target', '_parent');
				}
			});
		};
		
		function openPopup(url) {
			// check if window is smaller than popup width - 600px
			if ($(document.body).width() < 700){
				return true;
			}
			
			// add div to show content
			if (!$('#popup-view').length) {
				$('<div id="popup-view"><div id="popup-content"><a id="popup-close" href="javascript:;" class="btn-close"></a></div>').appendTo (document.body);				
			}
			
			if($(document.body).hasClass ('popupview')){
				return false;
			}
			
			// add popup class to body
			$(document.body).addClass ('popupview');				
			// get content from ajax
			
			var urlparts = url.split('#');
			if(urlparts[0].indexOf('?') == -1){
				urlparts[0] += '?tmpl=component';
			} else {
				urlparts[0] += '&tmpl=component';
			}
			
			url = urlparts.join('#');
			
			$('<div id="popup-inner" />')
				.html ($('<iframe id="popupIFrame" src="' + url + '" width="638" scrolling="no" frameborder="0" />')
					.bind('load', ifmOnload))
				.appendTo ('#popup-content');
			
			return false;
		};
	}	
});