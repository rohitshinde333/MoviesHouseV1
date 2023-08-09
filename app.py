
from flask import Flask, render_template, request, url_for, redirect,flash, jsonify
import os,sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, IntegerField, DateTimeField
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange
from flask_bcrypt import Bcrypt
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob
from flask_restful import Resource,Api, marshal_with,reqparse,fields


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY']='bin@9'
api = Api(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80),nullable = False)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    Tickets =  db.relationship('Tickets', backref='users')
    def __init__(self, firstname, lastname, username, password, age):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password
        self.age = age
    def __repr__(self):
        return f'<User {self.firstname}>'

class RegisterForm(FlaskForm):
    firstname = StringField('First name',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"firstname"})
    lastname = StringField('Last name',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"lastname"})
    username = StringField('username',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"username"})
    password = PasswordField('Password',[InputRequired(),Length(min=8,max=20)],render_kw={"Placeholder":"password"})
    age = IntegerField('Age',[InputRequired()],render_kw={"Placeholder":"age"})
    submit = SubmitField("Register")
    def validate_username(self, username):
        existing_data_username = User.query.filter_by(
            username = username.data
        ).first()

        if existing_data_username:
            raise ValidationError("Username is not available! Please Try another one.")

class LoginForm(FlaskForm):
    username = StringField('username',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"username"})
    password = PasswordField('password',[InputRequired(),Length(min=8,max=20)],render_kw={"Placeholder":"password"})
    submit = SubmitField("Login")

class UpdateUserForm(FlaskForm):
    firstname = StringField('First name',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"firstname"})
    lastname = StringField('Last name',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"lastname"})
    username = StringField('Last name',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"username"})
    password = PasswordField('Password',[InputRequired(),Length(min=8,max=20)],render_kw={"Placeholder":"password"})
    age = IntegerField('Age',[InputRequired()],render_kw={"Placeholder":"age"})
    submit = SubmitField("Update")
    def validate_username(self, username):
        existing_data_username = User.query.filter_by(
            username = username.data
        ).first()

        if existing_data_username:
            raise ValidationError("Username is not available! Please Try another one.")



class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    booked_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'),nullable = False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'),nullable = False)

    def __repr__(self):
        return f'<Ticket {self.id}>'
    def __init__(self,user_id,seat_id,show_id):
        self.user_id = user_id
        self.seat_id = seat_id
        self.show_id = show_id


seat_show = db.Table('seat_show',
                      db.Column('seat_id',db.Integer,db.ForeignKey('seats.id')),
                      db.Column('show_id',db.Integer,db.ForeignKey('show.id'))
)

class Seats(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    codeRow = db.Column(db.Integer, nullable = False)
    codeColumn = db.Column(db.Integer, nullable = False)
    Tier_id = db.Column(db.Integer, db.ForeignKey('tier.id'), nullable = False)
    Screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable = False)
    booking = db.relationship('Show', secondary = seat_show, backref = 'SeatsBooked')
    tickets = db.relationship('Tickets',backref = 'seats')
    def __repr__(self):
        return f'Row: {self.codeRow} Column: {self.codeColumn} {(Tier.query.filter_by(id=self.Tier_id)).first()}'
    def __init__(self,codeRow,codeColumn,Tier_id,Screen_id):
        self.codeRow = codeRow
        self.codeColumn = codeColumn
        self.Tier_id = Tier_id
        self.Screen_id = Screen_id
        

def Seat_query():
    return Seats.query.filter_by(status=0)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable = False)
    time = db.Column(db.DateTime,nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable = False)
    
    tickets = db.relationship('Tickets',backref = 'show')
    def __init__(self,movie_id,time,screen_id):
        self.movie_id = movie_id
        self.time = time
        self.screen_id = screen_id
    def __repr__(self):
        
        return f'{(Screen.query.filter_by(id=self.screen_id)).first()}  Movie: {(Movie.query.filter_by(id = self.movie_id)).first()} Show Time: {self.time}'

movie_cast = db.Table('movie_cast',
                      db.Column('movie_id',db.Integer,db.ForeignKey('movie.id')),
                      db.Column('cast_id',db.Integer,db.ForeignKey('cast.id'))
)


