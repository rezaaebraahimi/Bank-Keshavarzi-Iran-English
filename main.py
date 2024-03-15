import os
from flask import Flask, flash, render_template, request, redirect, session, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from dotenv import load_dotenv
from persiantools.jdatetime import JalaliDate
import json
import pandas as pd
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor


executor = ThreadPoolExecutor(max_workers=1)

app=Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"]= (os.environ.get("SECRET_KEY"))
app.config['SQLALCHEMY_DATABASE_URI']= (os.environ.get("SQLALCHEMY_DATABASE_URI"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
app.config['FAVICON'] = os.path.join(os.getcwd(), 'static', 'favicon.ico')

db=SQLAlchemy(app)
app.app_context().push()
Session(app) 


class Admin(db.Model):
    __tablename__= 'admin'
    id = db.Column(db.Integer, primary_key=True)
    admin_user = db.Column(db.String(45), nullable=False)
    admin_pass = db.Column(db.String(128), nullable=False) 


class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(45), db.ForeignKey('user.CenterCode'), nullable=False)  
    cardType = db.Column(db.String(45), db.ForeignKey('card.typeOfCards'), nullable=False)
    date_add = db.Column(db.Date, default=JalaliDate.today())
    supply = db.Column(db.Integer, default=0, nullable=False)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    CenterName = db.Column(db.String(100), nullable=False)
    CenterCode = db.Column(db.String(45), nullable=False, unique=True)
    personal = db.Column(db.String(45), nullable=False)
    personalCode = db.Column(db.String(45), nullable=False, unique=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False) 
    sum_supply = db.Column(db.Integer, default=0, nullable=False)
    date_added = db.Column(db.Date, default=JalaliDate.today())
    status = db.Column(db.Integer, default=0, nullable=False)
    properties = db.relationship('Property', backref='user', lazy=True)  


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    typeOfCards = db.Column(db.String(45), nullable=False)
    properties = db.relationship('Property', backref='card', lazy=True)  
    receives = db.relationship('Receive', backref='card', lazy=True)  


class Receive(db.Model):
    __tablename__ = 'receive'  
    id = db.Column(db.Integer, primary_key=True)
    admin_supply = db.Column(db.Integer, default=0, nullable=False)
    recieve_date = db.Column(db.Date, default=JalaliDate.today())
    cardType = db.Column(db.String(45), db.ForeignKey('card.typeOfCards'), nullable=False) 


class Blogpost(db.Model):
    __tablename__ = 'blogpost'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.Date)
    content = db.Column(db.Text)


class UserRequest(db.Model):
    __tablename__ = 'userrequest'
    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.String(45), db.ForeignKey('user.CenterCode'))
    card_type = db.Column(db.String(45))
    supply_quantity = db.Column(db.Integer)
    date_added = db.Column(db.Date, default=JalaliDate.today())
    status = db.Column(db.String(45), default='Pending') 




@app.route('/')
def index():
    return render_template('index.html',title="")


@app.route('/admin/', methods=["POST", "GET"])
def admin_index():
    if request.method == 'POST':
        admin_user = request.form.get('admin_user')
        admin_pass = request.form.get('admin_pass')
        if not admin_user or not admin_pass:
            flash('لطفا تمامی موارد را کامل کنید', 'error')
            return redirect('/admin/')
        else:
            admin = Admin.query.filter_by(admin_user=admin_user, admin_pass=admin_pass).first()
            if admin:
                session['admin_id'] = admin.id
                session['admin_name'] = admin.admin_user
                flash('ورود موفقیت آمیز بود', 'message')
                return redirect('/admin/dashboard')
            else:
                flash('نام کاربری یا رمز عبور اشتباه است', 'error')
                return redirect('/admin/')
    else:
        return render_template('admin/index.html', title="ورود مدیریت")



@app.route('/admin/dashboard', methods=["POST", "GET"])
def admin_dashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    else:
        if request.method == 'POST':
            user_code = request.form.get('usercode')
            return redirect(url_for('adminGetDetails', usercode=user_code))
        else:
            users = User.query.all()
            all_pro = Property.query.all()
            if all_pro and users:
                infos = []
                for user in users:
                    c_user = user.CenterCode
                    for pro in all_pro:
                        if pro.user_code == c_user:
                            infos.append(Property.query.filter_by(user_code=c_user))
                return render_template('admin/dashboard.html', title="میزکار مدیریت", users=users, infos=infos)
            else:
                return render_template('admin/empty-dashboard.html', title="میزکار مدیریت")



