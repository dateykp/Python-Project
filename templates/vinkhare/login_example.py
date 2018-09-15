from flask import Flask, render_template, request, session , url_for , redirect,json
from flask_pymongo import PyMongo
from random import randint
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import datetime


app = Flask(__name__)

app.config.update(
    DEBUG = True
)


app.config['MONGO_DBNAME'] = 'login_test'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "/%s" % (self.uid)
    
    def __eq__(self, other):
            '''
            Checks the equality of two `UserMixin` objects using `get_id`.
            '''
            if isinstance(other, UserMixin):
                return self.get_id() == other.get_id()
            return NotImplemented

mongo = PyMongo(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route('/home')
def home():
    session.clear()
    return render_template('index.html')

@app.route('/ostatus')
@login_required
def ostatus():
    return render_template('OrderStatus.html')
    
@app.route('/')
def index():
        return render_template('index.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/create')
@login_required
def create():
    return render_template('B_Success.html')

@app.route('/createproduct')
@login_required
def createproduct():
    return render_template('Add_Product.html')

@app.route('/addproduct', methods=['POST'])
def addproduct():
    if request.method == 'POST':
        supplier = mongo.db.supplier
        user=session['username']
        productname = request.form['productname'] 
        pname = productname+'_'+str(randint(10000,99999))
        Producttype = request.form['Producttype']  
        description=request.form['description']
        price_per_qty=request.form['price']
        quantity=request.form['quantity']
        delivery_day=request.form['delivery']
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        supplier.insert({'_id':pname,'product_id':pname,'product_name' : productname , 'username' : user,'Product_type' : Producttype,'product_description' : description,'price_per_qty' : price_per_qty,'product_quantity': quantity,'delivery_day': delivery_day, 'no_orders': delivery_day,'product_create_dt': pcreate_dt})
        params=['PRODUCT_ID',pname]
        return render_template('S_Success.html',params=params)
    
@app.route('/showallproducts',methods=['POST','GET'])
@login_required
def showallproducts():
    return render_template('showallproducts.html')

@app.route('/showproducts',methods=['POST','GET'])
@login_required
def showproducts():

     product_snapshot = mongo.db.supplier
     product_snapshot = product_snapshot.find()
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     productSnapShot=[]
     for productStatus in product_snapshot:
        oSnapshot={
                'product_id': productStatus['product_id'],
                'product_name': productStatus['product_name'],
                'product_description': productStatus['product_description'],
                'price_per_qty' : productStatus['price_per_qty'],
				'product_quantity' : productStatus['product_quantity'],
				'delivery_day' : productStatus['delivery_day']
                }
        productSnapShot.append(oSnapshot)

     return json.dumps(productSnapShot)



@app.route('/bhome')
@login_required
def bhome():
    return render_template('B_Dashboard.html')

@app.route('/shome')
@login_required
def shome():
    return render_template('S_Dashboard.html')

@app.route('/sjob')
@login_required
def sjob():
    return render_template('Search_job.html')


    

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    uname=request.form['username']
    login_user1 = users.find_one({'username' : request.form['username']})
    error = None
    if login_user:
        if request.form['pass'] == login_user1['password']:
            session['username'] = request.form['username']
            id = uname.split('user')[-5:]
            user = User(id)
            login_user(user)
            if login_user1['partner'] == 'B':
                    return render_template('B_Dashboard.html')
            else:
                    return render_template('S_Dashboard.html')
    else:
        error = 'Invalid username or password'
    return render_template('index.html',error=error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['name']})
        error = None
        if existing_user is None:
            name = request.form['name'] 
            partner = request.form['partner']
            uname = name + str(randint(10000,99999))
            if partner == 'B':
                uname = 'B_'+uname
            else:
                uname='S_'+uname
                
            location=request.form['location']
            district=request.form['district']
            pincode=request.form['pincode']
            hashpass=request.form['pincode']
            users.insert({'name' : name, 'username' : uname,'password' : hashpass,'partner' : partner,'location' : location,'district': district,'pincode': pincode})
            params=[uname,hashpass]
            return render_template('Register_Sucess.html',params=params)
        else:
            error = 'User Already Exsist !!!'
    
    return render_template('register.html',error=error)

