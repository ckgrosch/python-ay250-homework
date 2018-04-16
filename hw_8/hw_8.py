import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import send_from_directory
from pybtex.database import parse_file
from pybtex.richtext import String
import sqlite3
import os.path
from bib2db import bib_to_db #bib2py is a set of functions I wrote to convert the .bib file to a .db

#setting up flask
app = Flask(__name__)
#this section sets up all the directories for file upload
if os.path.isdir('uploads'):
    UPLOAD_FOLDER = 'uploads'
else:
    os.mkdir('uploads')
    UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['bib'])
DB_NAME = 'uploads/uploaded_citations.db'
TBL_NAME = 'query_table'
# conn = sqlite3.connect(DB_NAME)
# cursor = conn.cursor()
# cmd1 = """DROP TABLE IF EXISTS {}""".format(TBL_NAME)
# cursor.execute(cmd1)
# sql_cmd = """CREATE TABLE {} (id INTEGER PRIMARY KEY AUTOINCREMENT, cit_key TEXT, author_list TEXT, journal TEXT, volume INT, pages TEXT, year INT, title TEXT, collection TEXT)""".format(TBL_NAME)
# cursor.execute(sql_cmd)
# conn.commit()
# conn.close()


#function for homepage
@app.route('/', methods=['GET', 'POST'])
def home_page():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT collection FROM {} ".format(TBL_NAME))
    collects_present = [clct[0] for clct in cursor.fetchall()]
    conn.commit()
    conn.close()
    return render_template('index.html', collects_present = collects_present)

# All the functions for .bib file upload and file upload page
def allowed_file(filename):
    """This function is called by upload file to make sure only
     .bib files are uploaded"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/insert', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            collection_name = request.form['collection_name']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fname = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            bib_to_db(fname,collection_name,DB_NAME, TBL_NAME)
            return redirect(url_for('home_page'))
    return render_template('insert.html')
# @app.route('/insert', methods=['GET', 'POST'])
# def insert_stuff():
#     return render_template('base.html', page_title = "Insert Stuff", content = "MAKE BUTTS")

@app.route('/search', methods=['GET', 'POST'])
def search_stuff():
    col_names = ['Citation Key','Author List','Journal','Volume','Pages','Year','Title','Collection']
    print(request.method)
    results = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT collection FROM {};".format(TBL_NAME))
    collects_present = [clct[0] for clct in cursor.fetchall()]
    if len(collects_present) == 0:
        collects_present = False
    else:
        collects_present = True
        print(request.method)
        if request.method == 'POST':
            print('POST')
            query_str = request.form['query_str']
            search = "SELECT * FROM {} WHERE ".format(TBL_NAME) + query_str + ';'
            print(search)
            cursor.execute(search)
            query_out = cursor.fetchall()
            print(query_out)
            citation = ""
            for cite in query_out:
                for idx, item in enumerate(cite[1:]):
                    citation += col_names[idx] + ': '+ str(item) + '<br>'
                results.append(citation)
                citation = ""
            return render_template('query.html', collects_present=collects_present, results = results)
    print(collects_present)
    return render_template('query.html', collects_present=collects_present, results = results)
