{% extends "base-page.tpl" %}
{% block CONTENT_NAV %}
            <nav class="nav nav-works">
                <ul class="cf">

                    <li class="nav-title">Catégorie</li>
                    {% for elements in contentNav -%}
                        {{ elements }}
                    {% endfor %}
                </ul>
            </nav>

            <nav class="nav nav-works">
                <ul class="cf">

                    <li class="nav-title">Année</li>
                    {% for elements in yearNav -%}
                    {{ elements }}
                    {% endfor %}
                </ul>
            </nav>
{% endblock %}
{% block CONTENT %}

            <div class="works">

                <div class="gutter-sizer"></div>
                {% for elements in workList %}
                {{ elements|indent(15,false) }}
                {% endfor %}
            </div> <!-- works -->

{% endblock %}


{% block EXTRA_SCRIPTS %}
        <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
        <script src="js/packery.pkgd.min.js"></script>
        <script src="js/imagesloaded.pkgd.min.js"></script>
        <script src="js/jquery.fancybox.pack.js"></script>
{% endblock %}
            
