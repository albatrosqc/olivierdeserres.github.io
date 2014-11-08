var App = (function() {
	// App variables
	var $container = $('.works');
	var $works = $('.work');
	var $navWorks = $('.nav-works');
	
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
		
		// TODO : reset fancybox with only visible ones
	};
	
	var onWindowResize = function(ev) {
		// $container.packery('layout');
	};
	
	// Constructor
	
	var construct = (function() {
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
		
		// Setup fancybox for all the works
		$works.find('a[rel=work]').fancybox({
			scrolling:'no',
			arrows:true
		});
		
		// Click event on work navigation
		$navWorks.find('a').on('click', onNavWorksClick);
		
		// Hash change event
		$(window).on('hashchange', onHashChange).trigger('hashchange');
		$(window).on('resize', onWindowResize);
	})();
})();