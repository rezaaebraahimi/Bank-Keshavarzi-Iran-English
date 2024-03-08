import os
from flask import Flask, flash, render_template, request,redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from dotenv import load_dotenv
from persiantools.jdatetime import JalaliDate

app=Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"]= (os.environ.get("SECRET_KEY"))
app.config['SQLALCHEMY_DATABASE_URI']= (os.environ.get("SQLALCHEMY_DATABASE_URI"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'

db=SQLAlchemy(app)
app.app_context().push()
Session(app) 


class Property(db.Model):
    __tablenme__ = 'property'
    id=db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(45), db.ForeignKey('user.CenterCode'))
    cardType = db.Column(db.String(45), db.ForeignKey('card.typeOfCards'))
    date_add=db.Column(db.Date, default=JalaliDate.today())
    supply = db.Column(db.Integer,default=0, nullable=False)   
    
    def __repr__(self):
        return f'Property("{self.user_code}","{self.cardType}","{self.supply}")' 


class User(db.Model):
    __tablename__ = 'user'
    id=db.Column(db.Integer, primary_key=True)
    CenterName=db.Column(db.String(100), nullable=False)
    CenterCode=db.Column(db.String(45), nullable=False)
    username=db.Column(db.String(45), nullable=False)
    password=db.Column(db.String(45), nullable=False)
    sum_supply = db.Column(db.Integer,default=0, nullable=False)
    date_added=db.Column(db.Date, default=JalaliDate.today())
    status=db.Column(db.Integer,default=0, nullable=False)
    owner = db.relationship('Card', secondary='property')

    def __repr__(self):
        return f'User("{self.id}","{self.CenterName}","{self.CenterCode}","{self.username}","{self.status}","{self.owner}")'


class Admin(db.Model):
    __tablename__= 'admin'
    id=db.Column(db.Integer, primary_key=True)
    admin_user=db.Column(db.String(45), nullable=False)
    admin_pass=db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return f'Admin("{self.admin_user}","{self.id}")'




class Card(db.Model):
    __tablename__ = 'card'
    id=db.Column(db.Integer, primary_key=True)
    typeOfCards = db.Column(db.String(45), nullable=False)
    asset = db.relationship('User', secondary='property')
    _type = db.relationship('Recieve')
    def __repr__(self):
        return f'Card("{self.typeOfCards}","{self.id}","{self.asset}",""{self._type})'
    

class Recieve(db.Model):
    __tablename__ = 'recieve'
    id=db.Column(db.Integer, primary_key=True)
    admin_supply  = db.Column(db.Integer, default=0, nullable=False)
    recieve_date = db.Column(db.Date, default=JalaliDate.today())
    _type = db.Column(db.String(45), db.ForeignKey('card.typeOfCards'))
    
    def __repr__(self):
        return f'Recieve("{self.id}","{self.admin_supply}","{self.recieve_date}","{self._type}")'



@app.route('/')
def index():
    return render_template('index.html',title="")


@app.route('/admin/',methods=["POST","GET"])
def adminIndex():
    if request.method == 'POST':
        admin_user = request.form.get('admin_user')
        admin_pass = request.form.get('admin_pass')
        if admin_user=="" and admin_pass=="":
            flash('لطفا تمامی موارد را کامل کنید','error')
            return redirect('/admin/')
        else:
            admins=Admin().query.filter_by(admin_user=admin_user).first()
            admins_p=Admin().query.filter_by(admin_pass=admin_pass).first()
            if admins and admins_p:
                session['admin_id']=admins.id
                session['admin_name']=admins.admin_user
                flash('ورود موفقیت آمیز بود','message')
                return redirect('/admin/dashboard')
            else:
                flash('نام کاربری یا رمز عبور اشتباه است','error')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html',title="ورود مدیریت")


@app.route('/admin/dashboard', methods=["POST","GET"])
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    else:
        if request.method == 'POST':
            usercode = request.form.get('usercode')
            return redirect(url_for('adminGetDetails', usercode=usercode))
        else:
            users=User.query.all()
            for user in users:
                c_user = user.CenterCode
                all_pro = Property.query.all()
                for pro in all_pro:
                    if pro.user_code == c_user:
                        infos = Property.query.filter_by(user_code=c_user)
            return render_template('admin/dashboard.html',title="میزکار مدیریت",users=users,infos=infos)
        

@app.route('/admin/get-all-details/', methods=["POST","GET"])
def adminGetDetails():
    if not session.get('admin_id'):
        return redirect('/admin/')
    usercode = request.args.get('usercode')
    users=User.query.all()
    for user in users:
        if user.CenterCode == usercode:
            all_pro = Property.query.all()
            for pro in all_pro:
                if pro.user_code == usercode:
                    infos = Property.query.filter_by(user_code=usercode)
                    return render_template('admin/admin-get-details.html',title=" جزئیات موجودی",users=users,infos=infos,usercode=usercode)
        
    
@app.route('/admin/addCardToUser', methods=["POST","GET"])
def addCardToUser():
    users = User.query.all()
    types = Card.query.all()
    if request.method == 'POST':
        CenterCode = request.form.get('CenterCode')
        sendToUser = request.form.get('sendToUser')
        typeOfCards = request.form.get('typeOfCards')
        Checker = Property.query.filter_by(user_code=CenterCode,cardType=typeOfCards ).first()
        if sendToUser == '':
            flash('لطفا با دقت کامل کنید','error')
            return redirect('/admin/addCardToUser')
        elif Checker:
            sum = Property.supply + sendToUser
            Checker.supply = sum
            Checker.date_add = JalaliDate.today()
            User.query.filter_by(CenterCode=CenterCode).update(dict(date_added=JalaliDate.today()))

            db.session.commit()
            flash('تخصیص داده شد','message')
            return redirect('/admin/addCardToUser')          

        else:
            _property = Property(user_code=CenterCode, cardType=typeOfCards, supply=sendToUser, date_add=JalaliDate.today())
            User.query.filter_by(CenterCode=CenterCode).update(dict(date_added=JalaliDate.today()))
            db.session.add(_property)
            db.session.commit()
            flash('تخصیص داده شد','message')
            return redirect('/admin/addCardToUser')
    else:
        return render_template('admin/add-card-to-user.html', title='توزیع کارت',users=users,types=types)
    


@app.route('/admin/recieve', methods=["POST","GET"])
def recieve():
    if not session.get('admin_id'):
        return redirect('/admin/')
    types = Card.query.all()
    _recieve = Recieve.query.all()
    if request.method == 'POST':
        adminRecieve = request.form.get('adminRecieve')
        typeOfCards = request.form.get('typeOfCards')
        Checker = Recieve.query.filter_by(_type=typeOfCards).first()
        if adminRecieve == '':
            flash('لطفا با دقت کامل کنید','error')
            return redirect('/admin/recieve')
        elif typeOfCards == Checker:
            sum = Recieve.admin_supply + adminRecieve
            _recieve.admin_supply = sum
            Recieve.query.filter_by(_type=typeOfCards).update(dict(recieve_date=JalaliDate.today()))
            db.session.commit()
            flash('توسط خزانه دریافت شد','message')
            return redirect('/admin/addCardToUser')  
        else :
            new_recieve = Recieve(admin_supply = adminRecieve, recieve_date = JalaliDate.today(), _type = typeOfCards)
            db.session.add(new_recieve)
            db.session.commit()
            flash('توسط خزانه دریافت شد','message')
            return redirect('/admin/recieve')          

    else:
        return render_template('admin/recieve.html', title='توزیع کارت',_recieve=_recieve,types=types)
    
    



@app.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.CenterCode.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='لیست کاربران',users=users)
    else:
        users=User.query.all()
        
        return render_template('admin/all-user.html',title=' لیست کابران',users=users)


