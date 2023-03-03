from flask import *
from flask_mysqldb import *
import MySQLdb.cursors
import re
from flask_login import *
from flask_session import Session
from flask_googlemaps import *
import googlemaps



app=Flask(__name__)
app.secret_key = 'your secret key'
#Database Config to Flask
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'tiger'
app.config['MYSQL_DB'] = 'amazon'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# googlemaps API key
API_KEY='AIzaSyAFe4wqGLZzrpPqWYCifazdAxLqocTbbnc'

# map_address = googlemaps.Client(API_KEY)




mysql = MySQL(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Login_manager Assign to Flask



@app.route('/',methods=['GET', 'POST'])
def index():
    msg=" "
    session['role']=None
    if request.method == 'POST':
        
        details=request.form
        name=details['username']
        password=details['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM users WHERE name = %s and password = %s',[name, password])
        user = cur.fetchone()
        if user:
            session['name'] = name
            role=user['role']
            session['role'] = role
            # address_1='1 market st, San Francisco, CA'
            # loc = map_address.geocode(address_1)

            # print(loc[0]['geometry'])
            if role=='admin':
                return  redirect(url_for('dashboard'))
            elif role=='user' or role=='approver' :
                return redirect(url_for('dashboard'))
        else:
            msg='Usrname or Password Incorrect'
    return render_template('index.html',msg=msg)



@app.route('/register',methods=['GET','POST'])
def register():
    msg=""
    if request.method=='POST':
        details=request.form 
        name=details['name']
        email=details['email']
        mnumber=details['mobilenumber']
        password=details['password']
        confirmpassword=details['confirmpassword']
        if password == confirmpassword:
            regmsg="Register Successfully"
            return render_template('index.html',regmsg=regmsg)
        else :
            msg='Password Does not match'
    return render_template('register.html')































@app.route('/dashboard')
#login_required

def dashboard():
    if session['role']:
        cur=mysql.connection.cursor()
        cur.execute('select * from products ')
        products=cur.fetchall()
        return render_template('dashboard.html', product=products)
    else:
        print("The System Falls")
        return redirect("/")



































@app.route('/amproducts',methods=['GET','POST'])
#login_required
def products():
    if session['role'] == 'admin':
        cur=mysql.connection.cursor()
        rvalue=cur.execute("select * from products ")
        if rvalue > 0:
            products=cur.fetchall()
            return render_template('products.html',product=products)
        else:
            return render_template('noproduct.html')
        mysql.connection.commit()
    else:
        return redirect('/')
    

@app.route('/create', methods=['GET','POST'])
#login_required
def create():
    cur=mysql.connection.cursor()
    #for adding Product
    
    if request.method == 'POST':
        prodetails=request.form
        cur=mysql.connection.cursor()
        cur.execute("select procode from products")
        pro=cur.fetchall()       
        msg=""
        name=prodetails['crproname']
        code=prodetails['crprocode']
        price=prodetails['crprice']
        quantity=prodetails['crquantity']
        dealer=prodetails['crdealer']
        status=prodetails['crstatus']         
        cur.execute('insert into products(procode,proname,price,quantity,procompany,status) values(%s, %s, %s, %s, %s, %s)',[code, name, price, quantity, dealer, status ])
        mysql.connection.commit()
        cur.execute('select MAX(productid) from products')
        c=cur.fetchone()
        curid=c.get('MAX(productid)')
            
    
        msg="Product Create Successfully"
        return jsonify({"status":msg, "productid":curid})
        
    
    

@app.route('/editproduct',methods=['GET', 'POST'])
#login_required
def editproduct():
    cur=mysql.connection.cursor()

    if request.method == 'POST':
        product=request.form
        #edit details of product
        productid=product['edproductid']
        code=product['edprocode']
        name=product['edproname']
        price=product['edprice']
        quantity=product['edquantity']
        dealer=product['eddealer']
        status=product['edstatus']
        print()
        print("hi")
        print()


        quary="update products set  procode=%s,proname=%s,price=%s,Quantity=%s,procompany=%s,status=%s where productid=%s"
        cur.execute(quary,[code, name, price, quantity, dealer, status, productid])
        mysql.connection.commit()
        
        msg="Done"
        return jsonify({"status":msg, productid_1:productid})


















@app.route('/productsearch',methods=['GET','POST'])
def productsearch():
    cur=mysql.connection.cursor()
    if request.method == 'POST':
        name=request.form['productsearch']
        if name != " ":
            cur.execute("select * from products where proname like '%{}%'".format(name))
            searched_products=cur.fetchall()
    return jsonify ({'success':True,'value':searched_products})
















    
    

@app.route('/mycart',methods=['GET', 'POST'])
def mycart():
    cur=mysql.connection.cursor()
    cur.execute("select * from carts where name=%s",[session['name']])
    products=cur.fetchall()
    cur.close()
    print(session)
    return render_template('mycart.html',product=products)


# adding a product to the cart
@app.route('/addtocart',methods=['GET','POST'])
def addtocart():
    if request.method =='POST':
        
        id=request.form['id']
        quantity=request.form['quantity']
        print(quantity)
        cur=mysql.connection.cursor()
        cur.execute('select * from products where productid=%s',[id])
        a=cur.fetchone()
        proname = a["proname"]
        print(proname)
        price = a["price"]
        cur.execute('select proname from carts where name=%s and proname=%s',[session['name'], proname])
        exist=cur.fetchone()
        

        if exist:
            print("Already Exist")
            cur.execute('select quantity from carts where name=%s and proname=%s',[session['name'], proname])
            existquantity=cur.fetchone()
            val=existquantity["quantity"]
            print(val)
            print(type(val))
            print(type(quantity))
            val=val+int(quantity)
            cur.execute('update carts set quantity=%s where proname=%s and name=%s',[val, proname, session['name']])

            mysql.connection.commit()
        else:
            print("New Adding")
            cur.execute('insert into carts(name, proname, price, quantity) values(%s, %s, %s, %s)',[session['name'], proname, price, quantity])
            mysql.connection.commit()
    return jsonify({'success': True})


@app.route('/address',methods=['GET','POST'])
def address():
    cur=mysql.connection.cursor()
    cur.execute("select * from delivery where name=%s",[session['name']])
    address=cur.fetchall()    
    return render_template('address.html', address=address)


@app.route('/addaddress',methods=['GET','POST'])
def addaddress():
    if request.method=='POST':
        add=request.form
        holdername=add['crholdername']
        houseno=add['crhouseno']
        streetname=add['crstreetname']
        areaname=add['crareaname']
        districtname=add['crdistrictname']
        mobilenumber=add['crmobilenumber']
        cur=mysql.connection.cursor()
        cur.execute('select * from delivery where name=%s',[session['name']])
        d=cur.fetchone()
        if d== None:
            cur.execute('insert into delivery(name, holdername, houseno, streetname, areaname, districtname, mobilenumber, primary_address ) values(%s, %s, %s, %s, %s, %s, %s, "p")',[ session['name'], holdername, houseno, streetname, areaname, districtname, mobilenumber])
        else:
            cur.execute('insert into delivery(name, holdername, houseno, streetname, areaname, districtname, mobilenumber ) values(%s, %s, %s, %s, %s, %s, %s)',[ session['name'], holdername, houseno, streetname, areaname, districtname, mobilenumber])
        mysql.connection.commit()
        cur.execute('select MAX(sl_no) from delivery')
        c=cur.fetchone()
        addressid=c.get('MAX(sl_no)')
        msg="imported Success"
    return jsonify({'status':msg, "addressid":addressid})

@app.route('/editaddress',methods=['GET','POST'])
def editaddress():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        edit=request.form


@app.route('/deleteaddress',methods=['GET','POST'])
def deleteaddress():
    cur=mysql.connection.cursor()
    addressstatus='Deleted'
    if request.method=='POST':
        delete=request.form
        id=delete['id']
        print(id)
        cur.execute('select primary_address from delivery where sl_no=%s',[id])
        primary_address=cur.fetchone()
        s=primary_address['primary_address']
        if s=='n':
            cur.execute('update delivery set status="No" where sl_no=%s',[id])
        else:
            addressstatus='NotDeleted'
        mysql.connection.commit()
    return jsonify({'status':addressstatus})


@app.route('/changeprimaryaddress',methods=['GET','POST'])
def changeprimaryaddress():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        change=request.form
        id=change['id']
        cur.execute('select sl_no from delivery where name=%s and primary_address="p"',[session['name']])
        CurrentPrimaryAddress=cur.fetchone()
        CurrentPrimaryAddressId=CurrentPrimaryAddress['sl_no']
        intid=int(id)
        if intid != CurrentPrimaryAddressId:
            cur.execute('update delivery set primary_address="n" where sl_no=%s',[CurrentPrimaryAddressId])
            cur.execute('update delivery set primary_address="p" where sl_no=%s',[id])
            status="Changed"
        else:
            status="Unchanged"
        print(status)
        mysql.connection.commit()
        return jsonify({'status':status})


@app.route('/buyproducts',methods=['GET','POST'])
def buyproducts():
    cur=mysql.connection.cursor()
    cur.execute('select * from carts where name=%s',[session['name']])
    products=cur.fetchall()
    cur.execute('select sum(price * quantity) from carts where name=%s',[session['name']])
    a=cur.fetchone()
    b=a["sum(price * quantity)"]
    cur.execute('select * from delivery where name=%s and status="Yes"',[session['name']])
    n=cur.fetchall()
    return render_template('buyproducts.html', products=products, totalprice=b, addresses=n)






@app.route('/orderhistory',methods=['GET','POST'])
def orderhistory():
    return render_template('orderhistory.html')



@app.route('/contactus')
def contactus():
    return render_template('contactus.html')


















#Approver Setting

@app.route('/approveseller',methods=['GET','POST'])
def approveseller():
    cur=mysql.connection.cursor()
    cur.execute('select * from request')
    requests=cur.fetchall()
    return render_template('approveseller.html', request=requests)




@app.route('/approveproduct',methods=['GET','POST'])
def approveproduct():
    cur=mysql.connection.cursor()
    cur.execute('select * from productrequest')
    requests=cur.fetchall()
    return render_template('approveproduct.html',request=requests)


@app.route('/approvehistory',methods=['GET','POST'])
def approvehistory():
    return "hai"






















@app.route('/logout')
def logout():
    session['role']=None
    return redirect("/")



if __name__=='__main__':
    app.run(debug=True)