@app.route('/admin/get-all-details/', methods=["POST","GET"])
def adminGetDetails():
    if not session.get('admin_id'):
        return redirect('/admin/')
    usercode = request.args.get('usercode')
    users = User.query.filter_by(CenterCode=usercode).all()
    for user in users:
        if user.CenterCode == usercode:
            infos = Property.query.filter_by(user_code=usercode).all()
            return render_template('admin/admin-get-details.html', title="جزئیات موجودی", users=users, infos=infos)
   

def is_digit_string(s):
    for char in s:
        if not (ord('0') <= ord(char) <= ord('9')):
            return False
    return True

def is_number_string(s):
    if not isinstance(s, str):
        return False
    return is_digit_string(s)
  
    
@app.route('/admin/addCardToUser', methods=["POST","GET"])
def addCardToUser():
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    users = User.query.all()
    types = Card.query.all()
    
    if request.method == 'POST':
        CenterCode = request.form.get('CenterCode')
        sendToUser = request.form.get('sendToUser')
        typeOfCards = request.form.get('typeOfCards')

        if not CenterCode or not sendToUser or not typeOfCards or is_number_string(CenterCode) == False or is_number_string(sendToUser) == False:
            flash('لطفاً مقادیر را به درستی وارد کنید', 'error')
            return redirect('/admin/addCardToUser')
        
        sendToUser = int(sendToUser)
        CenterCode = int(CenterCode)
        
        adminChecker = Receive.query.filter_by(cardType=typeOfCards).first()
        
        if not adminChecker or adminChecker.admin_supply < sendToUser:
            flash('مقدار وارد شده در خزانه موجود نیست', 'error')
            return redirect('/admin/addCardToUser')
        
        
        Checker = Property.query.filter_by(user_code=CenterCode,cardType=typeOfCards).first()
        if Checker:
            adminChecker.admin_supply -= sendToUser
            Checker.supply += sendToUser
            Checker.date_add = JalaliDate.today()
            User.query.filter_by(CenterCode=CenterCode).update({'date_added': JalaliDate.today(), 'sum_supply': User.sum_supply + sendToUser})
        else:
            adminChecker.admin_supply -= sendToUser
            User.query.filter_by(CenterCode=CenterCode).update({'date_added': JalaliDate.today(), 'sum_supply': User.sum_supply + sendToUser})
            _property = Property(user_code=CenterCode, cardType=typeOfCards, supply=sendToUser, date_add=JalaliDate.today())
            db.session.add(_property)
        
        db.session.commit()
        flash('تخصیص داده شد', 'message')
        return redirect('/admin/addCardToUser')

    return render_template('admin/add-card-to-user.html', title='توزیع کالا',users=users,types=types)
    


@app.route('/admin/recieve', methods=["POST","GET"])
def recieve():
    if not session.get('admin_id'):
        return redirect('/admin/')
    
    types = Card.query.all()
    _recieve = Receive.query.all()  
    if request.method == 'POST':
        adminRecieve = request.form.get('adminRecieve')
        typeOfCards = request.form.get('typeOfCards')
        

        if not adminRecieve or not typeOfCards or not is_number_string(adminRecieve):
            flash('لطفا فرم را با دقت کامل کنید','error')
            return redirect('/admin/recieve')
        
        adminRecieve = int(adminRecieve)
        Checker = Receive.query.filter_by(cardType=typeOfCards).first()
        
        if Checker:
            sum = Checker.admin_supply + adminRecieve
            Checker.admin_supply = sum
            Checker.recieve_date = JalaliDate.today()
            db.session.commit()
        else:
            new_recieve = Receive(admin_supply=adminRecieve, recieve_date=JalaliDate.today(), cardType=typeOfCards)
            db.session.add(new_recieve)
            db.session.commit()
        
        flash('توسط خزانه دریافت شد', 'message')
        return redirect('/admin/recieve') 
    else:
        return render_template('admin/recieve.html', title=' خزانه',_recieve=_recieve,types=types)
    

