from flask import Flask, render_template, request, session , url_for , redirect,json,send_from_directory
from flask_pymongo import PyMongo,pymongo
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import pandas as pd
from datetime import datetime



app = Flask(__name__)

app.config.update(
    DEBUG = True
)


app.config['MONGO_DBNAME'] = 'BM'
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
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/create')
@login_required
def create():
    return render_template('B_Success.html')

@app.route('/showDetails/<case_num>' , methods=['GET'])
@login_required
def showDetails(case_num):
   
     return render_template('showDetails.html',case_num=case_num)

@app.route('/showBM' , methods=['GET'])
@login_required
def showBM():
    return render_template('showBM.html')

@app.route('/showBMData', methods=['POST'])
def showBMmaster():
     BM_MASTER = mongo.db.BM_MASTER
     user=session['username']
     print(user)
     bmMaster = BM_MASTER.find({'ASSIGNEE' : user})
     bmArray=[]
     for tempBM in bmMaster:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])
        oBM={
                    'EDG_NUM': tempBM['EDG_NUM'],
                    'PRDS4_CASE_NUM': tempBM['PRDS4_CASE_NUM'],
                    'DEV_4_CASE_NUMBER': tempBM['DEV_4_CASE_NUMBER'],
                    'TYPE_OF_ASSISTANCE_CD' : tempBM['TYPE_OF_ASSISTANCE_CD'],
                    'AGXX02_LAST_ONLINE_AUTH_DATE' :tempBM['AGXX02_LAST_ONLINE_AUTH_DATE'],
                    'GROUPLEVELREASONS' : tempBM['GROUPLEVELREASONS'],
                    'PERSONLEVELREASONS' :  tempBM['PERSONLEVELREASONS'],
                    'RTC_ID' :  tempBM['RTC_ID'],
                    'ASSIGNEE': tempBM['ASSIGNEE'],
                    'ASSIGNED_DATE' :  tempBM['ASSIGNED_DATE'],
                    'DUPLICATE_ISSUE' :  tempBM['DUPLICATE_ISSUE'],
                    'ANALYSIS_COMPLETED' :  tempBM['ANALYSIS_COMPLETED'],
                    'STATUS' :  tempBM['STATUS'],
                    'FIXED' :  tempBM['FIXED'],
                    'DEVELOPERS_COMMENT' :  tempBM['DEVELOPERS_COMMENT'],
                    'LEADS_COMMENTS' :  tempBM['LEADS_COMMENTS']
            }
        bmArray.append(oBM)

     return json.dumps(bmArray)
    
    


@app.route('/showOneCase', methods=['POST'])
def showOneCase():
     BM_MASTER = mongo.db.BM_MASTER
     _id=request.json['_id']
     BM_MASTER = BM_MASTER.find({'_id':_id})
     print(BM_MASTER)
     bmSnapshot=[]
     for tempBM in BM_MASTER:
        oBM={
                    '_id' : tempBM['_id'],
                    'EDG_NUM': tempBM['EDG_NUM'],
                    'PRDS4_CASE_NUM': tempBM['PRDS4_CASE_NUM'],
                    'DEV_4_CASE_NUMBER': tempBM['DEV_4_CASE_NUMBER'],
                    'TYPE_OF_ASSISTANCE_CD' : tempBM['TYPE_OF_ASSISTANCE_CD'],
                    'AGXX02_LAST_ONLINE_AUTH_DATE' :tempBM['AGXX02_LAST_ONLINE_AUTH_DATE'],
                    'GROUPLEVELREASONS' : tempBM['GROUPLEVELREASONS'],
                    'PERSONLEVELREASONS' :  tempBM['PERSONLEVELREASONS'],
                    'RTC_ID' :  tempBM['RTC_ID'],
                    'ASSIGNEE': tempBM['ASSIGNEE'],
                    'ASSIGNED_DATE' :  tempBM['ASSIGNED_DATE'],
                    'DUPLICATE_ISSUE' :  tempBM['DUPLICATE_ISSUE'],
                    'ANALYSIS_COMPLETED' :  tempBM['ANALYSIS_COMPLETED'],
                    'STATUS' :  tempBM['STATUS'],
                    'DEVELOPERS_COMMENT' :  tempBM['DEVELOPERS_COMMENT'],
                    'LEADS_COMMENTS' :  tempBM['LEADS_COMMENTS']
            }
        #bmSnapshot.append(oBM)
        return json.dumps(oBM)
              