@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    User().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('تایید موفقیت آمیز بود','message')
    return redirect('/admin/get-all-user')


@app.route('/admin/disapprove-user/<int:id>')
def adminDisApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    User().query.filter_by(id=id).update(dict(status=0))
    db.session.commit()
    flash('کاربر مورد نظر تعلیق شد','message')
    return redirect('/admin/get-all-user')


@app.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        admin_user=request.form.get('admin_user')
        admin_pass=request.form.get('admin_pass')
        if admin_user == "" or admin_pass=="":
            flash('لطفا جای خالی را کامل کنید','error')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(admin_user=admin_user).update(dict(admin_pass=admin_pass))
            db.session.commit()
            flash('تغییر رمز عبور مدیریت موفقیت آمیز بود','message')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',
                               title='تغییر رمز عبور مدیریت',admin=admin)


@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')


@app.route('/user/',methods=["POST","GET"])
def userIndex():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        users=User().query.filter_by(username=username).first()
        users_p=User().query.filter_by(password=password).first()
        if users and users_p:
            is_approve=User.query.filter_by(id=users.id).first()
            if is_approve.status == 0:
                flash('شما توسط مدیریت تایید نشده اید','error')
                return redirect('/user/')
            else:
                session['user_id']=users.id
                session['username']=users.username
                flash('ورود موفقیت آمیز بود ','message')
                return redirect('/user/dashboard')
        else:
            flash('نام کاربری یا رمز عبور نادرست است ','error')
            return redirect('/user/')
    else:
        return render_template('user/index.html',title="ورود اعضا")


