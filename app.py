from datetime import datetime
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
app.config['MYSQL_DB'] = "szamla"

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for("bills_insert"))


@app.route("/bills_insert",methods=["GET","POST"])
def bills_insert():
    if request.method == "POST" and "loggedin" in session and request.form["Szamlaszam"] != "" and  request.form["Megrendeloneve"] != "" and request.form["Osszeg"] != None and request.form["begining"] != "" and  request.form["Hatarido"] != "":
        bill_details = request.form
        bills_id = bill_details["Szamlaszam"]
        costumer_name = bill_details["Megrendeloneve"]
        amount = bill_details["Osszeg"]
        begining = bill_details["begining"]
        deadline = bill_details["Hatarido"]
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(f"INSERT INTO adatok(szam, nev, osszeg, kiallitas, hatarido, teljesitve) VALUES(\"{bills_id}\",{amount},\"{costumer_name}\",\"{begining}\",\"{deadline}\",\"False\")")
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for("bills_insert"))
        except:
            return redirect(url_for("bills_insert"))
    else:
        return render_template("bills_insert.html")


@app.route("/bills", methods=["GET", "POST"])
def bills():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        resultValue = cur.execute(f"SELECT szam,nev,osszeg,kiallitas,hatarido,teljesitve FROM adatok order by teljesitve,szam")
        if resultValue>0:
            userDetails = cur.fetchall()
            line_number = len(userDetails)
            cur.close()
            return render_template('bills.html',userDetails=userDetails,line=line_number,today=date.today().strftime('%Y-%m-%d'))
        else:
            return redirect(url_for("bills_insert"))
    else:
        if request.form["Szamlaszam"] != "" and  request.form["Megrendeloneve"] != "" and request.form["Osszeg"] != None and request.form["Kiallitas"] != "" and  request.form["Hatarido"] != "":
            cur = mysql.connection.cursor()
            checked = 0
            if request.form.get("Teljesitve") != None:
                checked = 1
            try:
                command = f"UPDATE adatok SET szam='{request.form['Szamlaszam']}', osszeg={request.form['Osszeg']}, nev='{request.form['Megrendeloneve']}', kiallitas='{request.form['Kiallitas']}', hatarido='{request.form['Hatarido']}', teljesitve='{checked}' WHERE szamlaszam='{global_id}'"
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
    cur = mysql.connection.cursor()
    now = int(datetime.now().strftime("%Y"))
    print(now)
    now_str = str(int(now))+"-01-01"
    next_str = str(int(now)+1)+"-01-01"
    resultValue = cur.execute(f"SELECT nev,sum(osszeg) From adatok where kiallitas between '{now_str}' AND '{next_str}' group by nev order by sum(osszeg) desc")
    if resultValue>0:
        userDetails = cur.fetchall()
        line_number = range(len(userDetails)+1)[-1]
        cur.close()
        return render_template('companies.html',userDetails=userDetails,line=line_number)
    else:
        return redirect(url_for("bills_insert"))


@app.route("/processUserInfo/<string:userInfo>", methods=["POST"])
def processUserInfo (userInfo):
    userInfo = json.loads(userInfo)
    global global_id 
    global_id = userInfo['global_id']
    print(global_id)
    return "Good"


if __name__ == '__main__':
    app.run(debug=True)