from flask import flash, render_template, request, redirect, session, url_for, Blueprint
from persiantools.jdatetime import JalaliDate
from app.models import User, Card, Property,UserRequest
from app import db


user_blueprint = Blueprint(
    'user',
    __name__,
    template_folder='templates'
)



# Checks that the characters entered by the user are numeric characters.

def is_digit_string(s):
    for char in s:
        if not (ord('0') <= ord(char) <= ord('9')):
            return False
    return True
def is_number_string(s):
    if not isinstance(s, str):
        return False
    return is_digit_string(s)




# ---------------- Bank branches login page and check login information.------------------

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
                return redirect('/user/user-login')
            else:
                session['user_id'] = user.id
                session['username'] = user.username
                flash('ورود موفقیت آمیز بود', 'message')
                return redirect('/user/dashboard')
        else:
            flash('نام کاربری یا رمز عبور نادرست است', 'error')
            return redirect('/user/user-login')
    else:
        return render_template('user/index.html', title="ورود اعضا")




# ---------------- Bank branches signup page and check signup information.------------------

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

        if CenterName =="" or CenterCode=="" or password=="" or username=="" or personal=="" or personalCode=="" or is_number_string(CenterCode) == False:
            flash('لطفا تمامی موارد را به درستی تکمیل کنید','error')
            return redirect('/user/signup')
        elif len(password) < 6:
            flash('رمز عبور باید حداقل ۶ کاراکتر باشد', 'error')
            return redirect('/user/signup')
        else:
            is_username=User().query.filter_by(CenterCode=CenterCode).first()
            is_personal=User().query.filter_by(personalCode=personalCode).first()
            if is_username:
                flash('این کد شعبه قبلا ثبت شده است','error')
                return redirect('/user/signup')
            elif is_personal:
                flash('شماره پرسنلی در سامانه موجود است','error')
                return redirect('/user/signup')
            else:
                new_user = User(CenterName=CenterName, CenterCode=CenterCode, password=password,
                                username=username, personal=personal, personalCode=personalCode)
                db.session.add(new_user)
                db.session.commit()
                for _type in types:
                    c_type = _type.typeOfCards
                    _property = Property(user_code=CenterCode, cardType=c_type, supply=0)
                    db.session.add(_property)
                    db.session.commit()   
                    
                nw_us = User.query.filter_by(CenterCode=CenterCode).first()
                nw_us_code = nw_us.CenterCode
                flash('لطفا موجودی اولیه خود را اعلام کنید','message')
                return redirect(url_for('user.firstSupply',nw_us_code=nw_us_code))
    else:
        return render_template('user/signup.html',title="ثبتنام اعضا")




# Receive information on the number and variety of the initial inventory of the branches' goods.---

@user_blueprint.route('/firstSupply/<nw_us_code>',methods=['POST','GET'])
def firstSupply(nw_us_code):   
    types = Card.query.all()

    if request.method=='POST':
        cType = request.form.getlist('cType')
        cSupply = request.form.getlist('cSupply')
        newcSupply = [n for n in cSupply if n != '']

        if cType is None or newcSupply is None:
            flash('لطفا فرم را به درستی کامل کنید', 'error')
            return redirect('/user/firstSupply/' + nw_us_code)
        else:
            for _type in cType:
                if is_number_string(newcSupply[cType.index(_type)]) == False:
                    flash('لطفا از مقادیر عددی استفاده کنید','error')
                    return redirect('/user/firstSupply/' + nw_us_code)
                
                else:
                    Checker = Property.query.filter_by(user_code=nw_us_code, cardType=_type).first()
                    if Checker:
                        Checker.date_add = JalaliDate.today()
                        Checker.supply = int( newcSupply[cType.index(_type)])

            db.session.commit()
            flash('ثبت اطلاعات انجام شد، بعد از تایید مدیریت به سامانه دسترسی خواهید داشت','message')
            return redirect('/')
            
    else:
        return render_template('user/first-supply.html',types=types)
   
   
   

