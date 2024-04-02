from flask import flash, render_template, request, redirect, session, url_for, Blueprint
from persiantools.jdatetime import JalaliDate
from app.models import Admin, User, Property, Card, UserRequest, Blogpost, Receive
from app import db


admin_blueprint = Blueprint(
    'admin',
    __name__,
    template_folder='templates'
)

# Checks that the characters entered by the admin are numeric characters.
def is_digit_string(s):
    for char in s:
        if not (ord('0') <= ord(char) <= ord('9')):
            return False
    return True
def is_number_string(s):
    if not isinstance(s, str):
        return False
    return is_digit_string(s)


# ---------------- Central Bank (Admin) login page and check login information.------------------

@admin_blueprint.route('/admin-login', methods=["POST", "GET"])
def admin_index():
    if request.method == 'POST':
        admin_user = request.form.get('admin_user')
        admin_pass = request.form.get('admin_pass')
        if not admin_user or not admin_pass:
            flash('Please complete the form correctly', 'error')
            return redirect('/admin/admin-login')
        else:
            admin = Admin.query.filter_by(admin_user=admin_user, admin_pass=admin_pass).first()
            if admin:
                session['admin_id'] = admin.id
                session['admin_name'] = admin.admin_user
                flash('Welcome to Digital banking consumer products system', 'message')
                return redirect('/admin/admin-dashboard')
            else:
                flash('The username or password is incorrect', 'error')
                return redirect('/admin/admin-login')
    else:
        return render_template('admin/index.html', title="Central Branch Login")


# ----------------------- Admin dashboard that show inventory of the bank branches' products.-------------------------

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
                return render_template('admin/dashboard.html', title="Dashboard", users=users, infos=infos)
            else:
                return render_template('admin/empty-dashboard.html', title="Dashboard")


# -------------------------- Admin get details of bank branches' product.--------------------------

@admin_blueprint.route('/get-all-details/', methods=["POST","GET"])
def adminGetDetails():
    if not session.get('admin_id'):
        return redirect('/')
    usercode = request.args.get('usercode')
    users = User.query.filter_by(CenterCode=usercode).all()
    for user in users:
        if user.CenterCode == usercode:
            infos = Property.query.filter_by(user_code=usercode).all()
            return render_template('admin/admin-get-details.html', title="Inventory Details", users=users, infos=infos)
   

#------------------------ Admin send to user without user request--------------------------
   
@admin_blueprint.route('/add_CardToUser', methods=["POST","GET"])
def add_CardToUser():
    if not session.get('admin_id'):
        return redirect('/')
    
    users = User.query.all()
    types = Card.query.all()
    
    if request.method == 'POST':
        CenterCode = request.form.get('CenterCode')
        cSupply = request.form.getlist('cSupply')
        typeOfCards = request.form.getlist('cType')
        sendToUser = [n for n in cSupply if n != '']

        if CenterCode is None or sendToUser ==[] or typeOfCards ==[]:
            flash('Please complete the form correctly', 'error')
            return redirect('/admin/add_CardToUser')
        
        elif len(typeOfCards) != len(sendToUser):
            flash("The number of selected products and the number of input values must be the same", 'error')
            return redirect('/admin/add_CardToUser')
        
        else:
            for _type in typeOfCards:
                adminChecker = Receive.query.filter_by(cardType=_type).first()
                Checker = Property.query.filter_by(user_code=CenterCode,cardType=_type).first()
                if is_number_string(sendToUser[typeOfCards.index(_type)]) == False:
                    flash('Please use numeric values', 'error')
                    return redirect('/admin/add_CardToUser')
                elif adminChecker is None or adminChecker.admin_supply < int( sendToUser[typeOfCards.index(_type)]):
                    flash('The amount entered is not available in the treasury', 'error')
                    return redirect('/admin/add_CardToUser')
                elif Checker:
                    adminChecker.admin_supply -= int( sendToUser[typeOfCards.index(_type)])
                    Checker.supply += int(sendToUser[typeOfCards.index(_type)])
                    Checker.date_add = JalaliDate.today()
                    User.query.filter_by(CenterCode=CenterCode).update({'date_added': JalaliDate.today()})
                else:
                    adminChecker.admin_supply -= int(sendToUser[typeOfCards.index(_type)])
                    User.query.filter_by(CenterCode=CenterCode).update({'date_added': JalaliDate.today()})
                    _property = Property(user_code=CenterCode, cardType=_type, supply=int(sendToUser[typeOfCards.index(_type)]), date_add=JalaliDate.today())
                    db.session.add(_property)
            
            db.session.commit()
            flash('Products Allocated Successfully!', 'message')
            return redirect('/admin/add_CardToUser')
    else:
        return render_template('admin/add-card-to-user.html', title='Distribution of Products',users=users,types=types)
   
 
#------------------- Add products to admin recieves ------------------

