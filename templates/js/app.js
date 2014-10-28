var container = document.querySelector('.works');
var works = document.querySelectorAll('.work');
/*
for (i = 0; i < works.length; ++i) {
	var image = works[i].querySelector('img');
	
	works[i].style.backgroundImage = 'url(' + image.src + ')';
}
*/

var pckry = new Packery(container, {
  // options
  itemSelector: '.work',
  gutter:'.gutter-sizer'
});

$(works).find('a').fancybox({
	scrolling:'no',
	arrows:true
});