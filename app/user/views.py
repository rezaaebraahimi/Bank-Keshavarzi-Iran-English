from flask import flash, render_template, request, redirect, session, url_for, Blueprint
from persiantools.jdatetime import JalaliDate
from app.models import User, Card, Property,UserRequest
from app import db

user_blueprint = Blueprint(
    'user',
    __name__,
    template_folder='templates'
)


def is_digit_string(s):
    for char in s:
        if not (ord('0') <= ord(char) <= ord('9')):
            return False
    return True

def is_number_string(s):
    if not isinstance(s, str):
        return False
    return is_digit_string(s)


@user_blueprint.route('/user-login', methods=["POST", "GET"])
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
                return redirect('/user-login')
            else:
                session['user_id'] = user.id
                session['username'] = user.username
                flash('ورود موفقیت آمیز بود', 'message')
                return redirect('/user/dashboard')
        else:
            flash('نام کاربری یا رمز عبور نادرست است', 'error')
            return redirect('/user-login')
    else:
        return render_template('user/index.html', title="ورود اعضا")



@user_blueprint.route('/signup',methods=['POST','GET'])
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
                return redirect(url_for('user.firstSupply',nw_us_code=nw_us_code))
    else:
        return render_template('user/signup.html',title="ثبتنام اعضا")



@user_blueprint.route('/firstSupply/<nw_us_code>',methods=['POST','GET'])
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
                Checker = Property.query.filter_by(user_code=nw_us_code, cardType=_type).first()
                if Checker:
                    Checker.date_add = JalaliDate.today()
                    Checker.supply = newcSupply[cType.index(_type)]

        db.session.commit()
        flash('ثبت اطلاعات انجام شد، بعد از تایید مدیریت به سامانه دسترسی خواهید داشت','message')
        return redirect('/')
            
    else:
        return render_template('user/first-supply.html',types=types)
   
   
   
@user_blueprint.route('/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/')
    else:
        id = session.get('user_id')
        users = User().query.filter_by(id=id).first()
        if users:
            infos = Property.query.filter_by(user_code=users.CenterCode).all()
            return render_template('user/dashboard.html', title="میزکار کاربر", users=users, infos=infos)
        else:
            return render_template('user/empty-dashboard.html', title="میزکار کاربر")

    
    
@user_blueprint.route('/updateSupply',methods=['POST','GET'])
def updateSupply():
    types = Card.query.all()
    if not session.get('user_id'):
        return redirect('/')
    
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




@user_blueprint.route('/userRequest', methods=["POST", "GET"])
def userRequest():
    if not session.get('user_id'):
        return redirect('/')
    
    id = session.get('user_id')
    users = User.query.get(id)
    types = Card.query.all()
    
    if request.method == 'POST':
        cType = request.form.getlist('cType')
        cSupply = request.form.getlist('cSupply')
        newcSupply = [n for n in cSupply if n != '']
        checker = UserRequest.query.filter_by(user_code= users.CenterCode).first()
        for card_type, supply_quantity in zip(cType, newcSupply):
            if not is_number_string(supply_quantity):
                flash('لطفا از مقادیر عددی استفاده کنید', 'error')
                return redirect('/user/userRequest')
            elif users.CenterCode == checker:
                db.session.delete(checker)
                new_request = UserRequest(
                    user_code=users.CenterCode,
                    card_type=card_type,
                    supply_quantity=int(supply_quantity),
                    date_added=JalaliDate.today(),
                    status='Pending'
                )
                db.session.add(new_request)
            else:
                new_request = UserRequest(
                    user_code=users.CenterCode,
                    card_type=card_type,
                    supply_quantity=int(supply_quantity),
                    date_added=JalaliDate.today(),
                    status='Pending'
                )
                db.session.add(new_request)

        db.session.commit()

        flash('درخواست‌های شما ارسال شدند', 'success')
        return redirect('/user/dashboard')

    else:        
        return render_template('user/user-request.html', users=users, types=types)


@user_blueprint.route('/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/')
    
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


@user_blueprint.route('/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/')

    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/')