class Movie(db.Model):
    __searchable__ = ['name','info']
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(100), nullable=False)
    info = db.Column(db.String(200), nullable=False)
    poster = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer,nullable = False)
    casting = db.relationship('Cast', secondary = movie_cast, backref = 'casted')
    
    shows = db.relationship('Show',backref = 'movie')
    reviews = db.relationship('Review',backref = 'movie')
    def __init__(self,name,info,poster,rating):
        self.name = name
        self.info = info
        self.poster = poster
        self.rating = rating
        
    def __repr__(self):
        return f' {self.name} '

def Movie_query():
    return Movie.query


class Cast(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20),nullable=False)
    photo = db.Column(db.String(), nullable=False)
    def __init__(self,firstname,lastname,type,photo):
        self.firstname = firstname
        self.lastname = lastname
        self.type = type
        self.photo = photo
    def __repr__(self):
        return f'Casting {self.type} {self.firstname} {self.lastname}'

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pin = db.Column(db.Integer,nullable=False)
    theatres = db.relationship('Theatre', backref='place')
    def __init__(self,city,state,pin):
        self.city = city
        self.state = state
        self.pin = pin
    def __repr__(self):
        return f' {self.city}, {self.state} '


def place_query():
    return Place.query


class Theatre(db.Model):
    __searchable__ = ['name','photo','place_id']
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String(100), nullable=False)
    photo =db.Column(db.String(), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'), nullable = False)
    screens = db.relationship('Screen', backref='theatre')
    def __init__(self,name,place_id,photo):
        self.name = name
        self.place_id = place_id
        self.photo = photo
    def __repr__(self):
        return f'{self.name}'

def Theatre_query():
    return Theatre.query


class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    number = db.Column(db.Integer, nullable=False)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'), nullable = False)
    shows = db.relationship('Show',backref='screen')
    tiers = db.relationship('Tier', backref='screen')
    
    
    def __init__(self,number,theatre_id):
        self.number = number
        self.theatre_id = theatre_id
    def __repr__(self):
        return f'Screen: {self.number} Theatre name: {(Theatre.query.filter_by(id = self.theatre_id)).first()} '

def Screen_query():
    return Screen.query

class Tier(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    number = db.Column(db.Integer, nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screen.id'), nullable = False)
    price = db.Column(db.Integer, nullable=False)
    seats = db.relationship('Seats', backref='tier')
    def __init__(self,number,screen_id, price):
        self.number = number
        self.screen_id = screen_id
        self.price = price
        
    def __repr__(self):
        return f'Tier : {self.number}  {(Screen.query.filter_by(id=self.screen_id).first())}'
    
def Tier_query():
    return Tier.query




class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(80), unique=True, nullable=False) 
    feedback = db.Column(db.String(500), nullable=False)
    def __init__(self, username, feedback):
        self.username = username
        self.feedback = feedback
    def __repr__(self):
        return f'<Feedback {self.id}>'
    
#defining flask forms from here.
class FeedbackForm(FlaskForm):
    username = StringField('username',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"username"})
    feedback = StringField('feedback',[InputRequired(),Length(min=3,max=500)],render_kw={"Placeholder":"feedback"})
    submit = SubmitField("Submit Feedback")

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)      
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable = False)
    
    def __init__(self, user_id, content, movie_id):
        self.user_id = user_id
        self.content = content
        self.movie_id = movie_id
    def __repr__(self):
        return f' @ {((User.query.filter_by(id=self.user_id)).first()).username} : {self.content}'

class Sentiments(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable = False)
    subjectivity = db.Column(db.Integer,nullable = False)
    polarity = db.Column(db.Integer,nullable = False)

    def __init__(self,movie_id,subjectivity,polarity):
        self.movie_id = movie_id
        self.subjectivity = subjectivity
        self.polarity = polarity

class AddPlaceForm(FlaskForm):
    city = StringField('city',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"City"})
    state = StringField('state',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"State"})
    pin = IntegerField('pin',[InputRequired()],render_kw={"Placeholder":"6 digit pin"})
    submit = SubmitField("Add place")

class AddTheatreForm(FlaskForm):
    name = StringField('name',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"Name"})
    photo = StringField('theatre',[InputRequired()],render_kw={"Placeholder":"Photo"})
    place = QuerySelectField(query_factory=place_query, allow_blank=False)
    submit = SubmitField("Add Theatre")

class AddScreenForm(FlaskForm):
    number = IntegerField('number',[InputRequired()],render_kw={"Placeholder":"Screen Number"})
    theatre = QuerySelectField(query_factory=Theatre_query, allow_blank=False)
    submit = SubmitField("Add Screen")

