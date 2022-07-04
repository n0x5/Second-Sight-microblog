from flask import Flask
from flask import current_app
from flask import render_template
from flask import request
from flask import session
from flask import redirect
from werkzeug.utils import secure_filename
import json
import os
import sqlite3
import markdown
import datetime
import time

app = Flask(__name__)

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

@app.route("/")
def hello():
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql = 'select * from blog order by date desc limit 10'
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
            highest_id2 = results_higher[-1][-1]
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
    sql_lower = 'select * from blog where date < ? order by date desc limit 10'
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3], item[2]) for item in conn.execute(sql_lower, (after,))]
    highest_id = results[0][-1]
    lowest_id = results[-1][-1]
    sql_lower = 'select * from blog where date < ? order by date'
    results_lower = [item for item in conn.execute(sql_lower, (lowest_id,))]
    results_lower.reverse()
    if len(results_lower) != 0:
        lower_posts = '<a href="/older/{}">Older entries</a>' .format(lowest_id)
    else:
        lower_posts = ''
    sql_higher = 'select * from blog where date > ? order by date'
    results_higher = [item for item in conn.execute(sql_higher, (highest_id,))]
    results_higher.reverse()
    if len(results_higher) != 0:
        highest_id2 = results_higher[-1][-1]
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
    sql_higher2 = 'select * from blog where date > ? order by date limit 10'
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3], item[2]) for item in conn.execute(sql_higher2, (after,))]
    results.reverse()
    highest_id = results[0][-1]
    lowest_id = results[-1][-1]
    sql_lower = 'select * from blog where date < ? order by date'
    results_lower = [item for item in conn.execute(sql_lower, (lowest_id,))]
    results_lower.reverse()
    if len(results_lower) != 0:
        lower_posts = '<a href="/older/{}">Older entries</a>' .format(lowest_id)
    else:
        lower_posts = ''
    sql_higher = 'select * from blog where date > ? order by date'
    results_higher = [item for item in conn.execute(sql_higher, (highest_id,))]
    results_higher.reverse()
    if len(results_higher) != 0:
        highest_id2 = results_higher[-1][-1]
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
        for subdir, dirs, files in os.walk(upload):
            for fn in files:
                subdir1 = subdir.split(os.path.sep)[-1]+'/'+fn
                list_img.append(subdir1)
                list_img2 = reversed(list_img[-5:])
    if request.method == 'POST':
        content = request.form['body']
        date = int(time.time())
        conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
        sql = 'insert into blog (body, date) values (?,?)'
        conn.execute(sql, (content, date))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('blog.html', site_title=site_title, list_img=list_img2, user=current_app.config['USERNAME'])

@app.route('/post/<post_id>')
def post(post_id=None):
    conn = sqlite3.connect(os.path.join(db_path, 'site.db'))
    sql = 'select * from blog where post_id == {}' .format(post_id)
    results = [(markdown.markdown(item[0], extensions=extension_list).replace('<img', '<img width="500"'), item[1], \
                datetime.datetime.fromtimestamp(item[2]).strftime(date_format), item[3]) for item in conn.execute(sql)]
    conn.close()
    return render_template('post.html', results=results, site_title=site_title, user=current_app.config['USERNAME'])

@app.route('/delete/<post_id>')
def delete(post_id=None):
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
                filename2 = split[-0]+'_'+str(digit)+'.'+split[-1]
                while os.path.exists(os.path.join(datename, filename2)):
                    digit += 1
                    filename2 = split[-0]+'_'+str(digit)+'.'+split[-1]
                try:
                    file.save(os.path.join(datename, filename2))
                except:
                    pass
            return redirect('/')


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