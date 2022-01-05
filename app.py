from datetime import date, datetime
import MySQLdb
from flask import Flask, render_template, request, redirect,session
from flask.helpers import url_for
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import json


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "webszamla"

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("home.html")

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST" and request.form["username"] != "" and request.form["email"] is not "" and request.form["password"] is not "":
        userDetails = request.form
        name = userDetails["username"]
        email = userDetails["email"]
        password = bcrypt.generate_password_hash(userDetails["password"]).decode("utf-8")
        try:
            cur = mysql.connection.cursor()
            cur.execute(f"INSERT INTO user(felhasznalonev, email, jelszo) VALUES(\"{name}\",\"{email}\",\"{password}\")")
            mysql.connection.commit()
            cur.close()
            session["loggedin"] = True
            session["username"] = userDetails["username"]
            return redirect(url_for("user"))
        except:
             return redirect(url_for("user"))
    return render_template("registration.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = 'Bejelentkezés'
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        cursor = mysql.connection.cursor()
        command = f"SELECT felhasznalonev,email,jelszo FROM user WHERE felhasznalonev = '{username}'"
        cursor.execute(command)
        account = cursor.fetchall()
        cursor.close()
        try:
            if bcrypt.check_password_hash(account[0][2], password):
                session["loggedin"] = True
                session["username"] = username
                return redirect("/user")
        except:
            print("Something bad happend")
    return render_template('login.html', msg=msg)

@app.route("/user")
def user():
    if "loggedin" in session:
        return render_template('user.html')
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
   session.pop("loggedin", None)
   session.pop("username", None)
   return redirect(url_for("login"))


@app.route("/bills_insert",methods=["GET","POST"])
def bills_insert():
    if "loggedin" in session:
        if request.method == "POST" and "loggedin" in session and request.form["Szamlaszam"] != "" and  request.form["Megrendeloneve"] != "" and request.form["Osszeg"] != None and request.form["begining"] != "" and  request.form["Hatarido"] != "":
            bill_details = request.form
            bills_id = bill_details["Szamlaszam"]
            costumer_name = bill_details["Megrendeloneve"]
            amount = bill_details["Osszeg"]
            begining = bill_details["begining"]
            deadline = bill_details["Hatarido"]
            try:
                cursor = mysql.connection.cursor()
                cursor.execute(f"INSERT INTO datas(szamlaszam, osszeg, megrendeloneve, megrendeles_datuma, hatarido,felhasznalonev) VALUES(\"{bills_id}\",{amount},\"{costumer_name}\",\"{begining}\",\"{deadline}\",\"{session['username']}\")")
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for("bills_insert"))
            except:
                return redirect(url_for("bills_insert"))
        else:
            return render_template("bills_insert.html")
    return redirect(url_for("home"))


@app.route("/bills", methods=["GET", "POST"])
def bills():
    if request.method == "GET":
        if "loggedin" in session:
            cur = mysql.connection.cursor()
            resultValue = cur.execute(f"SELECT szamlaszam,megrendeloneve,osszeg,megrendeles_datuma,hatarido,teljesitve FROM datas where felhasznalonev='{session['username']}' order by teljesitve,szamlaszam")
            if resultValue>0:
                userDetails = cur.fetchall()
                line_number = len(userDetails)
                cur.close()
                return render_template('bills.html',userDetails=userDetails,line=line_number,today=date.today().strftime('%Y-%m-%d'))
            else:
                return redirect(url_for("bills_insert"))
        else:
            return redirect(url_for("home"))
    else:
        if request.form["Szamlaszam"] != "" and  request.form["Megrendeloneve"] != "" and request.form["Osszeg"] != None and request.form["Kiallitas"] != "" and  request.form["Hatarido"] != "":
            cur = mysql.connection.cursor()
            checked = 0
            if request.form.get("Teljesitve") != None:
                checked = 1
            try:
                command = f"UPDATE datas SET szamlaszam='{request.form['Szamlaszam']}', osszeg={request.form['Osszeg']}, megrendeloneve='{request.form['Megrendeloneve']}', megrendeles_datuma='{request.form['Kiallitas']}', hatarido='{request.form['Hatarido']}', teljesitve='{checked}' WHERE szamlaszam='{global_id}'"
                cur.execute(command)
                mysql.connection.commit()
                cur.close()
                return redirect(url_for("bills"))
            except:
                return redirect(url_for("bills"))
        else:
            return redirect(url_for("bills"))


@app.route("/companies")
def companies():
    if "loggedin" in session:
        cur = mysql.connection.cursor()
        now = int(datetime.now().strftime("%Y"))
        now_str = str(int(now))+"-01-01"
        next_str = str(int(now)+1)+"-01-01"
        resultValue = cur.execute(f"SELECT megrendeloneve,sum(osszeg) From datas where felhasznalonev = '{session['username']}' and megrendeles_datuma between '{now_str}' AND '{next_str}' group by megrendeloneve order by sum(osszeg) desc")
        if resultValue>0:
            userDetails = cur.fetchall()
            line_number = range(len(userDetails)+1)[-1]
            cur.close()
            return render_template('companies.html',userDetails=userDetails,line=line_number)
        else:
            return redirect(url_for("bills_insert"))
    return redirect(url_for("home.html"))


@app.route("/processUserInfo/<string:userInfo>", methods=["POST"])
def processUserInfo (userInfo):
    userInfo = json.loads(userInfo)
    global global_id 
    global_id = userInfo['global_id']
    print(global_id)
    return "Good"


if __name__ == '__main__':
    app.run(debug=True)