@app.route('/user/signup',methods=['POST','GET'])
def userSignup():
    types = Card.query.all()
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=='POST':
        CenterName=request.form.get('CenterName')
        CenterCode=request.form.get('CenterCode')
        username=request.form.get('username')
        password=request.form.get('password')

        if CenterName =="" or CenterCode=="" or password=="" or username=="":
            flash('لطفا تمامی موارد را تکمیل کنید','error')
            return redirect('/user/signup')
        else:
            is_username=User().query.filter_by(username=username).first()
            if is_username:
                flash('نام کاربری قبلا ثبت شده','error')
                return redirect('/user/signup')
            else:
                user=User(CenterName=CenterName,CenterCode=CenterCode,password=password,username=username)
                db.session.add(user)
                db.session.commit()
                for _type in types:
                    c_type = _type.typeOfCards
                    _property = Property(user_code=CenterCode, cardType=c_type, supply=0)
                    db.session.add(_property)
                    db.session.commit()   
                
                flash('بعد از تایید توسط مدیریت میتوانید دسترسی به سامانه برای شما آزاد میشود','message')
                return redirect('/user/')
    else:
        return render_template('user/signup.html',title="ثبتنام اعضا")


@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User().query.filter_by(id=id).first()
    return render_template('user/dashboard.html',title="میزکار کاربر ",users=users)


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
            flash('لطفا تمام موارد را کامل کنید','error')
            return redirect('/user/change-password')
        else:
            users=User.query.filter_by(username=username).first()
            if users:

               User.query.filter_by(username=username).update(dict(password=password))
               db.session.commit()
               flash('رمز عبور تغییر کرد','message')
               return redirect('/user/change-password')
            else:
                flash('نام کاربری نادرست است','error')
                return redirect('/user/change-password')

    else:
        return render_template('user/change-password.html',title="تغییر رمز عبور")


@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User.query.get(id)
    if request.method == 'POST':

        CenterName=request.form.get('CenterName')
        CenterCode=request.form.get('CenterCode')
        username=request.form.get('username')
        if CenterName =="" or CenterCode=="" or username=="":
            flash('لطفا تمام موارد را کامل کنید','error')
            return redirect('/user/update-profile')
        else:
            session['username']=None
            User.query.filter_by(id=id).update(dict(CenterName=CenterName,CenterCode=CenterCode,username=username))
            db.session.commit()
            session['username']=username
            flash('پروفایل بروزرسانی شد','message')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html',
                               title="بروز رسانی پروفایل",users=users)

if __name__=="__main__":
    app.run(debug=True)