class AddTierForm(FlaskForm):
    number = IntegerField('number',validators=[ InputRequired(),NumberRange(min=1, max=3)],render_kw={"Placeholder":"Tier Number"})
    price = IntegerField('price',validators=[ InputRequired()],render_kw={"Placeholder":"Ticket Price"})
    screen = QuerySelectField(query_factory=Screen_query, allow_blank=False)
    submit = SubmitField("Add Tier")

class AddMovieForm(FlaskForm):
    name = StringField('name',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"Name"})
    info = StringField('info',[InputRequired(),Length(min=3,max=150)],render_kw={"Placeholder":"Info"})
    poster = StringField('Paste Link',[InputRequired()],render_kw={"Placeholder":"Link"})
    rating = IntegerField('rating',[InputRequired(),NumberRange(min=1, max=5)],render_kw={"Placeholder":"Rating"})
    submit = SubmitField("Add Movie")

class AddSeatsForm(FlaskForm):
    rows = IntegerField('rows',validators=[ InputRequired(),NumberRange(min=1, max=20)],render_kw={"Placeholder":"rows"})
    columns = IntegerField('columns',validators=[ InputRequired(),NumberRange(min=1, max=20)],render_kw={"Placeholder":"columns"})
    tier = QuerySelectField(query_factory=Tier_query, allow_blank=False)
    submit = SubmitField("Add seats")

class AddShowForm(FlaskForm):
    screen = QuerySelectField(query_factory= Screen_query, )
    time = DateTimeField('Date Time',[InputRequired()],format= "%Y-%m-%d %H:%M:%S",render_kw={"Placeholder":"Y-m-d H:M:S"})
    movie = QuerySelectField(query_factory= Movie_query)
    
    submit = SubmitField("Add Show")

class AddMovieCast(FlaskForm):
    movie = StringField('movie',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"Movie Name"})
    cast = StringField('cast',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"Cast FirstName"})
    submit = SubmitField("Add Cast to movie")

class Bookings(FlaskForm):
    
    seat = QuerySelectMultipleField(query_factory=Seat_query, allow_blank=False)
    submit = SubmitField("Book Tickets")

class ReviewForm(FlaskForm):
    content = StringField('feedback',[InputRequired(),Length(min=3,max=1000)],render_kw={"Placeholder":"Write your review here...."})
    submit = SubmitField("Submit Review")

class SearchForm(FlaskForm):
    searched = StringField('searched',[InputRequired(),Length(min=3,max=20)],render_kw={"Placeholder":"search "})
    submit = SubmitField("Search")

class updatePlaceForm(FlaskForm):
    city = StringField('city',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"City"})
    state = StringField('state',[InputRequired(),Length(min=3,max=50)],render_kw={"Placeholder":"State"})
    pin = IntegerField('pin',[InputRequired()],render_kw={"Placeholder":"6 digit pin"})
    submit = SubmitField("Update place")

class updateTheatreForm(FlaskForm):
    name = StringField('city',[InputRequired(),Length(min=3,max=15)],render_kw={"Placeholder":"Name"})
    photo = StringField('theatre',[InputRequired()],render_kw={"Placeholder":"Photo"})
    place = QuerySelectField(query_factory=place_query, allow_blank=False)
    submit = SubmitField("Add Theatre")

class updateShowForm(FlaskForm):
    screen = QuerySelectField(query_factory= Screen_query, )
    time = DateTimeField('Date Time',[InputRequired()],format= "%Y-%m-%d %H:%M:%S",)
    movie = QuerySelectField(query_factory= Movie_query)
    
    submit = SubmitField("Update Show")

class updateScreenForm(FlaskForm):
    number = IntegerField('number',[InputRequired()],render_kw={"Placeholder":"Screen Number"})
    theatre = QuerySelectField(query_factory=Theatre_query, allow_blank=False)
    submit = SubmitField("Update Screen")

