# Second Sight microblog
## sqlite3 and Flask powered microblog with drag and drop upload, markdown and search.

It should work right out of the box.
Required packages:

pip install flask markdown pygments

Then run python app.py

Included a test site.db with some filler content

## Features:
* Drag and drop upload images
* Media library
* Search
* Markdown support with code highlighting
* sqlite3 pagination
* Default user is "admin" with password "password" (edit config.json to change)
* Should work by just running "python app.py".
* To delete database just delete the "database" folder and re-run "python app.py" and it will re-create the folder and db.
