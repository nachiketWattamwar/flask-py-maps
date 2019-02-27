from flask import Flask,render_template,redirect, url_for,request
from flask_dance.contrib.google import make_google_blueprint, google
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from google.cloud import datastore
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf import RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired,Email,Length
from six.moves import urllib
import json

endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
api_key = 'apikey'


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mySecretKey'
app.config['RECAPTCHA_PUBLIC_KEY'] = 'publicKey'
app.config['RECAPTCHA_PRIVATE_KEY'] = 'privateKey'

google_bp = make_google_blueprint(
client_id = "clientID",
client_secret = "secretKey"
)

app.register_blueprint(google_bp,url_prefix='/something')

Bootstrap(app)
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),Length(min=4,max=10)])
    password = PasswordField('password',validators=[InputRequired(),Length(min=5,max=10)])
    rememberme = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    email = StringField('email',validators=[InputRequired(),Email(message = 'Invalid email'),Length(max=40)])
    username = StringField('Username', validators=[InputRequired(),Length(min=4,max=10)])
    password = PasswordField('password',validators=[InputRequired(),Length(min=5,max=10)])
    recaptcha = RecaptchaField()

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/google')
def google_login():
    if not google.authorized:
        print("inside if ")
        return redirect_url(url_for('google.login'))
    print("failed")

@app.route('/admin',methods=['GET','POST'])
def admin():
    print("inside admin")
    form = LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():#if form.validate_on_submit():
        print("inside submit button ")
        if form.username.data == 'admin' and form.password.data == 'admin':
            print("inside if for admin")
            datastore_client = datastore.Client()
            query = datastore_client.query(kind = '5634161670881280')
            #print("all values ",list(query.fetch()))
            all_entities = list(query.fetch())
            #print(all_entities[0])
            return render_template('passwords.html',all_entities = all_entities)
            #return '<h1>'+form.username.data + ' ' + form.password.data + '<h1>
    return render_template('admin.html',form = form)


@app.route('/delete',methods=['POST'])
def delete():
    print("id is ",request.form.get("id"))
    datastore_client = datastore.Client()
    print("inside updateenttiy")
    entity = datastore.Entity(key=request.form.get("id"))
    entity.update({
    'password': 1337
    })
    datastore_client.put(entity)

    return render_template('passwords.html')

@app.route('/update',methods=['POST'])
def updateEntity():
    return 1

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    print(form.validate_on_submit())
    if form.validate_on_submit():#if form.validate_on_submit():
        print("inside if ")
        datastore_client = datastore.Client()
        query = datastore_client.query(kind = '5634161670881280')
        all_entities = list(query.fetch())
        for entity in all_entities:

            if form.username.data == entity['username'] and form.password.data == entity['password']:
                return render_template('/dashboard.html',name=entity['username'])

    print("else ")
    return render_template('login.html',form = form)

@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        datastore_client = datastore.Client()
        entity = datastore.Entity(key=datastore_client.key('5634161670881280'))
        entity.update({
        'email': form.email.data,
        'password':form.password.data,
        'username':form.username.data
        })
        print("key is ",datastore_client.put(entity))
        # get allvalues
        return 'inside if'

    print("inside else ")
    #print(request.form['g-recaptcha-response'])
    return render_template('signup.html',form = form)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/search', methods=['GET','POST'])
def search():
    origin = request.form['origin']
    print(origin)
    destination = request.form['destination']
    print(destination)
    nav_request = 'origin={}&destination={}&key={}'.format(origin,destination,api_key)
    myrequest = endpoint + nav_request
    print("complete request is ",myrequest)
    response = urllib.request.urlopen(myrequest).read()
    directions = json.loads(response)
    print(directions.keys())
    routes = directions['routes']
    routes[0].keys()
    return request.form['origin']


@app.route('/logout')
def logout():
    return 1



if __name__ == '__main__':
    app.run(debug=True)
