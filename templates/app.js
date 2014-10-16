var works = document.querySelectorAll('.work');

for (i = 0; i < works.length; ++i) {
	var image = works[i].querySelector('img');
	
	works[i].style.backgroundImage = 'url(' + image.src + ')';
	console.log(image.src);
}