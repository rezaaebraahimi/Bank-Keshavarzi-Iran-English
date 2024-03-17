from flask import flash, render_template, request, redirect, session, url_for, Blueprint
from persiantools.jdatetime import JalaliDate
from app.models import Admin, User, Property, Card, UserRequest, Blogpost, Receive
from app import db




admin_blueprint = Blueprint(
    'admin',
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



@admin_blueprint.route('/admin-login', methods=["POST", "GET"])
def admin_index():
    if request.method == 'POST':
        admin_user = request.form.get('admin_user')
        admin_pass = request.form.get('admin_pass')
        if not admin_user or not admin_pass:
            flash('لطفا تمامی موارد را کامل کنید', 'error')
            return redirect('/admin/admin-login')
        else:
            admin = Admin.query.filter_by(admin_user=admin_user, admin_pass=admin_pass).first()
            if admin:
                session['admin_id'] = admin.id
                session['admin_name'] = admin.admin_user
                flash('ورود موفقیت آمیز بود', 'message')
                return redirect('/admin/admin-dashboard')
            else:
                flash('نام کاربری یا رمز عبور اشتباه است', 'error')
                return redirect('/admin/admin-login')
    else:
        return render_template('admin/index.html', title="ورود مدیریت")



@admin_blueprint.route('/admin-dashboard', methods=["POST", "GET"])
def admin_dashboard():
    if not session.get('admin_id'):
        return redirect('/')
    else:
        if request.method == 'POST':
            user_code = request.form.get('usercode')
            return redirect(url_for('admin.adminGetDetails', usercode=user_code))
        else:
            users = User.query.all()
            all_pro = Property.query.all()
            if all_pro and users:
                infos = []
                for user in users:
                    c_user = user.CenterCode
                    for pro in all_pro:
                        if pro.user_code == c_user:
                             infos.append(pro)
                return render_template('admin/dashboard.html', title="میزکار مدیریت", users=users, infos=infos)
            else:
                return render_template('admin/empty-dashboard.html', title="میزکار مدیریت")



@admin_blueprint.route('/get-all-details/', methods=["POST","GET"])
def adminGetDetails():
    if not session.get('admin_id'):
        return redirect('/')
    usercode = request.args.get('usercode')
    users = User.query.filter_by(CenterCode=usercode).all()
    for user in users:
        if user.CenterCode == usercode:
            infos = Property.query.filter_by(user_code=usercode).all()
            return render_template('admin/admin-get-details.html', title="جزئیات موجودی", users=users, infos=infos)
   

    

@admin_blueprint.route('/recieve', methods=["POST","GET"])
def recieve():
    if not session.get('admin_id'):
        return redirect('/')
    
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
    
    

@admin_blueprint.route('/add-card-type', methods=["POST","GET"])
def addcardtype():
    if not session.get('admin_id'):
        return redirect('/')
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
        
        
        
@admin_blueprint.route('/remove-card-type', methods=["POST","GET"])
def removecardtype():
    if not session.get('admin_id'):
        return redirect('/')
    if request.method== "POST":
        card_type_remove = request.form.get('card_type_remove')
        if card_type_remove:
            card_to_delete  = Card.query.filter_by(typeOfCards=card_type_remove).first()
            card_delete = Receive.query.filter_by(cardType=card_type_remove).first()
            if card_delete:
                db.session.delete(card_delete)
                db.session.commit()
            db.session.delete(card_to_delete)
            db.session.commit()
            flash('کالا با موفقیت از خزانه حذف شد','message')    
            return redirect('/admin/recieve')
        else:
            flash('لطفا نام کالا را وارد کنید','error')
            return redirect('/admin/recieve')
        


@admin_blueprint.route('/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.CenterCode.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='لیست کاربران',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-user.html',title=' لیست کابران',users=users)



@admin_blueprint.route('/approve-user/<int:id>')
def approve(id):
    if not session.get('admin_id'):
        return redirect('/')
    else:
        User().query.filter_by(id=id).update(dict(status=1))
        db.session.commit()
        flash('تایید موفقیت آمیز بود','message')
        return redirect('/admin/get-all-user')



@admin_blueprint.route('/disapprove-user/<int:id>')
def disapprove(id):
    if not session.get('admin_id'):
        return redirect('/')
    else:
        User().query.filter_by(id=id).update(dict(status=0))
        db.session.commit()
        flash('کاربر مورد نظر تعلیق شد','message')
        return redirect('/admin/get-all-user')



@admin_blueprint.route('//change-admin-password', methods=["POST", "GET"])
def adminChangePassword():
    if not session.get('admin_id'):
        return redirect('/')
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



@admin_blueprint.route('/add')
def add():
    if not session.get('admin_id'):
        return redirect('/')
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('admin/add-post.html',posts=posts)



@admin_blueprint.route('/addpost', methods=['POST'])
def addpost():
    if not session.get('admin_id'):
        return redirect('/')
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



@admin_blueprint.route('/manageRequests', methods=["GET", "POST"])
def manageRequests():
    if not session.get('admin_id'):
        return redirect('/')
    
    if request.method == 'POST':
        search=request.form.get('search')
        users=UserRequest.query.filter(User.CenterCode.like('%'+search+'%')).all()
        return render_template('admin/manage-requests.html')
    else:
        users = User.query.all()
        requests = UserRequest.query.all()
        for user in users:
            for req in requests:
                if user.CenterCode == req.user_code:
                    reqUsers = User.query.filter_by(CenterCode=req.user_code).all()
                    reqses = UserRequest.query.filter_by(user_code=user.CenterCode).first()
                    dates = reqses.date_added
        return render_template('admin/manage-requests.html',reqUsers=reqUsers,dates=dates)



@admin_blueprint.route('/showRequests/<user_id>', methods=["GET", "POST"])
def showRequests(user_id):
    if not session.get('admin_id'):
        return redirect('/')
    else:
        users = User.query.get(user_id) 
        requests = UserRequest.query.filter_by(user_code=users.CenterCode).all() 
        reqses = UserRequest.query.filter_by(user_code=users.CenterCode).first() 
        dates = reqses.date_added
        return render_template('admin/show-requests.html', users=users, requests=requests,dates=dates)



    

@admin_blueprint.route('/manageUserRequests/<user_id>', methods=["GET", "POST"])
def manageUserRequests(user_id):
    if not session.get('admin_id'):
        return redirect('/')
    user = User.query.get(user_id)
    user_requests = UserRequest.query.filter_by(user_code=user.CenterCode).all()
    
    if request.method == 'POST':
        new_supply_quantity = request.form.getlist('new_supply_quantity')
        newSupplyquantity = [n for n in new_supply_quantity if n != '']
        
        for req ,sp in zip(user_requests, newSupplyquantity):
            
            req.supply_quantity = sp

        db.session.commit()

        flash('تغییرات با موفقیت ذخیره شد', 'success')
        return redirect('/admin/manageRequests')

    return render_template('admin/edit-requests.html', user_requests = user_requests)




@admin_blueprint.route('/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/')
    else:
        session['admin_id'] = None
        session['admin_name'] = None
        return redirect('/')
