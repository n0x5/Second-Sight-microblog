# Second Sight microblog
## sqlite3 and Flask powered microblog with drag and drop upload, markdown and search.

## Azure test branch to use Azure as CDN
pip install azure-storage-blob

Fill out config.json Azure details (Connection string and Data lake root URL)

It should work right out of the box.
Required packages:

pip install flask markdown pygments

Then run python app.py

Included a test site.db with some filler content

## Features:
* Drag and drop upload images
* If upload duplicate filenames it will add "_1", "_2" etc to end of filename automatically
* Media library
* Search
* Markdown support with code highlighting
* sqlite3 pagination
* Default user is "admin" with password "password" (edit config.json to change)
* Should work by just running "python app.py".
* To delete database just delete the "database" folder and re-run "python app.py" and it will re-create the folder and db.