#This Method is responsible for inserting Jobs into DB
@app.route('/createJob',methods=['POST','GET'])
@login_required
def createJob():
    if request.method == 'POST':
        create_job = mongo.db.create_job
        existing_job = create_job.find_one({'job_name' : request.form['jobName']})
        
        if existing_job is None:
            jobName = request.form['jobName'] 
            jobType = request.form['jobType']
            drawingNo=request.form['drawingNo']
            parts=request.form['parts']
            notes=request.form['notes']
            plannedQty=request.form['plannedQty']
            noDaysPerWeek=request.form['noDaysPerWeek']
            delDestination=request.form['delDestination']
            username=session['username']
            create_job.insert({'job_name' : jobName, 'job_type' : jobType,'drawing_no' : drawingNo,'parts' : parts,'notes' : notes,
                               'planned_qty': plannedQty,'no_days_per_week': noDaysPerWeek,'del_destination' : delDestination,'username' : username})
            params=[jobName,jobType]
            return render_template('createJobSuccess.html',params=params)
    
    return render_template('createJob.html')

#This Method is responsible for inserting Suppliers Capacity into DB
@app.route('/supplierCapacity',methods=['POST','GET'])
@login_required
def supplierCapacity():
    if request.method == 'POST':
        supplier_capacity = mongo.db.supplier_capacity
        existing_capacity = supplier_capacity.find_one({'s_name' : request.form['sName']})
        
        if existing_capacity is None:
            sName = request.form['sName'] 
            eqpMachineName = request.form['eqpMachineName']
            eqpSpec=request.form['eqpSpec']
            eqpWorkingPerDay=request.form['eqpWorkingPerDay']
            noOfWorkingDaysPerWeek=request.form['noOfWorkingDaysPerWeek']
            username=session['username']
            supplier_capacity.insert({'s_name' : sName, 'eqp_machine_name' : eqpMachineName,'eqp_spec' : eqpSpec,'eqpWorkingPerDay' : eqpWorkingPerDay,'eqp_working_per_day' : noOfWorkingDaysPerWeek,'username' : username})
            params=[sName,eqpMachineName]
            return render_template('supplierCapacitySuccess.html',params=params)
    
    return render_template('supplierCapacity.html')
@app.route('/orderList',methods=['POST','GET'])
@login_required
def orderList():
    
    return render_template('OrderList.html')
    #return order_status_snapshot
@app.route('/orderList1',methods=['POST','GET'])
@login_required
def orderList1():

     order_status_snapshot = mongo.db.order_status_snapshot
     order_status_snapshot=order_status_snapshot.find()
    #return render_template('OrderList.html',orderStatusSnapShot=order_status_snapshot)
     orderStatusSnapShot=[]
     for orderStatus in order_status_snapshot:
        oSnapshot={
                'order_id': orderStatus['order_id'],
                'supplier_name': orderStatus['supplier_name'],
                'planed_actual': orderStatus['planed_actual'],
                'ordered' : orderStatus['ordered']
                }
        orderStatusSnapShot.append(oSnapshot)

     return json.dumps(orderStatusSnapShot)
@app.route('/placeOrder',methods=['POST','GET'])
@login_required
def placeOrder():
    if request.method == 'POST':
        order_status_snapshot = mongo.db.order_status_snapshot
        #order_status_snapshot = mongo.db.order_status_snapshot
        recievedData = request.json['info']
        print(recievedData)
       
        result = order_status_snapshot.update_one({'order_id' : recievedData['order_id'] },{"$set" : {'supplier_name' : 'qwewwqq'}})
       # abc.supplier_name=recievedData['supplier_name'];
       # print(abc.supplier_name)
        print(result)
        return redirect(url_for('orderList'))

    

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5002)