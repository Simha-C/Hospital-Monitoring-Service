from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user


# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='simha'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hma'
db=SQLAlchemy(app)



# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    usertype=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))

class Doclogs(db.Model):
    trigid=db.Column(db.Integer,primary_key=True)
    docid=db.Column(db.Integer)
    docname=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))




# here we will pass endpoints and run the fuction
@app.route('/')
def index():
    return render_template('index.html')
    


@app.route('/doctors',methods=['POST','GET'])
def doctors():

    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')

        query=db.engine.execute(f"INSERT INTO `doctors` (`email`,`doctorname`,`dept`) VALUES ('{email}','{doctorname}','{dept}')")
        flash("Information is Stored","primary")

    return render_template('doctor.html')



@app.route('/patients',methods=['POST','GET'])
@login_required
def patient():
    doct=db.engine.execute("SELECT * FROM `doctors`")

    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        subject="HOSPITAL MANAGEMENT SYSTEM"
        query=db.engine.execute(f"INSERT INTO `patients` (`email`,`name`, `gender`,`slot`,`disease`,`time`,`date`,`dept`,`number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{time}','{date}','{dept}','{number}')")
        flash("Booking Confirmed","info")


    return render_template('patient.html',doct=doct)


@app.route('/bookings')
@login_required
def bookings(): 
    em=current_user.email
    if current_user.usertype=="Doctor":
        query=db.engine.execute(f"SELECT * FROM `patients`")
        return render_template('booking.html',query=query)
    else:
        query=db.engine.execute(f"SELECT * FROM `patients` WHERE email='{em}'")
        return render_template('booking.html',query=query)

@app.route('/doclogs')
@login_required
def doclogs():
    query=db.engine.execute(f"SELECT * FROM `doclogs`")
    return render_template('doclogs.html',query=query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/availdocs')
@login_required
def availdocs():
    query=db.engine.execute(f"SELECT * FROM `user`")
    return render_template('availdocs.html',query=query)

@app.route('/availpat')
@login_required
def availpat():
    query=User.query.filter_by(usertype="Doctor")
    return render_template('availpat.html',query=query)


@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        db.engine.execute(f"UPDATE `patients` SET `email` = '{email}', `name` = '{name}', `gender` = '{gender}', `slot` = '{slot}', `disease` = '{disease}', `time` = '{time}', `date` = '{date}', `dept` = '{dept}', `number` = '{number}' WHERE `patients`.`pid` = {pid}")
        flash("Slot is Updates","success")
        return redirect('/bookings')
    
    return render_template('edit.html',posts=posts)


@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    db.engine.execute(f"DELETE FROM `patients` WHERE `patients`.`pid`={pid}")
    flash("Slot Deleted Successful","danger")
    return redirect('/bookings')






@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        usertype=request.form.get('usertype')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`usertype`,`email`,`password`) VALUES ('{username}','{usertype}','{email}','{encpassword}')")
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    





    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'DB database is Connected'
    except:
        return 'DB is not Connected'
    

@app.route('/details')
@login_required
def details():
    # posts=Trigr.query.all()
    posts=db.engine.execute("SELECT * FROM `trigr`")
    return render_template('trigers.html',posts=posts)


@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    if request.method=="POST":
        query=request.form.get('search')
        dept=Doctors.query.filter_by(dept=query).first()
        name=Doctors.query.filter_by(doctorname=query).first()
        if name:
            flash("Doctor avaiable","success")
        elif not name:
            if dept:
                flash("Department available","info")
            elif not dept:
                flash("Department is not available","danger")
            else:
                flash("Doctor not available","danger")    
    return render_template('index.html')






app.run(debug=True)    

