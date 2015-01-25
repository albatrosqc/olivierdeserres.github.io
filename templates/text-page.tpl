{% extends "base-page.tpl" %}
{% block CONTENT %}
    <img src="img/{{ image_url }}" style="width:33%; float:left; padding:0 24px 100px 0;" />
    
    <h2>{{ text_section_title }}</h2>
    
    {% for line in text_content %}
        <p>{{ line }}</p>
    {% endfor %}
{% endblock CONTENT %}