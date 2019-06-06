import flask
from database import Database_Handler
import jinja2
from datetime import datetime
import dateutil.parser
from urllib.parse import urljoin
from flask_oauth import OAuth
import requests
import json

LOGIN_REDIRCT = '/cash_session'


app = flask.Flask(__name__, static_url_path='', static_folder='../web/static', template_folder='../web/templates')
app.config['GOOGLE_ID'] = '350802355428-83d26vllkpn4h8kkfl47f2dpgmea25ln.apps.googleusercontent.com'
app.config['GOOGLE_SECRET'] = '88XepAKjJu1Rz77wX-JpZPMK'
app.secret_key = 'dev'
oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=app.config.get('GOOGLE_ID'),
                          consumer_secret=app.config.get('GOOGLE_SECRET'))
@app.route('/')
def index():
    if 'google_token' in flask.session:
        me = google.get('userinfo')
        return flask.jsonify({"data": me.data})
    return flask.redirect(flask.url_for('login'))


@app.route('/login')
def login():
    return google.authorize(callback=flask.url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    flask.session.pop('google_token', None)
    return flask.redirect(flask.url_for('index'))


@app.route('/login/authorized')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    flask.session['access_token'] = access_token, ''
    re = requests.get('https://www.googleapis.com/oauth2/v1/userinfo?alt=json',None, headers={'Authorization': 'OAuth '+access_token})
    data = json.loads(re.text)
    flask.session['email'] = data['email']

    db = Database_Handler("../data/db.db")

    if db.has_account(data['email']):
        return flask.redirect(flask.url_for('get_cash_sessions'))
    else:
        return flask.redirect(flask.url_for('register'))


@google.tokengetter
def get_google_oauth_token():
    return flask.session.get('google_token')


@app.route('/register' , methods=["GET" , "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template('register.html' , email=flask.session.get('email'))
    elif flask.request.method == "POST":
        db = Database_Handler("../data/db.db")
        db.create_account(flask.request.form["email"] , flask.request.form['inital'])
        return flask.redirect(flask.url_for('get_cash_sessions'))


@app.route('/cash_session')
def get_cash_sessions():
    #return "hello"
    #Check to see if user is signed in otherwise redirect them to login screnn
    key = flask.session.get('access_token')
    if key is None:
        return flask.redirect(flask.url_for('index'))
    email = flask.session.get('email')
    
    
    db = Database_Handler("../data/db.db")
    rows , headers = db.get_cash_sessions(email)

    
    
    profits= []
    startForm = []
    endForm = []
    for row in rows:
        row = list(row) 
        
        date = dateutil.parser.parse(row[0])
        start = date.strftime('%D %T')
        startForm.append(start)
        end = None
        if not row[1] is None:
            date = dateutil.parser.parse(row[1])
            end = date.strftime("%D %T")
        endForm.append(end)
        if row[-1]:
            profit = row[-1] - row[-2]
            profits.append(profit)
        else:
            profits.append(None)

    
    headers.append("Profit")
    return flask.render_template('index.html' , rows=zip(rows , profits , startForm , endForm) , headers=headers)

@app.route("/addcash", methods=["GET" , "POST"])
def add_cash_session():
    #Check to see if user is signed in otherwise redirect them to login screnn
    access_key = flask.session.get('access_token')
    if access_key is None:
        return flask.redirect(flask.url_for('index'))
    


    if flask.request.method == "GET":
        return flask.render_template('add_cash.html')
    elif flask.request.method == 'POST':
        db = Database_Handler("../data/db.db")
        date = flask.request.form["starttime"]
        SB = flask.request.form["SB"] 
        BB = flask.request.form["BB"]
        buyin = int(flask.request.form["buyin"])
        email = flask.session.get('email')
        db.start_cash_session(date , SB , BB , buyin , email)
        return flask.redirect(flask.url_for("get_cash_sessions"))

@app.route("/endcash/<date>" , methods=["GET" , "POST"])
def end_cash_session(date):
        
        key = flask.session.get('access_token')
        if key is None:
            return flask.redirect(flask.url_for('index'))
        email = flask.session.get('email')
        db = Database_Handler("../data/db.db")

        

        if flask.request.method == "GET":
             entry = db.get_cash_session(date , email)
             
             return flask.render_template("end_cash.html",date=date , entry=entry)
        elif flask.request.method == "POST":
            
            
            if flask.request.form["function"] == 'END':
                cashout = flask.request.form["cashout"]
                endtime = flask.request.form["endtime"]
                db.end_cash_session(date , endtime , cashout , email)
            elif flask.request.form["function"] == "EDIT":  

                SB = flask.request.form["SB"]
                BB = flask.request.form["BB"]
                buyin = flask.request.form["buyin"]

                if SB != "":
                    db.update_SB(SB , date , email)
                if BB != "":
                    db.update_BB(BB , date , email )
                if buyin != "":
                    db.update_Buyin(buyin , date , email )

            else:
                db.remove_cash_entry(date , email)
            return flask.redirect(flask.url_for("get_cash_sessions"))


if __name__ == '__main__':
    app.run(debug=True)