@app.route('/updateProduct',methods=['POST'])
def updateProduct():
    if request.method == 'POST':
        supplier = mongo.db.supplier
        user=session['username']
        productinfo=request.json['info']
        pname = productinfo['product_name'] 
        product_id=productinfo['product_id']
        price_per_qty=productinfo['price_per_qty']
        quantity=productinfo['product_quantity']
        delivery_day=productinfo['delivery_day']
        now = datetime.datetime.now()
        pcreate_dt= now.strftime("%Y-%m-%d %H:%M")
        pname=product_id+user
        result=supplier.update_one({'_id':pname},{'$set':{'price_per_qty' : price_per_qty,'product_quantity': quantity,'delivery_day': delivery_day,'product_create_dt': pcreate_dt}})
        return redirect(url_for('showallproducts'))

 


@app.route('/ahome')
def ahome():
    return render_template('A_Dashboard.html')


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
    login_user1 = users.find_one({'email': request.form['username']})
    if request.form['username'] == 'ADMIN@deloitte.com' or  request.form['username'] == 'admin@deloitte.com':
         session['username'] = request.form['username']
         session['name']=login_user1['name']
         user = User(id)
         login_user(user)
         return render_template('showBMDataForLeads.html')
    error = None
    if login_user1:
        if request.form['pass'] == login_user1['password']:
            session['username'] = request.form['username']
            session['name']=login_user1['name']
            user = User(id)
            login_user(user)
            return render_template('showBM.html')
    else:
        error = 'Invalid username or password'
        return render_template('index.html', error=error)
              
              
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        users = mongo.db.users
        f = request.files['file']
        data_xls = pd.read_excel(f,parse_dates=True, index_col='Assigned Date')
        user_data_json_array=data_xls.to_json(orient='records')
        parsed = json.loads(user_data_json_array)
        for item in parsed:
            existing_user = users.find_one({'name' : item['name']})
            if existing_user is None:
                users.insert(item)
                print('Inserted : '+ str(item))
            else:
                print('User Already Exsist !!!' + str(item))
        return render_template('excel_upload.html')
    return render_template('excel_upload.html')

