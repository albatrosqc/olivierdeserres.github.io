var $container = $('.works');
var $works = $('.work');

$container.packery({
  // options
  itemSelector: '.work',
  gutter:'.gutter-sizer',
  transitionDuration:'0s'
});

imagesLoaded($container, function(ev) {
	$container.packery('layout');
});

$works.find('a[rel=work]').fancybox({
	scrolling:'no',
	arrows:true
});

$('.nav-works a').click(function(ev) {
	var $link = $(this);
	
	$link.closest('.nav-works').find('a').removeClass('active');
	$link.addClass('active');
	
	ev.preventDefault();
	
	var $selectors = $('.nav-works a.active');
	var params = {};
	
	$selectors.each(function() {
		params[$(this).closest('.nav-works').data('type')] = $(this).attr('href').replace(/#/, '');
	});
	
	// TODO : disable links when no results
	
	window.location.hash = $.param(params);
});

window.onhashchange = function(ev) {
	var params = $.deparam(window.location.hash.replace(/#/, ''));
	
	var filters = [];
	
	$.each(params, function(key, value) {
		$('.nav-works[data-type="' + key + '"] a').removeClass('active').filter('[href="#'  + value + '"]').addClass('active');
		
		if (value) {
			filters.push('[data-' + key +'*="' + value + '"]');
		}
	});
	
	if (filters.length) {
		$works.hide();
		$works.filter(filters.join('')).show();
	} else {
		$works.show();
	}
	
	$container.packery('layout');
};

window.onhashchange();