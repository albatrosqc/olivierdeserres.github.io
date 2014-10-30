<div data-category="{{ category_name }}, {{ image_year }}" class="work">
     <a rel="work" title="{{ image_title }} ({{ image_year }}){% if image_spec is defined %}: {{ image_spec }}{% endif %}" href="{{ image_url }}">
         <img src="{{ image_thumbnail_url }}" title ="{{ image_title }}" />
     </a>
 </div>