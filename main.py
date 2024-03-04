import os
from flask import Flask, flash, render_template, request,redirect, session
from flask_session import Session
from flask_bcrypt import Bcrypt

app=Flask(__name__)

app.config['MySQL_DATABASE_URI']="mysql://username:password@localhost/db_name"
app.config["SECRET_KEY"]='65b0b774279de460f1cc5c92'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
Session(app)

# User Class
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    CenterName=db.Column(db.String(255), nullable=False)
    CenterCode=db.Column(db.String(255), nullable=False)
    username=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)
    # date_added = db.Column(db.Datetime, default=datetime.utcnow)
    status=db.Column(db.Integer,default=0, nullable=False)

    def __repr__(self):
        return f'User("{self.id}","{self.CenterName}","{self.CenterCode}","{self.username}","{self.status}")'

# create admin Class
class Admin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}","{self.id}")'

# create table
db.create_all()

# insert admin data one time only one time insert this data
# latter will check the condition
admin=Admin(username='Rezaadmin',password=bcrypt.generate_password_hash('Admin',10))
db.session.add(admin)
db.session.commit()

# main index 
@app.route('/')
def index():
    return render_template('index.html',title="")


# admin loign
@app.route('/admin/',methods=["POST","GET"])
def adminIndex():
    # chect the request is post or not
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username=="" and password=="":
            flash('لطفا تمامی موارد را کامل کنید','خطا')
            return redirect('/admin/')
        else:
            # login admin by username 
            admins=Admin().query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password,password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('ورود موفقیت آمیز بود','درود')
                return redirect('/admin/dashboard')
            else:
                flash('نام کاربری یا رمز عبور اشتباه است','خطا')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html',title="Admin Login")

# admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    totalUser=User.query.count()
    totalApprove=User.query.filter_by(status=1).count()
    NotTotalApprove=User.query.filter_by(status=0).count()
    return render_template('admin/dashboard.html',title="Admin Dashboard",totalUser=totalUser,totalApprove=totalApprove,NotTotalApprove=NotTotalApprove)

# admin get all user 
@app.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.username.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-user.html',title='Approve User',users=users)

@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    User().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('تایید موفقیت آمیز بود','درود')
    return redirect('/admin/get-all-user')

# change admin password
@app.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('لطفا جای خالی را کامل کنید','خطا')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=bcrypt.generate_password_hash(password,10)))
            db.session.commit()
            flash('تغییر رمز عبور مدیریت موفقیت آمیز بود','درود')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)

# admin logout
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')
# -------------------------user area----------------------------


# User login
@app.route('/user/',methods=["POST","GET"])
def userIndex():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=="POST":
        # get the name of the field
        username=request.form.get('username')
        password=request.form.get('password')
        # check user exist in this username or not
        users=User().query.filter_by(username=username).first()
        if users and bcrypt.check_password_hash(users.password,password):
            # check the admin approve your account are not
            is_approve=User.query.filter_by(id=users.id).first()
            # first return the is_approve:
            if is_approve.status == 0:
                flash('شما توسط مدیریت تایید نشده اید','خطا')
                return redirect('/user/')
            else:
                session['user_id']=users.id
                session['username']=users.username
                flash('ورود موفقیت آمیز بود ','درود')
                return redirect('/user/dashboard')
        else:
            flash('نام کاربری یا رمز عبور نادرست است ','خطا')
            return redirect('/user/')
    else:
        return render_template('user/index.html',title="User Login")

# User Register
@app.route('/user/signup',methods=['POST','GET'])
def userSignup():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=='POST':
        # get all input field name
        CenterName=request.form.get('CenterName')
        CenterCode=request.form.get('CenterCode')
        username=request.form.get('username')
        password=request.form.get('password')
        # check all the field is filled are not
        if CenterName =="" or CenterCode=="" or password=="" or username=="":
            flash('لطفا تمامی موارد را تکمیل کنید','خطا')
            return redirect('/user/signup')
        else:
            is_username=User().query.filter_by(username=username).first()
            if is_username:
                flash('نام کاربری قبلا ثبت شده','خطا')
                return redirect('/user/signup')
            else:
                hash_password=bcrypt.generate_password_hash(password,10)
                user=User(CenterName=CenterName,CenterCode=CenterCode,password=hash_password,username=username)
                db.session.add(user)
                db.session.commit()
                flash('بعد از تایید توسط مدیریت میتوانید دسترسی به سامانه برای شما آزاد میشود','منتظر بمانید')
                return redirect('/user/')
    else:
        return render_template('user/signup.html',title="User Signup")


# user dashboard
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User().query.filter_by(id=id).first()
    return render_template('user/dashboard.html',title="User Dashboard",users=users)

# user logout
@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user/')

    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/user/')

@app.route('/user/change-password',methods=["POST","GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password == "":
            flash('لطفا تمام موارد را کامل کنید','خطا')
            return redirect('/user/change-password')
        else:
            users=User.query.filter_by(username=username).first()
            if users:
               hash_password=bcrypt.generate_password_hash(password,10)
               User.query.filter_by(username=username).update(dict(password=hash_password))
               db.session.commit()
               flash('رمز عبور تغییر کرد','درود')
               return redirect('/user/change-password')
            else:
                flash('نام کاربری نادرست است','خطا')
                return redirect('/user/change-password')

    else:
        return render_template('user/change-password.html',title="Change Password")

# user update profile
@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User.query.get(id)
    if request.method == 'POST':
        # get all input field name
        CenterName=request.form.get('CenterName')
        CenterCode=request.form.get('CenterCode')
        username=request.form.get('username')
        if CenterName =="" or CenterCode=="" or username=="":
            flash('لطفا تمام موارد را تکمیل کنید','خطا')
            return redirect('/user/update-profile')
        else:
            session['username']=None
            User.query.filter_by(id=id).update(dict(CenterName=CenterName,CenterCode=CenterCode,username=username))
            db.session.commit()
            session['username']=username
            flash('پروفایل بروزرسانی شد','درود')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html',title="Update Profile",users=users)

if __name__=="__main__":
    app.run(debug=True)