@admin_blueprint.route('/recieve', methods=["POST","GET"])
def recieve():
    if not session.get('admin_id'):
        return redirect('/')
    
    types = Card.query.all()
    _recieve = Receive.query.all()  
    if request.method == 'POST':
        adminRecieve = request.form.get('adminRecieve')
        typeOfCards = request.form.get('typeOfCards')
        
        if not adminRecieve or not typeOfCards or  is_number_string(adminRecieve) == False:
            flash('Please complete the form correctly', 'error')
            return redirect('/admin/recieve') 
        
        adminRecieve = int(adminRecieve)
        Checker = Receive.query.filter_by(cardType=typeOfCards).first()
        
        if Checker:
            sum = Checker.admin_supply + adminRecieve
            Checker.admin_supply = sum
            Checker.recieve_date = JalaliDate.today()
            db.session.commit()
            flash('Received by Treasury', 'message')
        else:
            new_recieve = Receive(admin_supply=adminRecieve, recieve_date=JalaliDate.today(), cardType=typeOfCards)
            db.session.add(new_recieve)
            db.session.commit()
            flash('Received by Treasury', 'message')
        
        return redirect('/admin/recieve') 
    else:
        return render_template('admin/recieve.html', title='Treasury',_recieve=_recieve,types=types)
   
      
#------------------------ Define a new type of products ----------------------

@admin_blueprint.route('/add-card-type', methods=["POST","GET"])
def addcardtype():
    if not session.get('admin_id'):
        return redirect('/')
    if request.method== "POST":
        card_type = request.form.get('card_type')
        if len(card_type) > 45:
            flash('The product name can contain a maximum of 45 characters.','error')
            return redirect('/admin/recieve')
        if card_type:
            new_card = Card(typeOfCards=card_type)
            db.session.add(new_card)
            db.session.commit()
            flash('The new product type has been successfully defined in the Treasury','message')    
            return redirect('/admin/recieve')
        else:
            flash('Please enter the product name','error')
            return redirect('/admin/recieve')
        
       
#------------------ remove a Type of products from database ----------------------- 
        
@admin_blueprint.route('/remove-card-type', methods=["POST","GET"])
def removecardtype():
    if not session.get('admin_id'):
        return redirect('/')
    
    if request.method== "POST":
        card_type_remove = request.form.get('card_type_remove')
        if card_type_remove:
            card_to_delete  = Card.query.filter_by(typeOfCards=card_type_remove).first()
            card_delete = Receive.query.filter_by(cardType=card_type_remove).first()
            property_delete = Property.query.filter_by(cardType=card_type_remove).all()
            if card_delete:
                db.session.delete(card_delete)
                db.session.commit()
            if property_delete:
                for pro in property_delete:
                    db.session.delete(pro)
                db.session.commit()
            db.session.delete(card_to_delete)
            db.session.commit()
            flash('The product was successfully removed from the vault','message')    
            return redirect('/admin/recieve')
        else:
            flash('Please enter the product name','error')
            return redirect('/admin/recieve')
        

#--------------------- show List of users to admin------------------------

@admin_blueprint.route('/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.CenterCode.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='List of Branchs',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-user.html',title='List of Branchs',users=users)


#--------------------- approve user ------------------------

@admin_blueprint.route('/approve-user/<int:id>')
def approve(id):
    if not session.get('admin_id'):
        return redirect('/')
    else:
        User().query.filter_by(id=id).update(dict(status=1))
        db.session.commit()
        flash('Verification was successful','message')
        return redirect('/admin/get-all-user')


#-------------------- disapprove user -------------------------

@admin_blueprint.route('/disapprove-user/<int:id>')
def disapprove(id):
    if not session.get('admin_id'):
        return redirect('/')
    else:
        User().query.filter_by(id=id).update(dict(status=0))
        db.session.commit()
        flash('The target user has been suspended','message')
        return redirect('/admin/get-all-user')


#------------------------ admin change password ---------------------------

@admin_blueprint.route('/change-admin-password', methods=["POST", "GET"])
def adminChangePassword():
    if not session.get('admin_id'):
        return redirect('/')
    admin = Admin.query.get(session['admin_id'])
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_password != admin.admin_pass:
            flash('The current password is incorrect', 'error')
            return redirect('/admin/change-admin-password')

        elif new_password != confirm_password:
            flash('The new password does not match the duplicate', 'error')
            return redirect('/admin/change-admin-password')
        else:
            admin.admin_pass = new_password
            db.session.commit()
            flash('Password changed successfully', 'message')
            return redirect('/admin/admin-dashboard')
    else:
        return render_template('admin/admin-change-password.html',title='تغییر رمز عبور مدیریت', admin=admin)


#----------------- new blog post page and list of posts-----------

@admin_blueprint.route('/add')
def add():
    if not session.get('admin_id'):
        return redirect('/')
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('admin/add-post.html',posts=posts)

