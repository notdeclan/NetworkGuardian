# Network Guardian #

## Folder / File Documentation ##
* protoyping/
    - Used to store prototypes for the software such as features that may be implemented later, or to help with 
    development. All code in here should be documented by the author.
* src/
    * /network guardian
        * /blueprints
            - Used to store Flask Routing Blueprints (see https://flask.palletsprojects.com/en/1.0.x/blueprints/ for more information about blueprinting)
                * /api.py - Blueprint for API requests
                * /panel.py - Blueprint for web page requests to display the gui
        * /static
            - Used to store static elements for the web application such as CSS and Javascript
                * /css
                    - Used to store CSS files
                * /js
                    - Used to store JS files
        * /templates
            - Used to store HTML templates used in the flask application for the GUI
                * /layouts
                * /pages