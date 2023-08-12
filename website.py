from flask import Flask, render_template, redirect, request, send_file, Response, flash
from pymongo import MongoClient
import json
import io
import base64
import datetime
from datetime import datetime


# univarsal book_id
website = Flask(__name__, static_url_path='/static')

website.secret_key = 'super secret key'


# our configurable file
json_file = open('configure.json')
parameter = json.load(json_file)

# ------------Connection with mongo DB server
client = MongoClient('mongodb://localhost:27017/')
db = client['bookstore']
registration = db['registration']
student_registration = db['student_registration']
book_detail = db['book_detail']
book_visited = db['book_visited']
book_order= db['book_order']


# normal home page
@website.route('/')
def home():
    id_temp2=db.book_visited.find({ "count": { '$gte': 5 } },{"date":0,"time":0,"count":0})
    temp2=[]
    for i in id_temp2:
        data=db.book_detail.find_one({"book_id":i['book_id']})
        temp2.append(data)
    temp1= db.book_detail.find().limit(3)
    parameter['bookList'] =temp1
    parameter['bookList2']=temp2
    return render_template('home.html', parameter=parameter)


# student login
@website.route('/slogin', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        if(isLogIn()):
            return render_template('login.html', login_status='Already Logged In(s)', parameter=parameter)
        email = request.form.get('email')
        upass = request.form.get('password')
# finding the same credincial into datacase
        data = list(db.student_registration.find({"email": email}))
        if(len(data) == 0):
            return render_template('login.html', login_status='NOT REGISTERED(s)', parameter=parameter)

        # condition when user able to logged in successfully
        if(upass == data[0]['password']):
            # it means student has logged in successfuly
            parameter['isLogIn'] = 0
            data = db.student_registration.find_one({"email": email})
            parameter['student'] = data['first_name']+" "+data['last_name']
            parameter['login_detail']=data
            print(data)
            return render_template('home.html', parameter=parameter)
        # if password is wornd then redirect to the login.html
        else:
            return render_template('login.html', login_status='WRONG PASSWORD(s)', parameter=parameter)
    if(isLogIn()):
        return render_template('login.html', login_status='Already Logged In(s)', parameter=parameter)
    return render_template('login.html', login_status='', parameter=parameter)


# for admin login
@website.route('/login', methods=['GET', 'POST'])
def admin_login():
    # checks the user credintails as accordingly provide the permission
    if request.method == 'POST':
        print('hi')
        if(isLogIn()):
            return render_template('login.html', temp='admin', login_status='Already Logged In(a)', parameter=parameter)
        email = request.form.get('email')
        upass = request.form.get('password')

        # finding the same credincial into datacase
        data = list(db.registration.find({"email": email}))
        if(len(data) == 0):
            return render_template('login.html', temp='admin', login_status='NOT REGISTERED(a)', parameter=parameter)

        # condition when user able to logged in successfully
        if(upass == data[0]['password']):
            parameter['isLogIn'] = 1  # admin has logged in successfullys
            data = db.registration.find_one({"email": email})

            parameter['admin'] = data['first_name']+" "+data['last_name']
            parameter['login_detail']=data
            # return render_template('admin_dashboard.html', add_book=None, parameter=parameter)
            # return render_template('home.html',parameter=parameter)

            return render_template('admin_dashboard.html', parameter=parameter)
        # if password is wornd then redirect to the login.html
        else:
            return render_template('login.html', temp='admin', login_status='WRONG PASSWORD(a)', parameter=parameter)
    if(isLogIn()):
        return render_template('login.html', temp='admin', login_status='Already Logged In(a)', parameter=parameter)
    return render_template('login.html', temp='admin', login_status='', parameter=parameter)


# for registration
@website.route('/register', methods=['GET', 'POST'])
def student_register():
    if request.method == "POST":
        email = request.form.get('email')

        data = list(db.student_registration.find({"email": email}))
        if(len(data) != 0):
            return render_template('login.html', temp='register', login_status='Email is Already Registered!(s)', parameter=parameter)

        passw = request.form.get('password')
        re_passw = request.form.get('re_password')
        if(passw != re_passw):
            return render_template('login.html', temp='register', login_status='Password NOt Matched!(s)', parameter=parameter)
        First_name = request.form.get('first_name')
        Last_name = request.form.get('last_name')

        obj = {"email": email, "password": passw,
               "first_name": First_name, "last_name": Last_name}
        # inserting into db
        db.student_registration.insert_one(obj)
        return render_template('login.html', login_status='Registered Successfully!\nYou can Login now.(s)', parameter=parameter)

    return render_template('login.html', temp='register', parameter=parameter)

# to logout


@website.route('/logout_<who>')
def logout(who):
    if who == '1':
        print('admin log out')
        parameter['isLogIn'] = -1
        parameter['admin'] = "Admin"
        parameter['login_detail']={}
        return redirect('/login')
    elif who == '0':
        print('studern log out')
        parameter['isLogIn'] = -1
        parameter['student'] = "Student"
        parameter['login_detail']={}
        return redirect('/slogin')
    else:
        print('other log out')
        parameter['isLogIn'] = -1
        parameter['student'] = "Student"
        parameter['admin'] = "Admin"
        parameter['login_detail']={}
        return redirect('/')
# to show the dashboard


@website.route('/admin_dashboard', methods=['GET', 'POST'])
def dashboard():
    if(isLogIn()):
        parameter['bookList'] = db.book_detail.find()
        return render_template('admin_dashboard.html', add_book=None, parameter=parameter)
    return redirect('/login')


# to add the book to database
@website.route('/admin_dashboard_add_book', methods=['GET', 'POST'])
def admin_add_book():
    # id already login the no problem
    if(isLogIn()):
        if request.method == 'POST':
            data = request.form
            # first open it to reading mode
            j_file = open('configure.json', 'r')
            par = json.load(j_file)
            obj = {
                "book_id": "b_"+str(par['book_id']),
                "cover_image": base64.b64encode(io.BufferedReader(io.BytesIO(request.files['book_cover_photo'].read())).read()).decode('utf-8'),
                # "cover_image":data.get('book_cover_photo'),#it gives null value as it has accespt only text
                "book_title": data.get('book_title'),
                "book_author": data.get('book_author'),
                "book_category": data.get("book_category"),
                "book_subcategory": data.get("book_subcategory"),
                "book_content": request.files['book_content'].read(),
                "about_author": data.get("about_author"),
                "about_book": data.get('about_book'),
                "price": int(data.get('price_'))
            }
            recommedation_detail = {
                "book_id": "b_"+str(par['book_id']),
                "date": str(datetime.now()).split(" ")[0],
                "time": str(datetime.now()).split(" ")[1].split('.')[0],
                "count": 0
            }
            db.book_detail.insert_one(obj)
            db.book_visited.insert_one(recommedation_detail)
            j_file.close()
            # NOw updating the book_id
            par['book_id'] = par['book_id']+1
            j2_file = open('configure.json', 'w')
            json.dump(par, j2_file)
            j2_file.close()
            return render_template('admin_dashboard.html', add_book='add_book', status='Data added Successfully!', parameter=parameter)
        return render_template('admin_dashboard.html', add_book='add_book', parameter=parameter)
    return redirect('/login')


# Read the Book
@website.route('/read_now_<book_id>')
def read_now(book_id):
    # count when come to read
    book_visited_detail = db.book_visited.find({"book_id": book_id})
    parameter['bookList'] = db.book_detail.find({"book_id": book_id})
    if(parameter['isLogIn']!=1):
        count = book_visited_detail[0]['count']+1
        date = str(datetime.now()).split(" ")[0]
        time = str(datetime.now()).split(" ")[1].split('.')[0]
        db.book_visited.update_one({"book_id": book_id}, {
                                '$set': {"date": date, "time": time, "count": count}})
    # return render_template('read_book.html', parameter=parameter)
    return Response(parameter['bookList'][0]['book_content'], mimetype='application/pdf')

# Showing Book details
@website.route('/book_detail_<book_id>')
def book_detail(book_id):
    parameter['bookList'] = db.book_detail.find({"book_id": book_id})
    book_visited_detail = db.book_visited.find({"book_id": book_id})
    # count when come to view details
    if(parameter['isLogIn']!=1):
        count = book_visited_detail[0]['count']+1
        date = str(datetime.now()).split(" ")[0]
        time = str(datetime.now()).split(" ")[1].split('.')[0]
        # updating the counting and date
        db.book_visited.update_one({"book_id": book_id}, {
                               '$set': {"date": date, "time": time, "count": count}})
    return render_template('book_detail.html', parameter=parameter)


@website.route('/book_download_<book_id>')
def book_download(book_id):
    parameter['bookList'] = db.book_detail.find({"book_id": book_id})
    return send_file(parameter['bookList'][0]['book_content'],
                     mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f"{parameter['bookList'][0]['book_title']}.pdf",)

# function use to check whether user is already log in or not


@website.route('/book_delete_<book_id>')
def book_delete(book_id):
    print(book_id)
    db.book_detail.delete_one({"book_id": book_id})
    db.book_visited.delete_one({"book_id": book_id})
    flash('Book Deleted Successfully!')
    return redirect('/admin_dashboard')

# for seaching a book


@website.route('/search_book', methods=['GET', 'POST'])
def search_book():
    if request.method == 'POST':
        print('hello')
        category = request.form.get('book_category')
        subcategory = request.form.get('book_subcategory')
        print(category)
        print(subcategory)
        parameter['bookList'] =list(db.book_detail.find({'$and': [
            {"book_category": category},
            {"book_subcategory": subcategory}
        ]}))
        # parameter['bookList']=db.book_detail.find( { "book_category": category}  )
        return render_template('search.html', parameter=parameter)
    return render_template('search.html', parameter=parameter)


@website.route('/purchase_book_<book_id>',methods=['GET','POST'])
def purchase_book(book_id):
    if(isLogIn()):
        if(request.method=='POST'):
            b_id=book_id
            first_name=request.form.get('first_name')
            last_name=request.form.get('last_name')
            email=request.form.get('email')
            address=request.form.get('address')
            book_title=request.form.get('book_title')
            book_author=request.form.get('book_author')
            book_price=request.form.get('price')
            # img=db.book_detail.find({'book_id':book_id},{'book_id':0,'book_title':0,'book_author':0,'book_category':0,'book_subcategory':0,'book_content':0,'about_author':0,'about_book':0,"price":0})
            obj={
                "book_id":b_id,
                "first_name":first_name,
                "last_name":last_name,
                "email":email,
                "address":address,
                "book_title":book_title,
                "book_author":book_author,
                "price":book_price,
                "time":str(datetime.now()).split(" ")[1].split('.')[0],
                "date":str(datetime.now()).split(" ")[0]
            }
            db.book_order.insert_one(obj)
            return render_template('purchase_book.html',parameter=parameter,order_status="Order Placed Successfully",status=0)
        parameter['bookList']=db.book_detail.find({"book_id":book_id})
        return render_template('purchase_book.html',parameter=parameter)
    return render_template('login.html', login_status='Login to Purchase', parameter=parameter)

# for order details
@website.route('/order_detail')
def order_detail():
    if(isLogIn()):
        all_order=list(db.book_order.find({"email":parameter['login_detail']['email']}))
        print(all_order)
        if(len(all_order)==0):
            # no order places
            order_d_status="No order Placed Yet!"
            return render_template('order_detail.html',parameter=parameter,order_d_status=order_d_status,order=0)
        temp_list=[]
        for i in all_order:
            temp_list.append(db.book_detail.find_one({'book_id':i['book_id']}))
        parameter['bookList']=temp_list
        print(len(temp_list))
        return render_template('order_detail.html',parameter=parameter,order=1,all_order=all_order)
    return render_template('login.html', login_status='Login to see Order Details', parameter=parameter)


@website.route('/main_search',methods=['GET','POST'])
def main_search():
    if request.method=="POST":
        book_name=request.form.get('search_book')
        parameter['bookList']=db.book_detail.find({'book_title':book_name})
        return render_template('main_search.html',parameter=parameter,all_book=0)
    parameter['bookList']=db.book_detail.find()
    return render_template('main_search.html',parameter=parameter,all_book=1)
def isLogIn():
    # 1 is for admin
    if(parameter['isLogIn'] == 1):
        return True
    # 0 is for student
    elif(parameter['isLogIn'] == 0):
        return True
    # none is logged in
    else:
        return False


if __name__ == "__main__":
    website.run(debug=True, use_reloader=True)