#Defining API class
with app.app_context():

    
    show_fields = {
        "id": fields.Integer,
        "movie_id": fields.Integer,
        "time": fields.DateTime,
        "screen_id": fields.Integer,
    }

    class ShowResource(Resource):
        @marshal_with(show_fields)
        def get(self, show_id):
            """Get a single Show by ID"""
            show = Show.query.get(show_id)
            if not show:
                return {"message": "Show not found"}, 404
            return show

        @marshal_with(show_fields)
        def put(self, show_id):
            """Update a single Show by ID"""
            parser = reqparse.RequestParser()
            parser.add_argument("movie_id", type=int, help="Movie ID is required")
            parser.add_argument("time", type=str, help="Show time is required")
            parser.add_argument("screen_id", type=int, help="Screen ID is required")
            args = parser.parse_args()

            show = Show.query.get(show_id)
            if not show:
                return {"message": "Show not found"}, 404

            show.movie_id = args["movie_id"]
            show.time = args["time"]
            show.screen_id = args["screen_id"]
            db.session.commit()
            return show

        def delete(self, show_id):
            """Delete a single Show by ID"""
            show = Show.query.get(show_id)
            if not show:
                return {"message": "Show not found"}, 404
            db.session.delete(show)
            db.session.commit()
            return {"message": "Show deleted successfully"}

    class ShowListResource(Resource):
        @marshal_with(show_fields)
        def get(self):
            """Get all Shows"""
            shows = Show.query.all()
            return shows

        @marshal_with(show_fields)
        def post(self):
            """Create a new Show"""
            parser = reqparse.RequestParser()
            parser.add_argument("movie_id", type=int, help="Movie ID is required")
            parser.add_argument("time", type=str, help="Show time is required")
            parser.add_argument("screen_id", type=int, help="Screen ID is required")
            args = parser.parse_args()

            show = Show(args["movie_id"], args["time"], args["screen_id"])
            db.session.add(show)
            db.session.commit()
            return show, 201

    
    api.add_resource(ShowResource, "/shows/<int:show_id>")
    api.add_resource(ShowListResource, "/shows")

    theatre_fields = {
        "id": fields.Integer,
        "name": fields.String,
        "photo": fields.String,
        "place_id": fields.Integer,
    }

    class TheatreResource(Resource):
        @marshal_with(theatre_fields)
        def get(self, theatre_id):
            """Get a single Theatre by ID"""
            theatre = Theatre.query.get(theatre_id)
            if not theatre:
                return {"message": "Theatre not found"}, 404
            return theatre

        @marshal_with(theatre_fields)
        def put(self, theatre_id):
            """Update a single Theatre by ID"""
            parser = reqparse.RequestParser()
            parser.add_argument("name", type=str, help="Name is required")
            parser.add_argument("photo", type=str, help="Photo is required")
            parser.add_argument("place_id", type=int, help="Place ID is required")
            args = parser.parse_args()

            theatre = Theatre.query.get(theatre_id)
            if not theatre:
                return {"message": "Theatre not found"}, 404

            theatre.name = args["name"]
            theatre.photo = args["photo"]
            theatre.place_id = args["place_id"]
            db.session.commit()
            return theatre

        def delete(self, theatre_id):
            """Delete a single Theatre by ID"""
            theatre = Theatre.query.get(theatre_id)
            if not theatre:
                return {"message": "Theatre not found"}, 404
            db.session.delete(theatre)
            db.session.commit()
            return {"message": "Theatre deleted successfully"}

    class TheatreListResource(Resource):
        @marshal_with(theatre_fields)
        def get(self):
            """Get all Theatres"""
            theatres = Theatre.query.all()
            return theatres

        @marshal_with(theatre_fields)
        def post(self):
            """Create a new Theatre"""
            parser = reqparse.RequestParser()
            parser.add_argument("name", type=str, help="Name is required")
            parser.add_argument("photo", type=str, help="Photo is required")
            parser.add_argument("place_id", type=int, help="Place ID is required")
            args = parser.parse_args()

            theatre = Theatre(args["name"], args["place_id"], args["photo"])
            db.session.add(theatre)
            db.session.commit()
            return theatre, 201

    
    api.add_resource(TheatreResource, "/theatres/<int:theatre_id>")
    api.add_resource(TheatreListResource, "/theatres")


#Defining routes from here.
@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else :
                raise ValidationError("Incorrect Password!")
        else:
            raise ValidationError("Username not found ! OOPS")
    return render_template('login.html',form = form)


@app.route('/logout',methods= ['GET','POST'])
@login_required
def logout():
    logout_user()
    return render_template('logout.html')



@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashing_pwd = bcrypt.generate_password_hash(form.password.data)
        new_user = User(firstname = form.firstname.data, lastname = form.lastname.data, username = form.username.data, password = hashing_pwd, age = form.age.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))


    return render_template('register.html',form = form)