@app.route('/admin/add-card-type', methods=["POST","GET"])
def addcardtype():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        card_type = request.form.get('card_type')
        if card_type:
            new_card = Card(typeOfCards=card_type)
            db.session.add(new_card)
            db.session.commit()
            flash('کالای جدید با موفقیت به خزانه اضافه شد','message')    
            return redirect('/admin/recieve')
        else:
            flash('لطفا نام کالا را وارد کنید','error')
            return redirect('/admin/recieve')
        
        
        
@app.route('/admin/remove-card-type', methods=["POST","GET"])
def removecardtype():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if request.method== "POST":
        card_type_remove = request.form.get('card_type_remove')
        if card_type_remove:
            card_to_delete  = Card.query.filter_by(typeOfCards=card_type_remove).first()
            card_delete = Receive.query.filter_by(cardType=card_type_remove).first()
            db.session.delete(card_delete)
            db.session.commit()
            db.session.delete(card_to_delete)
            db.session.commit()
            flash('کالا با موفقیت از خزانه حذف شد','message')    
            return redirect('/admin/recieve')
        else:
            flash('لطفا نام کالا را وارد کنید','error')
            return redirect('/admin/recieve')
        


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
    else:
        User().query.filter_by(id=id).update(dict(status=1))
        db.session.commit()
        flash('تایید موفقیت آمیز بود','message')
        return redirect('/admin/get-all-user')


@app.route('/admin/disapprove-user/<int:id>')
def adminDisApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin/')
    else:
        User().query.filter_by(id=id).update(dict(status=0))
        db.session.commit()
        flash('کاربر مورد نظر تعلیق شد','message')
        return redirect('/admin/get-all-user')


@app.route('/admin/change-admin-password', methods=["POST", "GET"])
def adminChangePassword():
    admin = Admin.query.get(1)
    if request.method == 'POST':
        admin_user = request.form.get('admin_user')
        admin_pass = request.form.get('admin_pass')
        if not admin_user or not admin_pass:
            flash('لطفاً جای خالی را کامل کنید', 'error')
            return redirect('/admin/change-admin-password')
        else:
            admin.admin_pass = admin_pass
            db.session.commit()
            flash('تغییر رمز عبور مدیریت موفقیت آمیز بود', 'message')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',
                               title='تغییر رمز عبور مدیریت', admin=admin)


@app.route('/admin/add')
def add():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('blog/add.html',posts=posts)

@app.route('/blog/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']
    if title and subtitle and author and content:
        post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=JalaliDate.today())
        db.session.add(post)
        db.session.commit()
        return redirect('/admin/add')
    else:
        flash('لطفا تمامی موارد را کامل کنید','error')
        return redirect('/admin/add')

@app.route('/blog/allPosts')
def allPosts():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('blog/all-posts.html', posts=posts)

