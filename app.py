from flask import Flask
from flask import current_app
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from flask import make_response
from flask import jsonify
from werkzeug.utils import secure_filename
from pygments import highlight
from pygments.lexers import PythonLexer
import json
import os
import sqlite3
import markdown
import datetime
import time
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

posts_per_page = 7
date_format = '%a %d, %Y'
site_title = 'Second sight microblog'
extension_list = ['codehilite', 'fenced_code', 'extra', 'meta', 'sane_lists', 'toc', 'wikilinks']

# edit config.json
app.config.from_file('config.json', load=json.load)
db_path = os.path.join(app.root_path, 'database')

if not os.path.exists(db_path):
    os.makedirs(db_path)
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql = 'create table if not exists blog (body text, post_type text, date int, post_id INTEGER PRIMARY KEY AUTOINCREMENT)'
    conn.execute(sql)
    conn.close()


@app.route("/search/", methods=['GET', 'POST'])
def search(search=None):
    if request.method == 'POST':
        conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
        search = request.form['search']
        sql = 'select body, post_id, date, substr(body, instr(lower(body), "{}")-20, 75) from blog where body like ? order by date' .format(search.lower())
        results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="200"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3], item[2]) for item in conn.execute(sql, ('%'+search+'%',))]
        count = len(results)
        conn.close()
    return render_template('search.html', results=results, count=count, search=search)

@app.route("/")
def hello():
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql = 'select * from blog order by date desc limit {}' .format(posts_per_page)
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3], item[2]) for item in conn.execute(sql)]
    if len(results) != 0:
        highest_id = results[0][-1]
        lowest_id = results[-1][-1]
        sql_lower = 'select * from blog where date < ? order by date'
        results_lower = [item for item in conn.execute(sql_lower, (lowest_id,))]
        if len(results_lower) != 0:
            lower_posts = '<a href="/older/{}">Older entries</a>' .format(lowest_id)
        else:
            lower_posts = ''
        sql_higher = 'select * from blog where date > ? order by date'
        results_higher = [item for item in conn.execute(sql_higher, (highest_id,))]
        if len(results_higher) != 0:
            higher_posts = '<a href="/newer/{}">Newer entries</a>' .format(highest_id)
        else:
            higher_posts = ''
        sql2 = 'select date from blog'
        results2 = [item for item in conn.execute(sql2)]
        count = len(results2)
    else:
        results = 'no posts'
        count = 'no posts'
        higher_posts = 'none'
        lower_posts = 'none'
    return render_template('index.html', results=results, site_title=site_title, user=current_app.config['USERNAME'], count=count, higher_posts=higher_posts, lower_posts=lower_posts)

@app.route("/older/<after>")
def older(after=None):
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql_lower = 'select * from blog where date < ? order by date desc limit {}' .format(posts_per_page)
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3], item[2]) for item in conn.execute(sql_lower, (after,))]
    highest_id = results[0][-1]
    lowest_id = results[-1][-1]
    sql_lower = 'select * from blog where date < ? order by date'
    results_lower = [item for item in conn.execute(sql_lower, (lowest_id,))]
    if len(results_lower) != 0:
        lower_posts = '<a href="/older/{}">Older entries</a>' .format(lowest_id)
    else:
        lower_posts = ''
    sql_higher = 'select * from blog where date > ? order by date'
    results_higher = [item for item in conn.execute(sql_higher, (highest_id,))]
    if len(results_higher) != 0:
        higher_posts = '<a href="/newer/{}">Newer entries</a>' .format(highest_id)
    else:
        higher_posts = ''
    sql2 = 'select date from blog'
    results2 = [item for item in conn.execute(sql2)]
    count = len(results2)
    return render_template('index.html', results=results, site_title=site_title, user=current_app.config['USERNAME'], count=count, higher_posts=higher_posts, lower_posts=lower_posts)

@app.route("/newer/<after>")
def newer(after=None):
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql_higher2 = 'select * from blog where date > ? order by date limit {}' .format(posts_per_page)
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3], item[2]) for item in conn.execute(sql_higher2, (after,))]
    results.reverse()
    highest_id = results[0][-1]
    lowest_id = results[-1][-1]
    sql_lower = 'select * from blog where date < ? order by date'
    results_lower = [item for item in conn.execute(sql_lower, (lowest_id,))]
    if len(results_lower) != 0:
        lower_posts = '<a href="/older/{}">Older entries</a>' .format(lowest_id)
    else:
        lower_posts = ''
    sql_higher = 'select * from blog where date > ? order by date'
    results_higher = [item for item in conn.execute(sql_higher, (highest_id,))]
    if len(results_higher) != 0:
        higher_posts = '<a href="/newer/{}">Newer entries</a>' .format(highest_id)
    else:
        higher_posts = ''
    sql2 = 'select date from blog'
    results2 = [item for item in conn.execute(sql2)]
    count = len(results2)
    return render_template('index.html', results=results, site_title=site_title, user=current_app.config['USERNAME'], count=count, higher_posts=higher_posts, lower_posts=lower_posts)