@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    user = current_user
    return render_template('dashboard.html',user=user)



@app.route('/dashboard/user_profile',methods=['GET','POST'])
@login_required
def user_profile():
    user=current_user
    return render_template('profile.html',user=user)




@app.route('/dashboard/user_profile/update',methods=['GET','POST'])
@login_required
def update_profile():
    form = UpdateUserForm()
    user = current_user
    if form.validate_on_submit():
        hashing_pwd = bcrypt.generate_password_hash(form.password.data)
        
        if request.method =="POST":
            user.firstname = request.form['firstname']
            user.lastname = request.form['lastname']
            user.username = request.form['username']
            user.password = hashing_pwd
            user.age = request.form['age']
            
            try:
                db.session.commit()
                flash("user updated successfully.")
                return redirect(url_for('user_profile'))
            except:
                flash("looks like there was some problem with database.")
    return render_template('updateProfile.html',form=form,user=user)



@app.route('/feedback',methods=['GET','POST'])
@login_required
def feedback():
    form = FeedbackForm()
    user = current_user
    feedbacks = Feedback.query.all()
    if form.validate_on_submit():
        new_feedback = Feedback(username = form.username.data, feedback= form.feedback.data)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('feedback'))
    return render_template('feedback.html',form=form,user=user,feedbacks=feedbacks)




@app.route('/admin')
@login_required
def admin():
    user = current_user
    id = current_user.id
    if id==1:
        return render_template('admin.html',user=user)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))



@app.route('/addPlace',methods=['GET','POST'])
@login_required
def addPlace():
    user = current_user
    id = current_user.id 
    if id==1:
        form = AddPlaceForm()
        if form.validate_on_submit():
            new_place = Place(city=form.city.data,state = form.state.data,pin = form.pin.data)
            db.session.add(new_place)
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addPlace.html',user=user,form=form)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))



@app.route('/addCast',methods=['GET','POST'])
@login_required
def addCast():
    user = current_user
    id = current_user.id
    if id==1:
        if request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            type = request.form['type']
            photo = request.form['link']
            new_cast = Cast(firstname=firstname,lastname=lastname,type=type,photo=photo)
            db.session.add(new_cast)
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addCast.html',user=user)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))



@app.route('/addTheatre',methods=['GET','POST'])
@login_required
def addTheatre():
    user = current_user
    id = current_user.id
    if id==1:
        form = AddTheatreForm()
        if form.validate_on_submit():
            
            
            new_theatre = Theatre(name=form.name.data, place_id=form.place.data.id, photo = form.photo.data)
            db.session.add(new_theatre)
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addTheatre.html',user=user,form=form)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))



@app.route('/addScreen',methods=['GET','POST'])
@login_required
def addScreen():
    user = current_user
    id = current_user.id
    if id==1:
        form = AddScreenForm()
        if form.validate_on_submit():
            
            
            new_screen = Screen(number=form.number.data, theatre_id=form.theatre.data.id)
            db.session.add(new_screen)
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addScreen.html',user=user,form=form)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))



@app.route('/addTier',methods=['GET','POST'])
@login_required
def addTier():
    user = current_user
    id = current_user.id
    theatre = Theatre.query.order_by(Theatre.id).all()
    if id==1:
        form = AddTierForm()
        if form.validate_on_submit():
            
            
            new_tier = Tier(number=form.number.data, screen_id=form.screen.data.id, price = form.price.data)
            db.session.add(new_tier)
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addTier.html',user=user,form=form,theatre = theatre)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    


@app.route('/addSeats',methods=['GET','POST'])
@login_required
def addSeats():
    user = current_user
    id = current_user.id
    if id==1:
        form = AddSeatsForm()
        if form.validate_on_submit():
            rows = form.rows.data
            columns = form.columns.data
            
            for i in range(1,rows + 1 ):
                for j in range(1, columns + 1):
                    new_seat = Seats(codeRow=i, codeColumn=j ,Tier_id=form.tier.data.id,Screen_id = form.tier.data.screen_id )
                    db.session.add(new_seat)
                    db.session.commit()

            
            return redirect(url_for('updateSuccessfull'))
        return render_template('addSeats.html',user=user,form=form)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))



