{% extends "base-page.tpl" %}
{% block EXTRA_NAV %}
<nav class="nav nav-works">
    <ul class="cf">
        <li class="nav-title">
            Catégorie
        </li>
        {% for elements in contentNav %}
            {{ elements }}
        {% endfor %}
 <!--      
        <li>
            <a href="#" class="active" data-hover="Toutes">Toutes</a>
        </li>
        <li>
            <a href="#peintures" data-hover="Peintures">Peintures</a>
        </li>
        <li>
            <a href="#dessins" data-hover="Dessins">Dessins</a>
        </li>
        <li>
            <a href="#graffitis" data-hover="Graffitis">Graffitis</a>
        </li>
        <li>
            <a href="#whatever" data-hover="whatever">whatever</a>
        </li> -->

    </ul>
</nav>

<nav class="nav nav-works">
    <ul class="cf">
        <li class="nav-title">
            Année
        </li>
        {% for elements in yearNav %}
            {{ elements }}
        {% endfor %}
<!-- 
        <li>
            <a href="#" class="active" data-hover="Toutes">Toutes</a>
        </li>
        <li>
            <a href="#2014" data-hover="2014">2014</a>
        </li>
        <li>
            <a href="#2013" data-hover="2013">2013</a>
        </li>
        <li>
            <a href="#2012" data-hover="2012">2012</a>
        </li>
        <li>
            <a href="#2011" data-hover="2011">2011</a>
        </li> -->
    </ul>
</nav>
{% endblock %}
{% block CONTENT %}

<div class="works">
    <div class="gutter-sizer"></div>
    
    {% for elements in workList %}
        {{ elements }}
    {% endfor %}
    <!-- 
    <div data-category="dessins" class="work">
        <a rel="work" title="Description de la piece" href="img/works/tumblr_mztnd1orCJ1sfinydo2_500.jpg">
            <img src="img/works/tumblr_mztnd1orCJ1sfinydo2_500.jpg" />
        </a>
    </div> -->
    
</div> <!-- works -->

{% endblock %}


{% block EXTRA_SCRIPTS %}
<script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
<script src="js/packery.pkgd.min.js"></script>
<script src="js/imagesloaded.pkgd.min.js"></script>
<script src="js/jquery.fancybox.pack.js"></script>
{% endblock %}
            
