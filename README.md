🧿 Blini is a minimal site builder for essays and exhibits. When the application is running, users can add and edit content that is saved directly to html files in the `site` directory. The site is self-contained with no external dependencies.  The site can be opened locally in the browser or deployed to Github pages, Netlify and other services. 

in progress ...
For the moment, to try it out, clone this repository, create a Python 3 virtualenv, pip install requirements.  You can change the site settings in [/site/site.yaml](https://github.com/apjanco/blini/blob/master/site/site.yaml).  To run the application `uvicorn main:app --reload`.  More documentation to come!

## Also note there is a `dev` variable in site.yaml  When it's false, the site behaves like a published static site.  When it's true, content can be added or edited. 