@app.route('/blog/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('blog/post.html', post=post)


@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    else:
        session['admin_id'] = None
        session['admin_name'] = None
        return redirect('/')


@app.route('/user/', methods=["POST", "GET"])
def userIndex():
    if session.get('user_id'):
        return redirect('/user/dashboard')

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            if user.status == 0:
                flash('شما توسط مدیریت تایید نشده اید', 'error')
                return redirect('/user/')
            else:
                session['user_id'] = user.id
                session['username'] = user.username
                flash('ورود موفقیت آمیز بود', 'message')
                return redirect('/user/dashboard')
        else:
            flash('نام کاربری یا رمز عبور نادرست است', 'error')
            return redirect('/user/')
    else:
        return render_template('user/index.html', title="ورود اعضا")


@app.route('/user/signup',methods=['POST','GET'])
def userSignup():
    types = Card.query.all()
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=='POST':
        CenterName=request.form.get('CenterName')
        CenterCode=request.form.get('CenterCode')
        personal=request.form.get('personal')
        personalCode=request.form.get('personalCode')
        username=request.form.get('username')
        password=request.form.get('password')

        if CenterName =="" or CenterCode=="" or password=="" or username=="" or personal=="" or personalCode=="" or  not is_number_string(CenterCode) or not is_number_string(personalCode):
            flash('لطفا تمامی موارد را به درستی تکمیل کنید','error')
            return redirect('/user/signup')
        else:
            is_username=User().query.filter_by(username=username).first()
            is_personal=User().query.filter_by(personalCode=personalCode).first()
            if is_username:
                flash('نام کاربری قبلا ثبت شده','error')
                return redirect('/user/signup')
            elif is_personal:
                flash('شماره پرسنلی در سامانه موجود است','error')
                return redirect('/user/signup')
            else:
                new_user=User(CenterName=CenterName,CenterCode=CenterCode,password=password,username=username,personal=personal,personalCode=personalCode)
                db.session.add(new_user)
                db.session.commit()
                for _type in types:
                    c_type = _type.typeOfCards
                    _property = Property(user_code=CenterCode, cardType=c_type, supply=0)
                    db.session.add(_property)
                    db.session.commit()   
                    
                nw_us = User.query.filter_by(CenterCode=CenterCode).first()
                nw_us_code = nw_us.CenterCode
                flash('لطفا فرم مرحله بعد را نیز تکمیل کنید','message')
                return redirect(url_for('firstSupply',nw_us_code=nw_us_code))
    else:
        return render_template('user/signup.html',title="ثبتنام اعضا")



@app.route('/user/firstSupply/<nw_us_code>',methods=['POST','GET'])
def firstSupply(nw_us_code):
    types = Card.query.all()

    if request.method=='POST':
        cType = request.form.getlist('cType')
        cSupply = request.form.getlist('cSupply')
        newcSupply = [n for n in cSupply if n != '']
        
        for _type in cType:
            if not is_number_string(newcSupply[cType.index(_type)]):
                flash('لطفا از مقادیر عددی استفاده کنید','error')
                return redirect('/user/firstSupply/' + nw_us_code)
            
            else:
                Checker = Property.query.filter_by(user_code=nw_us_code.CenterCode, cardType=_type).first()
                if Checker:
                    Checker.date_add = JalaliDate.today()
                    Checker.supply = newcSupply[cType.index(_type)]

        db.session.commit()
        flash('ثبت اطلاعات انجام شد، بعد از تایید مدیریت به سامانه دسترسی خواهید داشت','message')
        return redirect('/user/')
            
    else:
        return render_template('user/first-supply.html',types=types)
   
   
   
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    else:
        id = session.get('user_id')
        users = User().query.filter_by(id=id).first()
        if users:
            infos = Property.query.filter_by(user_code=users.CenterCode).all()
            return render_template('user/dashboard.html', title="میزکار کاربر", users=users, infos=infos)
        else:
            return render_template('user/empty-dashboard.html', title="میزکار کاربر")

    
    
@app.route('/user/updateSupply',methods=['POST','GET'])
def updateSupply():
    types = Card.query.all()
    if not session.get('user_id'):
        return redirect('/user/')
    
    else:
        user_id = session.get('user_id')
        users = User.query.get(user_id)
    
    if request.method == 'POST':
        cType = request.form.getlist('cType')
        cSupply = request.form.getlist('cSupply')
        newcSupply = [n for n in cSupply if n != '']

        for _type in cType:
            if not is_number_string(newcSupply[cType.index(_type)]):
                flash('لطفا از مقادیر عددی استفاده کنید', 'error')
                return redirect('/user/updateSupply')
            else:
                checker = Property.query.filter_by(user_code=users.CenterCode, cardType=_type).first()
                if checker:
                    checker.date_add = JalaliDate.today()
                    checker.supply = newcSupply[cType.index(_type)]

        db.session.commit()
        flash('موجودی شعبه بروزرسانی شد', 'message')
        return redirect('/user/dashboard')
    else:        
        return render_template('user/update-supply.html',users=users,types=types)     


@app.route('/admin/manageRequests', methods=["GET", "POST"])
def manageRequests():
    if not session.get('admin_id'):
        return redirect('/admin/')
    else:
        users = User.query.all()
        reqs = UserRequest.query.all()  
        return render_template('admin/manage-requests.html', requests=reqs,users=users)


@app.route("/display-and-generate", methods=["GET", "POST"])
def display_and_generate():
    if request.method == "POST":
        try:
            with open("user_requests.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            df = pd.DataFrame(data)
            if df.empty:
                flash("درخواستی وجود ندارد", "error")
                return redirect(url_for("display_and_generate"))

            plt.rcParams['font.family'] = 'Samim'
            plt.rcParams['font.size'] = 12
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['axes.formatter.use_locale'] = True 
            plt.rcParams['xtick.direction'] = 'in'
            plt.rcParams['ytick.direction'] = 'in'

            def generate_image():
                plt.figure(figsize=(10, 6))
                plt.axis('off')
                plt.table(cellText=df.values, colLabels=df.columns, loc='center')
                plt.savefig("static/tables/table.png", bbox_inches='tight', pad_inches=0.1)
                plt.close()

            executor.submit(generate_image).result()
        except FileNotFoundError:
            flash("فایل JSON یافت نشد.", "error")
            return redirect(url_for("display_and_generate"))
        except Exception as e:
            flash(f"خطایی در خواندن فایل JSON رخ داده است: {e}", "error")
            return redirect(url_for("display_and_generate"))
        
        flash("جدول با موفقیت نمایش داده شد و تصویر آن در فایل table.png ذخیره شد.", "success")
        return send_file("static/tables/table.png", as_attachment=True)
    else:
        return render_template("admin/display-and-generate.html")


@app.route('/user/userRequest', methods=["POST", "GET"])
def userRequest():
    if not session.get('user_id'):
        return redirect('/user/')
    
    id = session.get('user_id')
    users = User.query.get(id)
    types = Card.query.all()
    
    if request.method == 'POST':
        cType = request.form.getlist('cType')
        cSupply = request.form.getlist('cSupply')
        newcSupply = [n for n in cSupply if n != '']

        all_requests = {}
        
        for card_type, supply_quantity in zip(cType, newcSupply):
            if not is_number_string(supply_quantity):
                flash('لطفا از مقادیر عددی استفاده کنید', 'error')
                return redirect('/user/userRequest')
            else:
                new_request = {    
                    'نام شعبه': users.CenterName,   
                    'نوع کالا': card_type,
                    'تعداد': supply_quantity,
                    'تاریخ': str(JalaliDate.today())
                }
                
                if users.CenterCode in all_requests:
                    all_requests[users.CenterCode].append(new_request)  
                    all_requests[users.CenterCode] = [new_request]  

        with open('user_requests.json', 'a', encoding='utf-8') as json_file:
            json.dump(all_requests, json_file, ensure_ascii=False, indent=4)
            json_file.write('\n')

        flash('درخواست‌های شما ارسال شدند', 'success')
        return redirect('/user/dashboard')

    else:        
        return render_template('user/user-request.html', users=users, types=types)




@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user/')
    
    elif session.get('user_id'):
        id = session.get('user_id')
        
        users = User.query.get(id)
        if request.method == 'POST':
            CenterName = request.form.get('CenterName')
            CenterCode = request.form.get('CenterCode')
            personal = request.form.get('personal')
            personalCode = request.form.get('personalCode')
            username = request.form.get('username')
            password = request.form.get('password')
            if not all([CenterName, CenterCode, username, password, personal, personalCode]) or not all(is_number_string(val) for val in [CenterCode, personalCode]):
                flash('لطفا تمامی موارد را به درستی تکمیل کنید', 'error')
                return redirect('/user/update-profile')
            else:
                session['username'] = None
                users.CenterName = CenterName
                users.CenterCode = CenterCode
                users.username = username
                users.password = password
                db.session.commit()
                session['username'] = username
                flash('پروفایل بروزرسانی شد', 'message')
                return redirect('/user/update-profile')
        else:
            return render_template('user/update-profile.html', title="بروز رسانی پروفایل", user=users)


@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user/')

    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/user/')


@app.errorhandler(404)
def not_found(e):
    app.logger.error(f"Forbidden Access: {e}, --> route: {request.url}")
    return render_template("error/404.html")


@app.errorhandler(403)
def forbidden(e):
    app.logger.error(f"Forbidden Access: {e}, --> route: {request.url}")
    return render_template("error/403.html")

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server Error: {e}, --> route: {request.url}")
    return render_template("error/500.html")



if __name__=="__main__":
    app.run(debug=True)