@app.route("/aupload", methods=['GET', 'POST'])
def aupload():
    if request.method == 'POST':
        BM_MASTER = mongo.db.BM_MASTER
        f = request.files['file']
        data_xls = pd.read_excel(f,parse_dates=True)
        print(data_xls)
      #  user_data_json_array=data_xls.to_json(orient='records')
       # parsed = json.loads(user_data_json_array)
        updated_rows=0
        inserted_rows=0
        for index, item in data_xls.iterrows():
            print(item)
            if pd.isnull(item['PRDS4_CASE_NUM'])==False:
                    if item['PRDS4_CASE_NUM'] is not None:
                          if item['SR_NUM'] is not None:
                              SR_NUM = str(int(item['SR_NUM']))
                          else:
                              SR_NUM = str(item['SR_NUM'])
                          
                          if item['EDG_NUM'] is not None:
                              if pd.isnull(item['EDG_NUM']):
                                  EDG_NUM=''
                              else:
                                  EDG_NUM = str(int(item['EDG_NUM'])) 
                          else:
                              EDG_NUM = str(int(item['EDG_NUM'])) 
                          if pd.isnull(item['PRDS4_CASE_NUM']):
                              PRDS4_CASE_NUM = ''
                          else:
                              PRDS4_CASE_NUM = str(int(item['PRDS4_CASE_NUM']))
                          if item['DEV_4_CASE_NUMBER'] is not None:
                              if pd.isnull(item['DEV_4_CASE_NUMBER']):
                                  DEV_4_CASE_NUMBER = ''
                              else:
                                  DEV_4_CASE_NUMBER = str(int(item['DEV_4_CASE_NUMBER']))
                          else:
                              DEV_4_CASE_NUMBER = ''
                          if pd.isnull(item['TYPE_OF_ASSISTANCE_CD']):
                                  TYPE_OF_ASSISTANCE_CD = ''
                          else:
                                  TYPE_OF_ASSISTANCE_CD = str(item['TYPE_OF_ASSISTANCE_CD'])
                          if pd.isnull(item['AGXX02_LAST_ONLINE_AUTH_DATE']):
                                  AGXX02_LAST_ONLINE_AUTH_DATE = ''
                          else:
                                  AGXX02_LAST_ONLINE_AUTH_DATE = str(item['AGXX02_LAST_ONLINE_AUTH_DATE'])
                          if pd.isnull(item['GROUPLEVELREASONS']):
                                  GROUPLEVELREASONS = ''
                          else:
                                  GROUPLEVELREASONS= str(item['GROUPLEVELREASONS'])
                         
                          if pd.isnull(item['PERSONLEVELREASONS']):
                                  PERSONLEVELREASONS = ''
                          else:
                                  PERSONLEVELREASONS= str(item['PERSONLEVELREASONS']) 
                          if pd.isnull(item['RTCID']):
                                  RTC_ID = ''
                          else:
                                   RTC_ID= str(item['RTCID'])
                          if pd.isnull(item['Assignee']):
                                  ASSIGNEE = ''
                          else:
                                   ASSIGNEE= item['Assignee']
                          
                          
                          if pd.isnull(item['Assigned Date'])== False:
                              print(item['Assigned Date'])
                              #ASSIGNED_DATE = item['Assigned Date']
                              if item['Assigned Date'] is not pd.NaT:
                                  ASSIGNED_DATE=pd.to_datetime(item['Assigned Date']).date().isoformat()                         
                          else:
                              ASSIGNED_DATE = ''
                          if pd.isnull(item['Analysis Completed(Y/N)']):
                                  ANALYSIS_COMPLETED = ''
                          else:
                                   ANALYSIS_COMPLETED= str(item['Analysis Completed(Y/N)'])
                          if pd.isnull(item['Duplicate/Similar Issue? If Yes Update row number']):
                                  DUPLICATE_ISSUE=''
                          else:
                                  DUPLICATE_ISSUE= str(int(item['Duplicate/Similar Issue? If Yes Update row number']))
                          if pd.isnull(item['Status']):
                              STATUS= ''
                          else:
                              STATUS= str(item['Status'])
                          if pd.isnull(item['Developers Comments']):
                              DEVELOPERS_COMMENT= ''
                          else:
                              DEVELOPERS_COMMENT= str(item['Developers Comments'])
                              
                          if pd.isnull(item['Leads Comments']):
                             LEADS_COMMENTS= ''
                          else:
                              LEADS_COMMENTS= str(item['Leads Comments']  ) 
                         
                          _id=EDG_NUM+PRDS4_CASE_NUM
                          bmMASTER=BM_MASTER.find_one({'_id' : str(_id)})
                          if bmMASTER is None :
                              inserted_rows=inserted_rows+1
                              print('insert')
                              BM_MASTER.insert({'_id':_id,'SR_NUM' : SR_NUM,'EDG_NUM' : EDG_NUM, 'PRDS4_CASE_NUM' : PRDS4_CASE_NUM,
                                              'DEV_4_CASE_NUMBER' : DEV_4_CASE_NUMBER,'TYPE_OF_ASSISTANCE_CD' : TYPE_OF_ASSISTANCE_CD,
                                              'AGXX02_LAST_ONLINE_AUTH_DATE' : AGXX02_LAST_ONLINE_AUTH_DATE,'GROUPLEVELREASONS': GROUPLEVELREASONS,
                                              'PERSONLEVELREASONS': PERSONLEVELREASONS, 'RTC_ID': RTC_ID,'ASSIGNEE': ASSIGNEE, 'ASSIGNED_DATE' : ASSIGNED_DATE,
                                              'ANALYSIS_COMPLETED': ANALYSIS_COMPLETED, 'DUPLICATE_ISSUE': DUPLICATE_ISSUE,
                                              'STATUS': STATUS,'DEVELOPERS_COMMENT': DEVELOPERS_COMMENT,'LEADS_COMMENTS': LEADS_COMMENTS
                                               })
                          else :
                                updated_rows=updated_rows+1
                                print('update')
                                BM_MASTER.update_one({'_id' : bmMASTER['_id'] },{"$set" : {'RTC_ID': RTC_ID,'ASSIGNEE': ASSIGNEE,
                                                      'ASSIGNED_DATE' : ASSIGNED_DATE, 'ANALYSIS_COMPLETED': ANALYSIS_COMPLETED,
                                                       'DUPLICATE_ISSUE': DUPLICATE_ISSUE,'STATUS': STATUS,'DEVELOPERS_COMMENT': DEVELOPERS_COMMENT,'LEADS_COMMENTS': LEADS_COMMENTS
                                                      }})
                          
                        
                 
        #return render_template('excel_aupload.html')
        print("total rows updated ="+str(updated_rows))
        print("total rows inserted ="+str(inserted_rows))
    return render_template('excel_aupload.html')


