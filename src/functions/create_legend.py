from branca.element import Template, MacroElement
from folium.plugins import Fullscreen

def run(m, map_title, legend_name, html_markers, title_only = False, ):
    """
    Renvoie une cartographie Folium agrémentée d'un titre et d'une légende

    Paramètres
    -------
    m : folium Map
    map_title : str | titre à afficher sur la cartographie
    legend_name : str | libellé de la légende
    html_markers : str | code CSS correspondant au contenu à afficher dans la légende
    
    Retourne
    -------
    m : folium Map
    """ 

    head = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Map</title>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
    
    <script>
    $(function() {
        $("#maplegend").draggable({
            start: function (event, ui) {
                $(this).css('z-index', 1001);
            },
            stop: function (event, ui) {
                $(this).css('z-index', 9999);
            }
        });
    });

    // Adjust legend position when entering or exiting fullscreen mode
    function handleFullscreenChange() {
        var isFullscreen = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement;
        var legend = document.getElementById('maplegend');
        if (isFullscreen) {
            legend.style.position = 'fixed';  // Switch to fixed positioning in fullscreen mode
            legend.style.left = '20px';
            legend.style.bottom = '20px';
        } else {
            legend.style.position = 'absolute';  // Revert to absolute positioning
        }
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);

    </script>
    </head>"""

    if title_only == True:
        body = f"""
        <body>
            <div id='maptitle' class='maptitle'>{map_title}</div>   
            <div id='mapwatermark' class='mapwatermark'>Cette carte a été réalisée grâce à l'application <a href='https://sportoo.streamlit.app/' target='_blank'>Sportoo</a></div>
        </body>
        </html>
        """        

    else:
        body = f"""
        <body>
            <div id='maptitle' class='maptitle'>{map_title}</div>
            <div id='mapwatermark' class='mapwatermark'>Cette carte a été réalisée grâce à l'application <a href='https://sportoo.streamlit.app/' target='_blank'>Sportoo</a></div>
            <div id='maplegend' class='maplegend' 
                style='position:absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
                border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 20px;'>
                
                <div class='legend-title'>{legend_name}</div>
                <div class='legend-scale'>
                    <ul class='legend-labels'>
                        {html_markers}
                    </ul>
                </div>
            </div>            
        </body>
        </html>
        """


    css = """
    <style type='text/css'>
    .maptitle {
        position:absolute;
        z-index:9999; 
        border:2px solid grey; 
        background-color:rgba(255, 255, 255, 0.8);
        border-radius:6px; 
        padding: 10px; 
        font-size:14px; 
        left: 50px; 
        top: 10px;
        }
    .mapwatermark {
        position:absolute;
        z-index:9999; 
        background-color:rgba(255, 255, 255, 0.8);
        border-radius:6px; 
        padding: 10px; 
        font-size:14px; 
        right: 10px; 
        bottom: 20px;
        }
    .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
    .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
    .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
    .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 16px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
    #circle{
        border-radius: 50%;
        float: left;
        height: 16px;
        width: 16px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
    .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
    .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %}"""
    
    template = head + body + css
    macro = MacroElement()
    macro._template = Template(template)

    m.add_child(macro)

    return m