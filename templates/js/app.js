var $container = document.querySelector('.works');
var $works = $('.work');

var pckry = new Packery($container, {
  // options
  itemSelector: '.work',
  gutter:'.gutter-sizer',
  transitionDuration:'0s'
});

$works.find('a[rel=work]').fancybox({
	scrolling:'no',
	arrows:true
});

window.onhashchange = function(ev) {
	var category = window.location.hash.replace(/#/, '');
	
	if (category) {
		$works.hide();
		$works.filter('[data-category*="' + category + '"]').show();
	} else {
		$works.show();
	}
	
	pckry.layout();
	
	$('.nav-works a').removeClass('active').filter('[href="#'  + category + '"]').addClass('active');
};

window.onhashchange();