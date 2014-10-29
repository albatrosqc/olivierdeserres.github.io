<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        
        <title>{{ titre-site }}</title>
        
        <meta name="description" content="{{ description-sitre }}">
        
        <!-- Facebook share -->
        <meta property="og:title" content="{{ titre-site }}"/>
        <meta property="og:description" content="{{ description-sitre }}"/>
        <meta property="og:image" content="{{ share-image-site }}"/>
        
        <!-- Twitter share -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{{ titre-site }}">
        <meta name="twitter:description" content="{{ description-sitre }}">
        <meta name="twitter:image:src" content="{{ share-image-site }}">
        <meta name="twitter:domain" content="www.olivierdeserres.com">
        
        <!-- Mobile configuration -->
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-title" content="{{ titre-site }}">
        
        <!-- Stylesheet -->
        <link href="http://fonts.googleapis.com/css?family=Oswald:400,300|Armata" rel="stylesheet" type="text/css">
        <link href="css/jquery.fancybox.css" media="all" rel="stylesheet" type="text/css">
        <link href="css/global.css" media="all" rel="stylesheet" type="text/css">
    </head>
    <body>
        <div class="notes">
            <p>Background : morceau d'une toile, shape abstraite</p>
            <p>Logo : signature, handwritten</p>
            <p>Roll-over work : info</p>
            <p>Click work : overlay, close cursor, navigation sidescreen</p>
        </div>
        
        <div class="wrapper">
            <header class="header cf">
           
                <h1 class="title"><a href="index.html">Olivier<span> </span><em>De<span> </span>Serres</em></a></h1>
                
                {% include "navigation.html" %}
           
            </header> 
            <div class="content">

                {% block CONTENT %}


                {% endblock %}

            </div><!--content-->
            
        </div><!--wrapper-->

        {% block SCRIPTS %}            
        {% endblock %}
        
    </body>
</html>