@app.route('/download', methods=['GET'])
def download():
    BM_MASTER = mongo.db.BM_MASTER
    BM_MASTER = BM_MASTER.find()
    bmSnapshot=[]
    #columns=[EDG_NUM,PRDS4_CASE_NUM,DEV_4_CASE_NUMBER,TYPE_OF_ASSISTANCE_CD,AGXX02_LAST_ONLINE_AUTH_DATE,GROUPLEVELREASONS,PERSONLEVELREASONS,RTC_ID,ASSIGNEE,ASSIGNED_DATE,DUPLICATE_ISSUE,ANALYSIS_COMPLETED,STATUS,FIXED,DEVELOPERS_COMMENT,LEADS_COMMENTS]
     
    for tempBM in BM_MASTER:
            oBM={
                    'SR_NUM': tempBM['SR_NUM'],
                    'EDG_NUM': tempBM['EDG_NUM'],
                    'PRDS4_CASE_NUM': tempBM['PRDS4_CASE_NUM'],
                    'DEV_4_CASE_NUMBER': tempBM['DEV_4_CASE_NUMBER'],
                    'TYPE_OF_ASSISTANCE_CD' : tempBM['TYPE_OF_ASSISTANCE_CD'],
                    'AGXX02_LAST_ONLINE_AUTH_DATE' :tempBM['AGXX02_LAST_ONLINE_AUTH_DATE'],
                    'GROUPLEVELREASONS' : tempBM['GROUPLEVELREASONS'],
                    'PERSONLEVELREASONS' :  tempBM['PERSONLEVELREASONS'],
                    'RTCID' :  tempBM['RTC_ID'],
                    'Assignee': tempBM['ASSIGNEE'],
                    'Assigned Date' :  tempBM['ASSIGNED_DATE'],
                    'Duplicate/Similar Issue? If Yes, Update row number' :  tempBM['DUPLICATE_ISSUE'],
                    'Analysis Completed(Y/N)' :  tempBM['ANALYSIS_COMPLETED'],
                    'Status' :  tempBM['STATUS'],
                    'Developers Comments' :  tempBM['DEVELOPERS_COMMENT'],
                    'Leads Comments' :  tempBM['LEADS_COMMENTS']
            }
            bmSnapshot.append(oBM)
           # print(bmSnapshot)
            
          
    df =  pd.DataFrame(bmSnapshot)
   # now = datetime.datetime.now()
    #downlaod_dt= now.strftime("%Y-%m-%d %H:%M")
    out_path="C:\\firm software\\new inventory\\BM-Utility\\static\\xls\\BM.xlsx"
    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
    #BM_Columns=pd.DataFrame.from_records(form_info)
   
    df.to_excel(writer,sheet_name="CV006",startrow=0, columns=['SR_NUM','EDG_NUM','PRDS4_CASE_NUM','DEV_4_CASE_NUMBER','TYPE_OF_ASSISTANCE_CD','AGXX02_LAST_ONLINE_AUTH_DATE','GROUPLEVELREASONS','PERSONLEVELREASONS','RTCID','Assignee','Assigned Date','Duplicate/Similar Issue? If Yes Update row number','Analysis Completed(Y/N)','Status','Developers Comments','Leads Comments'],index=False)
    writer.save()
    return render_template('excel_aupload.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    error = None
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email' : request.form['email']})
        error = None
        if existing_user is None:
            name = request.form['name'] 
            email = request.form['email']
            password = request.form['password']
            users.insert({'name' : name, 'email' : email,'password' : password})
            params=[email,password]
            return render_template('Register_Sucess.html',params=params)
        else:
            error = 'User Already Exsist !!!'
    
    return render_template('register.html',error=error)




@app.route('/showusers',methods=['POST','GET'])
def showusers():
     user_snapshot = mongo.db.users
     user_snapshot = user_snapshot.find()
     usersnapShot=[]
     for userStatus in user_snapshot:
        #qty=int(productStatus['product_quantity']) - int(productStatus['no_orders'])      
        oSnapshot={
                'name': userStatus['name'],
                'username': userStatus['username'],
                'password': userStatus['password'],
                'location' : userStatus['location']
                }
        usersnapShot.append(oSnapshot)

     return json.dumps(usersnapShot)
 
@app.route('/showoneuser',methods=['POST','GET'])
def showoneuser():
     user_snapshot = mongo.db.users
     pname=request.json['username']
     user_snapshot = user_snapshot.find({'username':pname})
     userSnapShot=[]
     for userStatus in user_snapshot:
        oSnapshot={
               'name': userStatus['name'],
                'username': userStatus['username'],
                'password': userStatus['password'],
                'location' : userStatus['location'],
                }
        userSnapShot.append(oSnapshot)
     return json.dumps(userSnapShot)
 
@app.route('/updateRecord',methods=['POST'])
def updateRecord():
    if request.method == 'POST':
        BM_MASTER = mongo.db.BM_MASTER
        caseData=request.json['info']
        _id = caseData['_id']
        PRDS4_CASE_NUM = caseData['PRDS4_CASE_NUM']
        ANALYSIS_COMPLETED = caseData['ANALYSIS_COMPLETED'] 
        DUPLICATE_ISSUE= caseData['DUPLICATE_ISSUE']
        STATUS = caseData['STATUS']
        DEVELOPERS_COMMENT = caseData['DEVELOPERS_COMMENT']
        bmMASTER = BM_MASTER.find_one({'_id': _id})
        if bmMASTER is not None: 
            BM_MASTER.update_one({'_id': bmMASTER['_id']},{'$set':{'ANALYSIS_COMPLETED' : str(ANALYSIS_COMPLETED),'DUPLICATE_ISSUE': str(DUPLICATE_ISSUE),
                                    'STATUS': str(STATUS),'DEVELOPERS_COMMENT': str(DEVELOPERS_COMMENT)}})
        return redirect(url_for('showBM'))
    

@app.route('/showBMDataForLeads', methods=['POST', 'GET'])
def showBMDataForLeads():
    return render_template('showBMDataForLeads.html')
    
@app.route('/showAllBMData', methods=['POST', 'GET'])
def showBMData():
    BM_MASTER = mongo.db.BM_MASTER
    BM_MASTER = BM_MASTER.find()
    bmSnapshot=[]
    for tempBM in BM_MASTER:
            oBM={
                    '_id' : str(tempBM['_id']),
                    'SR_NUM' : str(tempBM['SR_NUM']),
                    'EDG_NUM': str(tempBM['EDG_NUM']),
                    'PRDS4_CASE_NUM': str(tempBM['PRDS4_CASE_NUM']),
                    'DEV_4_CASE_NUMBER': str(tempBM['DEV_4_CASE_NUMBER']),
                    'TYPE_OF_ASSISTANCE_CD' : str(tempBM['TYPE_OF_ASSISTANCE_CD']),
                    'AGXX02_LAST_ONLINE_AUTH_DATE' :str(tempBM['AGXX02_LAST_ONLINE_AUTH_DATE']),
                    'GROUPLEVELREASONS' : str(tempBM['GROUPLEVELREASONS']),
                    'PERSONLEVELREASONS' :  str(tempBM['PERSONLEVELREASONS']),
                    'RTC_ID' :  str(tempBM['RTC_ID']),
                    'ASSIGNEE': str(tempBM['ASSIGNEE']),
                    'ASSIGNED_DATE' :  tempBM['ASSIGNED_DATE'],
                    'DUPLICATE_ISSUE' :  tempBM['DUPLICATE_ISSUE'],
                    'ANALYSIS_COMPLETED' :  tempBM['ANALYSIS_COMPLETED'],
                    'STATUS' :  tempBM['STATUS'],
                    'DEVELOPERS_COMMENT' :  tempBM['DEVELOPERS_COMMENT'],
                    'LEADS_COMMENTS' :  tempBM['LEADS_COMMENTS']
                    }
            bmSnapshot.append(oBM)
    return json.dumps(bmSnapshot)

@app.route('/showDetailsForLeads/<case_num>' , methods=['GET'])
def showDetailsForLeads(case_num):
   
     return render_template('showDetailsForLeads.html',case_num=case_num)
 
@app.route('/updateLeadRecord',methods=['POST'])
def updateLeadRecord():
    if request.method == 'POST':
        BM_MASTER = mongo.db.BM_MASTER
        caseData=request.json['info']
        _id=caseData['_id']
        PRDS4_CASE_NUM = caseData['PRDS4_CASE_NUM']
        RTC_ID=caseData['RTC_ID']
        ASSIGNED_DATE=caseData['ASSIGNED_DATE']
        ASSIGNEE=caseData['ASSIGNEE']
        ANALYSIS_COMPLETED = caseData['ANALYSIS_COMPLETED'] 
        DUPLICATE_ISSUE= caseData['DUPLICATE_ISSUE']
        STATUS = caseData['STATUS']
        DEVELOPERS_COMMENT = caseData['DEVELOPERS_COMMENT']
        LEADS_COMMENTS = caseData['LEADS_COMMENTS']
        bmMASTER = BM_MASTER.find_one({'_id': str(_id)})
        if bmMASTER is not None: 
            print(bmMASTER['PRDS4_CASE_NUM'])
            print("Data found updating ")
            result=    BM_MASTER.update_one({'_id': bmMASTER['_id']},{'$set':{'RTC_ID': str(RTC_ID),'ANALYSIS_COMPLETED' : str(ANALYSIS_COMPLETED),'ASSIGNEE': str(ASSIGNEE),'ASSIGNED_DATE': str(ASSIGNED_DATE),
                                  'DUPLICATE_ISSUE': str(DUPLICATE_ISSUE),'STATUS': str(STATUS),'DEVELOPERS_COMMENT': str(DEVELOPERS_COMMENT),'LEADS_COMMENTS': str(LEADS_COMMENTS)}})
            
            print(result.modified_count)
        return redirect(url_for('showBMDataForLeads'))
    
@app.route('/statusSummary' , methods=['GET'])
def statusSummary():
    return render_template('statusSummary.html')  

@app.route('/getStatusData', methods=[ 'GET'])
def getStatusData():
    BM_MASTER = mongo.db.BM_MASTER
    BM_MASTER = BM_MASTER.find()
    analyzing=0
    confirmationPendingFromHarsha=0
    designGap=0
    dataCVIssue=0
    icesInformationNeeded=0
    issueClosed=0
    notToBeAnalyzed=0
    fixInProgress=0
    iedssWorkingICESCleanup=0
    icesDefect=0
    noStatus=0
    for tempBM in BM_MASTER:
                if tempBM['STATUS'] =='Analyzing':
                    analyzing=analyzing+1;
                if tempBM['STATUS'] =='Confirmation Pending from Harsha':
                    confirmationPendingFromHarsha=confirmationPendingFromHarsha+1;
                if tempBM['STATUS'] =='Design Gap':
                    designGap=designGap+1;
                if tempBM['STATUS'] =='Data/CV Issue':
                     dataCVIssue=dataCVIssue+1;
                if tempBM['STATUS'] =='ICES-Information Needed':
                     icesInformationNeeded=icesInformationNeeded+1;
                if tempBM['STATUS'] =='Issue Closed':
                     issueClosed=issueClosed+1;
                if tempBM['STATUS'] =='Not to be analyzed':
                     notToBeAnalyzed=notToBeAnalyzed+1;
                if tempBM['STATUS'] =='Fix In Progress':
                     fixInProgress=fixInProgress+1;
                if tempBM['STATUS'] =='IEDSS is working fine-ICES Clean up':
                     iedssWorkingICESCleanup=iedssWorkingICESCleanup+1;
                if tempBM['STATUS'] =='ICES Defect':
                     icesDefect=icesDefect+1;
                if tempBM['STATUS'] =='ICES Defect':
                     noStatus=noStatus+1;
    oBM={
             'analyzing': analyzing,
             'confirmationPendingFromHarsha': confirmationPendingFromHarsha,
             'designGap' : designGap,
             'dataCVIssue' : dataCVIssue,
             'icesInformationNeeded' : icesInformationNeeded,
             'issueClosed' : issueClosed,
             'notToBeAnalyzed' : notToBeAnalyzed,
             'fixInProgress' : fixInProgress,
             'iedssWorkingICESCleanup' : iedssWorkingICESCleanup,
             'icesDefect' : icesDefect,
             'noStatus' : noStatus
            }
    return json.dumps(oBM)
#downloadStatusSummary for statusSummary
@app.route('/downloadStatusSummary', methods=['POST', 'GET'])
def downloadStatusSummary():
   if request.method == 'POST':
        summary_data=request.json['info']
        print(summary_data)
        colList=['Analyzing','Confirmation Pending from Harsha','Design Gap','Data/CV Issue','ICES-Information Needed','Issue Closed','Not to be analyzed','Fix In Progress','IEDSS is working fine-ICES Clean up','ICES Defect']
        valueList=[summary_data['analyzing'],summary_data['confirmationPendingFromHarsha'],summary_data['designGap'],summary_data['dataCVIssue'],summary_data['icesInformationNeeded'],summary_data['issueClosed'],summary_data['notToBeAnalyzed'],summary_data['fixInProgress'],summary_data['iedssWorkingICESCleanup'],summary_data['icesDefect']]
        print(colList)
        print(valueList)
        
   # now = datetime.datetime.now()
    #downlaod_dt= now.strftime("%Y-%m-%d %H:%M")
    
        
        df =  pd.DataFrame({'Status_Code': colList,
                            'Status_Value':valueList})
        out_path="C:\\firm software\\new inventory\\BM-Utility\\static\\xls\\BMSummary.xlsx"
        UPLOAD_DIRECTORY = 'C:\\firm software\\new inventory\\BM-Utility\\static\\xls\\'
        path='BMSummary.xlsx'
        writer = pd.ExcelWriter(out_path, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Status_Summary',index=False,startcol=5,startrow=7)
        writer.save()
        return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True) 

@app.route('/downloadStatusSummaryInLocal', methods=['GET'])
def downloadStatusSummaryInLocal():
    UPLOAD_DIRECTORY = 'C:\\firm software\\new inventory\\BM-Utility\\static\\xls\\'
    path='BMSummary.xlsx'
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(port=5002,host='0.0.0.0')


