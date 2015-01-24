var App = (function() {
	// App variables
	var $container = null;
	var $works = null;
	var $navWorks = null;
	
	var reindexSlides = function() {
		$works.filter(':visible').each(function(index) {
			var $work = $(this);
			var $trigger = $(this).find('a');
				$trigger.data('index', index);
		});
	};
	
	var setupSlides = function() {		
		$works.find('a').on('click', function(ev) {
			ev.preventDefault();
			
			var items = [];
			var options =  {
				index:$(this).data('index')
			};
			
			$works.filter(':visible').each(function(index) {
				var $trigger = $(this).find('a');
				
				items.push({
					src:$trigger.attr('href'),
					w:$trigger.data('width') || 500,
					h:$trigger.data('height') || 500,
					title:$trigger.attr('title')
				});
			});
			
			var gallery = new PhotoSwipe(document.querySelectorAll('.pswp')[0], PhotoSwipeUI_Default, items, options);
				gallery.init();
		});
	};
	
	// Navigation event
	
	var onNavWorksClick = function(ev) {
		// Prevent link from firing, hash will be changed further down
		ev.preventDefault();
		
		var $link = $(this);
		
		// Apply active class on link
		$link.closest('.nav-works').find('a').removeClass('active');
		$link.addClass('active');
		
		// TODO : disable links when no results
		
		// Prepare parameters
		var $selectors = $navWorks.find('a.active');
		var params = {};
		
		// Loop through active links and build parameters
		$selectors.each(function() {
			params[$(this).closest('.nav-works').data('type')] = $(this).attr('href').replace(/#/, '');
		});
		
		// Store paramaters in the hash
		window.location.hash = $.param(params);
	};
	
	// Hash change event
	
	var onHashChange = function(ev) {
		// Fetch parameters from hash
		var params = $.deparam(window.location.hash.replace(/#/, ''));
		
		// Setup filters
		var filters = [];
		
		// Loop through parameters
		$.each(params, function(key, value) {
			// Activate link in navigation
			$('.nav-works[data-type="' + key + '"] a').removeClass('active').filter('[href="#'  + value + '"]').addClass('active');
			
			// Add filter if value is not null
			if (value) {
				filters.push('[data-' + key +'*="' + value + '"]');
			}
		});
		
		if (filters.length) {
			// If we have filters, hide all works and show only relevant ones
			$works.hide();
			$works.filter(filters.join('')).show();
		} else {
			// Show all works if we have no filters
			$works.show();
		}
		
		// Repack all works in a new layout
		$container.packery('layout');
		
		// reset photoswipe with only visible ones
		reindexSlides();
	};
	
	var onWindowResize = function(ev) {
		// $container.packery('layout');
	};
	
	var onPageReady = function(ev) {
		$container = $('.works');
		$works = $('.work');
		$navWorks = $('.nav-works');
		
		if ($container.length) {
			// Layout all the works using packery
			$container.packery({
				itemSelector: '.work', // Item selector
				gutter:'.gutter-sizer', // Percent-based gutter
				transitionDuration:'0s' // No transition when resizing
			});

			// When all images are loaded, apply new layout to make sure everything looks good
			imagesLoaded($container, function(ev) {
				$container.packery('layout');
			});

			// Setup photoswipe
			reindexSlides();
			setupSlides();

			// Click event on work navigation
			$navWorks.find('a').on('click', onNavWorksClick);
		}
	};
	
	// Constructor
	
	var construct = (function() {
		$(document).pjax('a', '.content', {
			fragment:'.content'
		});

		$('.nav-header a').on('click', function(ev) {
			$(this).closest('.nav-header').find('a').removeClass('active');
			$(this).addClass('active');
		});
		
		$(document).on('pjax:complete', onPageReady).trigger('pjax:complete');
		
		$('.toggle-nav').on('click', function(ev) {
			ev.preventDefault();
			
			$('.nav.nav-header').toggleClass('nav-opened');
		});
		
		// Hash change event
		$(window).on('hashchange', onHashChange).trigger('hashchange');
		$(window).on('resize', onWindowResize);
	})();
})();