#----------------- add new blog post (just admin can do it)--------------

@admin_blueprint.route('/addpost', methods=['POST'])
def addpost():
    if not session.get('admin_id'):
        return redirect('/')
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']
    
    if len(title) > 45 or len(subtitle) > 45 or len(author) > 45:
        flash('Titles can be a maximum of 45 characters.','error')
        return redirect('/admin/add')
    
    if title and subtitle and author and content:
        post = Blogpost(title=title, subtitle=subtitle, author=author, content=content, date_posted=JalaliDate.today())
        db.session.add(post)
        db.session.commit()
        return redirect('/admin/add')
    else:
        flash('Please complete the form correctly', 'error')
        return redirect('/admin/add')


#-------------------Show user requests to admin ---------------

@admin_blueprint.route('/manageRequests', methods=["GET", "POST"])
def manageRequests():
    if not session.get('admin_id'):
        return redirect('/')

    users = User.query.all()
    requests = UserRequest.query.all()
    if requests != []:
        for user in users:
            for req in requests:     
                reqUsers = User.query.filter_by(CenterCode=req.user_code).all()
                reqses = UserRequest.query.filter_by(user_code=user.CenterCode).first()
                dates = reqses.date_added
                status = reqses.status
                return render_template('admin/manage-requests.html',reqUsers=reqUsers,dates=dates,status=status)
    else:
        return render_template('admin/empty-manage-requests.html')
    
    
    
#----------- Show specific user request details to admin and ready for print ----------------
    
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


#--------------------- Admin can edit user requests details --------------------

@admin_blueprint.route('/editUserRequests/<user_id>', methods=["GET", "POST"])
def editUserRequests(user_id):
    if not session.get('admin_id'):
        return redirect('/')
    
    user = User.query.get(user_id)
    user_requests = UserRequest.query.filter_by(user_code=user.CenterCode).all()
    
    if request.method == 'POST':
        new_supply_quantity = request.form.getlist('new_supply_quantity')
        newSupplyquantity = [n for n in new_supply_quantity if n != '']
        
        for req ,sp in zip(user_requests, newSupplyquantity):
            if is_number_string(sp) == False:
                flash('Please use numeric values','error')
                return redirect('/admin/editUserRequests/' + str(user_id))
            else:
                req.supply_quantity = sp

        db.session.commit()

        flash('Changes saved successfully', 'message')
        return redirect('/admin/manageRequests')

    return render_template('admin/edit-requests.html', user_requests = user_requests)


#------------- admin can remove user request --------------

@admin_blueprint.route('/removeUserRequests/<user_id>', methods=["GET", "POST"])
def removeUserRequests(user_id):
    if not session.get('admin_id'):
        return redirect('/')
    user = User.query.get(user_id)
    
    UserRequest.query.filter_by(user_code=user.CenterCode).delete()
    db.session.commit()
    
    flash('The request was rejected and deleted', 'message')
    return redirect('/admin/manageRequests')


#----------------Admin give products to User after user send request --------------

@admin_blueprint.route('/addCardToUser/<user_id>', methods=["POST", "GET"])
def addCardToUser(user_id):
    if not session.get('admin_id'):
        return redirect('/')

    user = User.query.get(user_id)
    user_requests = UserRequest.query.filter_by(user_code=user.CenterCode).all()

    for req in user_requests:
        
        typeOfCards = req.card_type
        sendToUser = int(req.supply_quantity)
        
        adminChecker = Receive.query.filter_by(cardType=typeOfCards).first()
        
        if not adminChecker:
            flash("The amount of the requested product is not specified in the treasury list",'error')
            return redirect('/admin/manageRequests')
        elif adminChecker.admin_supply < sendToUser:
            flash('Requested amounts are not available in the treasury', 'error')
            return redirect('/admin/manageRequests')
        
        property_record = Property.query.filter_by(user_code=user.CenterCode, cardType=typeOfCards).first()
        
        if property_record:
            adminChecker.admin_supply -= sendToUser
            property_record.supply += sendToUser
            property_record.date_add = JalaliDate.today()
            user.date_added = JalaliDate.today()
            UserRequest.query.filter_by(user_code=user.CenterCode,card_type=typeOfCards).update(dict(status=1))

        else:
            property_record = Property(user_code=user.CenterCode, cardType=typeOfCards, supply=sendToUser, date_add=JalaliDate.today())
            user.date_added = JalaliDate.today()
            UserRequest.query.filter_by(user_code=user.CenterCode,card_type=typeOfCards).update(dict(status=1))
            db.session.add(property_record)

    db.session.commit()
    flash('Products Allocated Successfully!', 'message')
    return redirect('/admin/manageRequests')


#------ Admin logout --------

@admin_blueprint.route('/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/')
    else:
        session['admin_id'] = None
        session['admin_name'] = None
        return redirect('/')