@app.route('/addShow',methods=['GET','POST'])
@login_required
def addShow():
    user = current_user
    theatre = Theatre.query.order_by(Theatre.id).all()
    
    id = current_user.id
    
    if id==1:
        form = AddShowForm()
        if form.validate_on_submit():
            
            
            new_show = Show(movie_id=form.movie.data.id,time =(form.time.data) ,screen_id=form.screen.data.id)
            db.session.add(new_show)
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addShow.html',user=user,form=form,theatre= theatre)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))

@app.route('/addMovie',methods=['GET','POST'])
@login_required
def addMovie():
    user = current_user
    id = current_user.id
    if id==1:
        form = AddMovieForm()
        if form.validate_on_submit():
            name = form.name.data
            info = form.info.data
            ratings = form.rating.data
            poster = form.poster.data
            new_movie = Movie(name=name,info=info,rating=ratings,poster=poster)
            db.session.add(new_movie)
            
            
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addMovie.html',user=user,form = form)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))





@app.route('/addMovieCast',methods=['GET','POST'])
@login_required
def addMovieCast():
    user = current_user
    id = current_user.id
    form = AddMovieCast()
    if id==1:
        if form.validate_on_submit():
            moviename = form.movie.data
            castname = form.cast.data

            movie = Movie.query.filter_by(name=moviename).first()
            cast = Cast.query.filter_by(firstname = castname).first()

            movie.casting.append(cast)
            
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        return render_template('addMovieCast.html',user=user,form=form)
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))


@app.route('/updateSuccessfull')
@login_required
def updateSuccessfull():
    user = current_user
    return render_template('updateSuccess.html', user = user)

@app.route('/showMovie',methods=['GET','POST'])
@login_required
def showMovie():
    user = current_user
    form = SearchForm()
    if form.validate_on_submit():
        movie_searched = form.searched.data
        
        
        movies = (Movie.query.filter(Movie.name.like('%'+movie_searched+'%'))).all()
    else: 
        movies = Movie.query.all()
    
    return render_template('movies.html',user=user,movies=movies,form=form)    

@app.route('/showStars',methods=['GET','POST'])
@login_required
def showStars():
    user = current_user
    form = SearchForm()
    if form.validate_on_submit():
        cast_searched = form.searched.data
        
        
        casts = (Cast.query.filter(Cast.firstname.like('%'+cast_searched+'%'))).all()
    else: 
        casts = Cast.query.all()
    
    return render_template('stars.html',user=user,casts=casts,form=form) 

@app.route('/showTheatres',methods=['GET','POST'])
@login_required
def showTheatres():
    user = current_user
    
    form = SearchForm()
    if form.validate_on_submit():
        theatre_searched = form.searched.data
        
        
        theatres = (Theatre.query.filter(Theatre.name.like('%'+theatre_searched+'%'))).all()
    else: 
        theatres = Theatre.query.all()
    return render_template('theatre.html',user=user,theatres=theatres,form=form) 




@app.route('/showTheatresShows/<int:theatre_id>',methods=['GET','POST'])
@login_required
def showTheatresShows(theatre_id):
    user = current_user
    screen_ids= Screen.query.filter_by(theatre_id=theatre_id).all()
    
    shows =[]
    for screen_id in screen_ids:
        dt_obj = datetime.now()
        titu = datetime.strptime(dt_obj.isoformat(' ', 'seconds'),"%Y-%m-%d %H:%M:%S")
        allshow = Show.query.filter_by(screen_id=screen_id.id ).all()
        for a in allshow:
            if a.time < titu:
                deleteTickets(a.id)
                db.session.delete(a)
                db.session.commit()
            else:
                shows.append(a)
    return render_template('theatreShows.html',user=user,shows=shows) 



