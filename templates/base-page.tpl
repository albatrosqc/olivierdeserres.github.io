<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        
        <title>{{ titre_site }}</title>
        
        <meta name="description" content="{{ description_site }}">
        
        <link rel="shortcut icon" type="image/x-icon" href="img/favicon.ico">
        
        <!-- Facebook share -->
        <meta property="og:title" content="{{ titre_site }}"/>
        <meta property="og:description" content="{{ description_site }}"/>
        <meta property="og:image" content="img/{{ share_image }}"/>
        
        <!-- Twitter share -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{{ titre_site }}">
        <meta name="twitter:description" content="{{ description_site }}">
        <meta name="twitter:image:src" content="img/{{ share_image }}">
        <meta name="twitter:domain" content="www.olivierdeserres.com">
        
        <!-- Mobile configuration -->
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-title" content="{{ titre_site }}">
        
        <!-- Stylesheet -->
        <link href="http://fonts.googleapis.com/css?family=Oswald:400,300|Armata" rel="stylesheet" type="text/css">
	    <link href="css/photoswipe.css" media="all" rel="stylesheet" type="text/css">
	  	<link href="css/default-skin/default-skin.css" media="all" rel="stylesheet" type="text/css">
        <link href="css/global.css" media="all" rel="stylesheet" type="text/css">
        <link href="css/custom.css" media="all" rel="stylesheet" type="text/css">
    </head>
    <body>
        <div class="wrapper">
            <header class="header cf">
                <h1 class="title"><a href="index.html">Olivier<span> </span><em>De<span> </span>Serres</em></a></h1>
        
                <nav class="nav nav-header">
                    <ul class="cf">

                        {% for elements in headerNav -%}
                            {{ elements }}
                        {% endfor %}
                    </ul>
                </nav>        
            </header>
            
            <div class="content">
                    {% block CONTENT_NAV %}
                    {% endblock %}

                    {% block CONTENT %}
                    {% endblock %}
            </div><!--content-->
        </div><!--wrapper-->
        
        {% block EXTRA_SCRIPTS %}
        {% endblock %}
        <script src="js/app.js"></script>
    </body>
</html>