# ----------------------- User dashboard that show inventory of the branch goods.-------------------------
   
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

    
    
    
# ---------------------- Update the inventory of the branch's goods by the user.-----------------------

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

        if not cType or not newcSupply:
            flash('لطفا فرم را به درستی کامل کنید','error')
            return redirect('/user/updateSupply')
        elif len(cType) != len(newcSupply):
            flash('تعداد نوع محصول و تعداد موجودی باید یکسان باشد', 'error')
            return redirect('/user/updateSupply')
        else:
            
            for _type in cType:
                checker = Property.query.filter_by(user_code=users.CenterCode, cardType=_type).first()
                if is_number_string(newcSupply[cType.index(_type)]) == False:
                    flash('لطفا از مقادیر عددی استفاده کنید', 'error')
                    return redirect('/user/updateSupply')
                elif checker:
                    checker.date_add = JalaliDate.today()
                    checker.supply = newcSupply[cType.index(_type)]
                    users.date_added = JalaliDate.today()

            db.session.commit()
            flash('موجودی شعبه بروزرسانی شد', 'message')
            return redirect('/user/dashboard')
    else:        
        return render_template('user/update-supply.html',users=users,types=types)     




# --------------------- Request new goods by the user.-----------------------

@user_blueprint.route('/userRequest', methods=["POST", "GET"])
def userRequest():
    if not session.get('user_id'):
        return redirect('/')
    
    id = session.get('user_id')
    users = User.query.get(id)
    types = Card.query.all()
    us_req = UserRequest.query.filter_by(user_code=users.CenterCode).first()
    if us_req != None:
        dates = us_req.date_added
        status = us_req.status
    else:
        dates = "درخواستی ثبت نشده"
        status = 0
    
    if request.method == 'POST':
        cType = request.form.getlist('cType')
        cSupply = request.form.getlist('cSupply')
        newcSupply = [n for n in cSupply if n != '']

        if users.date_added == str(JalaliDate.today()):
            if not cType or not newcSupply:
                flash('لطفاً فرم را به درستی کامل کنید', 'error')
                return redirect('/user/userRequest')
            elif len(cType) != len(newcSupply):
                flash('تعداد محصول انتخابی و تعداد مقادیر ورودی باید یکسان باشد', 'error')
                return redirect('/user/updateSupply')
            
            elif us_req is None or us_req.status == 1 :
                UserRequest.query.filter_by(user_code=users.CenterCode).delete()
                for card_type, supply_quantity in zip(cType, newcSupply):
                    if is_number_string(supply_quantity) == False:
                        flash('لطفاً از مقادیر عددی استفاده کنید', 'error')
                        return redirect('/user/userRequest')
                    else:
                        new_request = UserRequest(
                            user_code=users.CenterCode,
                            card_type=card_type,
                            supply_quantity=int(supply_quantity),
                            date_added=JalaliDate.today()
                        )
                        db.session.add(new_request)

                db.session.commit()
                flash('درخواست‌ شما ارسال شد', 'message')
                return redirect('/user/dashboard')
            
            elif us_req and us_req.status == 0:
                flash('درخواست سابق شما در حال بررسی است', 'error')
                return redirect('/user/userRequest')
        else:
            flash('لطفا ابتدا موجودی خود را بروزرسانی کنید', 'error')
            return redirect('/user/dashboard')    

    else:        
        return render_template('user/user-request.html', users=users, types=types, dates=dates,status=status)





#----------------------- Show Requests to Admin ------------------------

@user_blueprint.route('/show_Requests/<user_id>', methods=["GET", "POST"])
def show_Requests(user_id):
    if not session.get('user_id'):
        return redirect('/')
    
    users = User.query.get(user_id) 
    requests = UserRequest.query.filter_by(user_code=users.CenterCode).all()     
    reqses = UserRequest.query.filter_by(user_code=users.CenterCode).first()
    dates = reqses.date_added
    status = reqses.status
    return render_template('user/user-show-requests.html', users=users,dates=dates,status=status,requests=requests)




# --------------------- Update Profile for User.-----------------------

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
            if all([CenterName, CenterCode, username, password, personal, personalCode]) is None or is_number_string(CenterCode) == False:
                flash('لطفا تمامی موارد را به درستی تکمیل کنید', 'error')
                return redirect('/user/update-profile')
            else:
                session['username'] = None
                users.CenterName = CenterName
                users.CenterCode = CenterCode
                users.personal = personal
                users.personalCode = personalCode
                users.username = username
                users.password = password
                db.session.commit()
                session['username'] = username
                flash('پروفایل بروزرسانی شد', 'message')
                return redirect('/user/update-profile')
        else:
            return render_template('user/update-profile.html', title="بروز رسانی پروفایل", users=users)



# -------- User Logout ---------

@user_blueprint.route('/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/')

    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/')