@app.route('/new', methods=['GET', 'POST'])
def blog_new():
    if not session.get('logged_in'):
        return 'access denied'
    if request.method == 'GET':
        upload = os.path.join(app.root_path, 'static', 'uploads')
        list_img = []
        list_img2 = []
        list_img3 = []
        try:
            for subdir, dirs, files in os.walk(upload):
                for fn in files:
                    list_img.append(os.path.join(subdir, fn))
            list_img2 = sorted(list_img, key=os.path.getmtime)
            for item in list_img2:
                fname = item.split(os.path.sep)
                subdir1 = fname[-2]+'/'+fname[-1]
                list_img3.append(subdir1)
            list_img4 = list_img3[-4:]
            list_img4.reverse()

        except Exception:
            list_img2 = []
        if 'Hx-Trigger' in request.headers:
            return render_template('blog_htmx.html', list_img=list_img4)
        return render_template('blog.html', site_title=site_title, list_img=list_img4, user=current_app.config['USERNAME'])

    if request.method == 'POST':
        content = request.form['body']
        date = int(time.time())
        conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
        sql = 'insert into blog (body, date) values (?,?)'
        conn.execute(sql, (content, date))
        conn.commit()
        conn.close()
        return redirect('/')

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def blog_edit(post_id=None):
    if not session.get('logged_in'):
        return 'access denied'
    if request.method == 'GET':
        conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
        sql = 'select * from blog where post_id == {}' .format(post_id)
        results = [item for item in conn.execute(sql)]
        body = results[0][0]
        upload = os.path.join(app.root_path, 'static', 'uploads')
        list_img = []
        list_img2 = []
        list_img3 = []
        try:
            for subdir, dirs, files in os.walk(upload):
                for fn in files:
                    list_img.append(os.path.join(subdir, fn))
            list_img2 = sorted(list_img, key=os.path.getmtime)
            for item in list_img2:
                fname = item.split(os.path.sep)
                subdir1 = fname[-2]+'/'+fname[-1]
                list_img3.append(subdir1)
            list_img4 = list_img3[-4:]
            list_img4.reverse()

        except Exception:
            list_img2 = []
        if 'Hx-Trigger' in request.headers:
            return render_template('blog_htmx.html', list_img=list_img4)
        return render_template('blog_edit.html', site_title=site_title, list_img=list_img4, user=current_app.config['USERNAME'], post_text=body, post_id=post_id)

    if request.method == 'POST':
        content = request.form['body']
        date = int(time.time())
        conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
        sql = 'update blog set body = ? where post_id = ?'
        conn.execute(sql, (content, post_id))
        conn.commit()
        conn.close()
        return redirect('/post/{}' .format(post_id))

@app.route('/post/<post_id>')
def post(post_id=None):
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql = 'select * from blog where post_id == {}' .format(post_id)
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3]) for item in conn.execute(sql)]
    sql2 = 'select date from blog'
    results2 = [item for item in conn.execute(sql2)]
    count = len(results2)
    conn.close()
    return render_template('post.html', results=results, site_title=site_title, user=current_app.config['USERNAME'], count=count)

@app.route('/delete/<post_id>')
def delete(post_id=None):
    if not session.get('logged_in'):
        return 'access denied'
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql = 'delete from blog where post_id == {}' .format(post_id)
    conn.execute(sql)
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/blog-upload', methods=['GET', 'POST'])
def upload_file_blog(date=None):
    date = datetime.datetime.today().strftime('%Y-%m')
    upload = os.path.join(app.root_path, 'static', 'uploads')
    if not session.get('logged_in'):
        return 'access denied'

    if request.method == 'POST':
        lst = []
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            lst.append(filename)
            datename = os.path.join(upload, date)
            if not os.path.exists(datename):
                os.makedirs(datename)
            os.chmod(datename, 0o777)
            if not os.path.exists(os.path.join(datename, filename)):
                file.save(os.path.join(datename, filename))
            else:
                digit = 1
                split = filename.split('.')
                filename2 = '_'.join(split[0:-1])+'_'+str(digit)+'.'+split[-1]
                while os.path.exists(os.path.join(datename, filename2)):
                    digit += 1
                    filename2 = '_'.join(split[0:-1])+'_'+str(digit)+'.'+split[-1]
                try:
                    file.save(os.path.join(datename, filename2))
                except:
                    pass
            return redirect('/')

@app.route('/library')
def media_library():
    upload = os.path.join(app.root_path, 'static', 'uploads')
    list_img = []
    for subdir, dirs, files in os.walk(upload):
        for fn in files:
            subdir1 = subdir.split(os.path.sep)[-1]+'/'+fn
            list_img.append(subdir1)
            list_img.reverse()
    return render_template('media_library.html', site_title=site_title, user=current_app.config['USERNAME'], list_img=list_img)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            return redirect('/')
    return render_template('login.html', error=error, user=current_app.config['USERNAME'])

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('inde22x'))


if __name__ == "__main__":
    app.run()