@app.route('/bookSeats/<int:show_id>/<int:screen_id>',methods=['GET','POST'])
@login_required
def bookings(show_id,screen_id):
    
    user = current_user
    show= Show.query.filter_by(id=show_id).first()
    form = Bookings()
    already_booked_seats = show.SeatsBooked
    id_already_booked_seats = []
    for s in already_booked_seats:
        id_already_booked_seats.append(s.id)
    
    form.seat.query = Seats.query.filter(Seats.id.not_in(id_already_booked_seats) ).filter_by(Screen_id = screen_id) 
    
    seats_booked = form.seat.data
    numberOfSeatsBooked = len(seats_booked)
    if form.validate_on_submit():
        for i in range(numberOfSeatsBooked):
            ticket = Tickets(user_id=user.id ,seat_id=form.seat.data[i].id,show_id = show.id)
            db.session.add(ticket)
            db.session.commit()
        for i in range(numberOfSeatsBooked):
            Seats.query.filter_by(id = form.seat.data[i].id).first().booking.append(show)
            db.session.commit()
        
        db.session.commit()
        return render_template('ticketsbooked.html',user=user)
            
    avialable_seats=Seats.query.filter(Seats.id.not_in(id_already_booked_seats) ).filter_by(Screen_id = screen_id).count() 
    if avialable_seats == 0:
        return render_template('housefull.html',user = user)    
    dt_obj = datetime.now()
    
    t = show.time
    
    
    titu = datetime.strptime(dt_obj.isoformat(' ', 'seconds'),"%Y-%m-%d %H:%M:%S")
    
    if (t) < titu:
        
        for seat in show.SeatsBooked:
            db.session.delete(seat)
            db.session.commit()
        
        
    return render_template('bookings.html',user=current_user,form=form) 




@app.route('/Tickets')
@login_required
def tickets():
    user = current_user
    tickets = Tickets.query.filter_by(user_id = user.id)
    
    return render_template('tickets.html',user=user,tickets = tickets)



@app.route('/castInMovies/<int:cast_id>')
@login_required
def castInMovies(cast_id):
    user = current_user
    castMovies = ((Cast.query.filter_by(id=cast_id)).first()).casted
    return render_template('castInMovies.html',user = user, movies = castMovies)


@app.route('/MovieReviews/<int:movie_id>')
@login_required
def movieReviews(movie_id):
    user = current_user
    movie = Movie.query.filter_by(id = movie_id).first()
    reviews = Review.query.filter_by(movie_id = movie_id).all()
    return render_template('movieReviews.html',user=user,reviews = reviews, movie = movie)



@app.route('/reviewMovie/<int:movie_id>',methods=['GET','POST'])
@login_required
def reviewMovie(movie_id):
    form = ReviewForm()
    user = current_user
    if form.validate_on_submit():
        string1 = form.content.data
        polarity = TextBlob(string1).polarity
        subjectivity = TextBlob(string1).subjectivity
        
        sentiments = Sentiments.query.filter_by(movie_id= movie_id).first()
        if sentiments is not None:
            sentiment = Sentiments.query.filter_by(movie_id = movie_id).first()
            sentiment.polarity += polarity
            sentiment.subjectivity += subjectivity
            db.session.commit()
        else: 
            new_sentiment = Sentiments(movie_id=movie_id,subjectivity=subjectivity,polarity=polarity)
            db.session.add(new_sentiment)
            db.session.commit()
        new_review = Review(user_id=user.id,content=form.content.data,movie_id=movie_id)
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('reviewMovie.html',form=form,user=user)




@app.route('/updatePlace',methods=['GET','POST'])
@login_required
def updatePlace():
    user = current_user
    form = updatePlaceForm()     
    if user.id ==1 :
        if form.validate_on_submit():
            pin = form.pin.data
            place = Place.query.filter_by(pin = pin).first()
            place.state = form.state.data
            place.city = form.city.data
            
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    return render_template('updatePlace.html',user=user,form=form) 



@app.route('/updateTheatre/<int:theatre_id>',methods=['GET','POST'])
@login_required
def updateTheatre(theatre_id):
    user = current_user
    form = updateTheatreForm()     
    if user.id ==1 :
        if form.validate_on_submit():
            theatre = Theatre.query.filter_by(id = theatre_id).first()
            theatre.name = form.name.data
            theatre.photo = form.photo.data
            theatre.place = form.place.data
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    return render_template('updateTheatre.html',user=user,form=form) 




@app.route('/updateShow/<int:show_id>',methods=['GET','POST'])
@login_required
def updateShow(show_id):
    user = current_user
    form = updateShowForm()     
    if user.id ==1 :
        if form.validate_on_submit():
            show = Show.query.filter_by(id = show_id).first()
            show.screen_id = form.screen.data.id
            show.time = form.time.data
            show.movie_id = form.movie.data.id
            
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    return render_template('updateShow.html',user=user,form=form) 



@app.route('/updateMovie/<int:movie_id>',methods=['GET','POST'])
@login_required
def updateMovie(movie_id):
    user = current_user
         
    if user.id ==1 :
        if request.method == 'POST':
            movie = Movie.query.filter_by(id = movie_id).first()
            movie.name = request.form['name']
            movie.info = request.form['info']
            movie.ratings = request.form['ratings']
            movie.poster = request.form['link']
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    return render_template('updateMovie.html',user=user) 

