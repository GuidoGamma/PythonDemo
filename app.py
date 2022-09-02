from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_paginate  import Pagination, get_page_args
import urllib
import hashlib, os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from bokeh.embed import components

from classes import DeanOci, Autorisatie
from customtags import getallcustomtags
from devicetypes import getalldevicetypes, getdevicetype, getmostusedtagschart, getpiechart

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_WEB_APP_KEY')


@app.route('/')
@app.route('/login')
def home():
    session.clear()
    return render_template('login.html', title="Login pagina", logged_in=False)


@app.route('/login', methods=['POST'])
def login():
    params = urllib.parse.quote_plus(os.environ.get('AutorisatieDatabaseConnection'))
    engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(Autorisatie.Gebruiker).filter(Autorisatie.Gebruiker.Gebruikersnaam.in_([POST_USERNAME]))
    result = query.first()
    if result:
        passwordCheck = checkPassWord(POST_PASSWORD, result.SaltedHash)
        if passwordCheck == True:
            session['logged_in'] = True
        else:
            flash('Invalid Credentials')
    else:
        flash('Invalid Credentials')

    return redirect(url_for('index'))

def checkPassWord(provided_password, stored_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]

    pwdhash = hashlib.sha256(salt.encode('utf-8') + provided_password.encode('utf-8')).hexdigest()
    return pwdhash == stored_password


@app.route('/index')
def index():
    if (logged_in() == True):
        return render_template('index.html', title="Overzicht", logged_in=True)

    return redirect(url_for('login'))

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

def logged_in():
    if (session.get('logged_in')):
        if (session['logged_in'] == True):
            return True

    return False

@app.route('/customtags')
def customtags():
    if logged_in():
        data = getallcustomtags()

        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')

        total = len(data)
        pagination_data = get_paged_data(data, offset=offset, per_page=per_page)
        pagination = Pagination(page=page,
                                per_page=per_page,
                                total=total,
                                css_framework='bootstrap4')

        return render_template('customtags.html',
                                title="Custom Tags",
                                logged_in=True,
                                customtags=pagination_data,
                                page=page,
                                per_page=per_page,
                                pagination=pagination)

    return redirect(url_for('login'))

@app.route('/devicetypes')
def devicetypes():
    if logged_in():
        data = getalldevicetypes()

        page, per_page, offset = get_page_args(page_parameter='page',
                                               per_page_parameter='per_page')

        total = len(data)
        pagination_data = get_paged_data(data, offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total,
                                css_framework='bootstrap4')

        graph = getpiechart()

        piechart_script, piechart_div = components(graph)

        return render_template('devicetypes.html', title="Device Types", logged_in=True,
                               piechart_div = piechart_div,
                               piechart_script = piechart_script,
                                devicetypes=pagination_data,
                                page=page,
                                per_page=per_page,
                                pagination=pagination)

    return redirect(url_for('login'))

@app.route('/devicetypes/<devicetype_uid>')
def devicetype(devicetype_uid):
    if logged_in():
        data = getdevicetype(devicetype_uid)

        graph = getmostusedtagschart(devicetype_uid)

        script1, div1 = components(graph)

        return render_template('devicetype.html', title=data.Name + " details", deviceType = data, logged_in=True,
                               the_div1=div1, the_script1=script1)

    return redirect(url_for('login'))

def get_paged_data(data, offset=0, per_page=10):
    return data[offset: offset + per_page]

if __name__ == '__main__':
    app.run()