@app.route('/updateCast/<int:cast_id>',methods=['GET','POST'])
@login_required
def updateCast(cast_id):
    user = current_user
    id = current_user.id
    if id==1:
        if request.method == 'POST':
            cast = Cast.query.filter_by(id = cast_id).first()
            cast.firstname = request.form['firstname']
            cast.lastname = request.form['lastname']
            cast.type = request.form['type']
            cast.photo = request.form['link']
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
        
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    return render_template('updateCast.html',user=user)

@app.route('/updateScreen/<int:screen_id>',methods=['GET','POST'])
@login_required
def updateScreen(screen_id):
    user = current_user
    form = updateScreenForm()     
    if user.id ==1 :
        if form.validate_on_submit():
            screen = Screen.query.filter_by(id = screen_id).first()
            screen.number = form.number.data
            screen.theatre_id = form.theatre.data.id
            db.session.commit()
            return redirect(url_for('updateSuccessfull'))
    else:
        flash("Sorry you don't hava autorization to access this page.")
        return redirect(url_for('dashboard'))
    return render_template('updateScreen.html',user=user,form=form) 

@app.route('/deleteMovie/<int:movie_id>',methods=['GET','POST'])
@login_required
def deleteMovie(movie_id):
    user = current_user
    if user.id ==1:
        movie = Movie.query.filter_by(id = movie_id).first()
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('showMovie'))
    
@app.route('/deleteCast/<int:cast_id>',methods=['GET','POST'])
@login_required
def deleteCast(cast_id):
    user = current_user
    if user.id ==1:
        cast = Cast.query.filter_by(id = cast_id).first()
        db.session.delete(cast)
        db.session.commit()
        return redirect(url_for('showStars'))
    
@app.route('/deleteTheatre/<int:theatre_id>',methods=['GET','POST'])
@login_required
def deleteTheatre(theatre_id):
    user = current_user
    if user.id ==1:
        theatre = Theatre.query.filter_by(id = theatre_id).first()
        db.session.delete(theatre)
        db.session.commit()
        return redirect(url_for('showTheatres'))  

@app.route('/deleteShow/<int:show_id>',methods=['GET','POST'])
@login_required
def deleteShow(show_id):
    user = current_user
    if user.id ==1:
        show = Show.query.filter_by(id = show_id).first()
        for seat in show.SeatsBooked:
            db.session.delete(seat)
            db.session.commit()
        deleteTickets(show_id)
        db.session.delete(show)
        db.session.commit()
        return redirect(url_for('showTheatres'))

@app.route('/deleteScreen/<int:screen_id>',methods=['GET','POST'])
@login_required
def deleteScreen(screen_id):
    user = current_user
    if user.id ==1:
        screen = Screen.query.filter_by(id = screen_id).first()
        tiers = Tier.query.filter_by(screen_id=screen_id).all()
        shows = Show.query.filter_by(screen_id=screen_id).all()
        for show in shows:
            deleteShow(show.id)
            
        for tier in tiers:
            db.session.delete(tier)
            db.session.commit()
        db.session.delete(screen)
        db.session.commit()
        return redirect(url_for('showTheatres'))

@app.route('/deleteTickets/<int:show_id>',methods=['GET','POST'])
@login_required
def deleteTickets(show_id):
    user = current_user
    if user.id ==1:
        tickets = Tickets.query.filter_by(show_id = show_id).all()
        for ticket in tickets:
            db.session.delete(ticket)
            db.session.commit()
        return redirect(url_for('showTheatres'))




@app.route('/topmovies')
@login_required
def topmovies():
    user = current_user
    top_movie_sentiments = Sentiments.query.order_by(Sentiments.polarity.desc()).limit(10)

    movies = []
    for sentiment in top_movie_sentiments:
        top_movie = Movie.query.filter_by(id = sentiment.movie_id).first()
        movies.append(top_movie)
    form = SearchForm()
    if form.validate_on_submit():
        movie_searched = form.searched.data
        
        
        movies = (Movie.query.filter(Movie.name.like('%'+movie_searched+'%'))).all()
    
    
    return render_template('movies.html',user=user,movies=movies,form=form)   
    

if __name__ == '__main__':
   with app.app_context():
    db.create_all()
   app.run(debug = True)
    
