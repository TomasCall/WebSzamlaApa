from datetime import datetime,date
import MySQLdb
from flask import Flask, render_template, request, redirect,session
from flask.helpers import url_for
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import json

from itsdangerous import exc
##FINISHED


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
    if request.method == "POST" and request.form["Szamlaszam"] != "" and  request.form["Megrendeloneve"] != "" and request.form["Osszeg"] != None and request.form["begining"] != "" and  request.form["Hatarido"] != "":
        bill_details = request.form
        bills_id = bill_details["Szamlaszam"]
        costumer_name = bill_details["Megrendeloneve"]
        amount = bill_details["Osszeg"]
        begining = bill_details["begining"]
        deadline = bill_details["Hatarido"]
        print(f"INSERT INTO adatok(szam, nev, osszeg, kiallitas, hatarido, teljesitve) VALUES('{bills_id}','{costumer_name}',{amount},'{begining}','{deadline}','False')")
        try:
            cursor = mysql.connection.cursor()
            cursor.execute(f"INSERT INTO adatok(szam, nev, osszeg, kiallitas, hatarido, teljesitve) VALUES('{bills_id}','{costumer_name}',{amount},'{begining}','{deadline}','False')")
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for("bills_insert"))
        except:
            return redirect(url_for("bills_insert"))
    else:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT nev from adatok")
        names = cursor.fetchall()
        cursor.close()
        return render_template("bills_insert.html",names=names)


@app.route("/bills", methods=["GET", "POST"])
def bills():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        resultValue = cur.execute(f"SELECT szam,nev,osszeg,kiallitas,hatarido,teljesitve,befizetes FROM adatok order by teljesitve,szam")
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
                command = f"UPDATE adatok SET szam='{request.form['Szamlaszam']}', nev='{request.form['Megrendeloneve']}', osszeg={request.form['Osszeg']},  kiallitas='{request.form['Kiallitas']}', hatarido='{request.form['Hatarido']}', teljesitve='{checked}', befizetes='{request.form['Befizetes']}' WHERE szam='{global_id}'"
                cur.execute(command)
                mysql.connection.commit()
                cur.close()
                return redirect(url_for("bills"))
            except:
                return redirect(url_for("bills"))
        else:
            return redirect(url_for("bills"))


@app.route("/companies",methods=["GET", "POST"])
def companies():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        now = int(datetime.now().strftime("%Y"))
        print(now)
        now_str = str(int(now))+"-01-01"
        next_str = str(int(now)+1)+"-01-01"
        print(next_str)
        resultValue = cur.execute(f"SELECT nev,sum(osszeg) From adatok where teljesitve = 1 and befizetes between '{now_str}' AND '{next_str}' group by nev order by sum(osszeg) desc")
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT year(befizetes) FROM adatok WHERE befizetes is not null and befizetes != 0 GROUP BY year(befizetes) order by year(befizetes) desc;")
        years = cursor.fetchall()
        year_string = []
        for item in years:
            year_string.append(str(item[0]))
        print(type(year_string[0][0]))
        if resultValue>0:
            userDetails = cur.fetchall()
            line_number = range(len(userDetails)+1)[-1]
            cur.close()
            selected_date = now
            return render_template('companies.html',userDetails=userDetails,line=line_number,years=year_string,now = str(selected_date))
        else:
            return redirect(url_for("bills_insert"))
    else:
        print(request.form["a"])
        got_year = request.form["a"]
        cur = mysql.connection.cursor()
        print(f"a{type(got_year)}")
        now_str = str(int(got_year))+"-01-01"
        next_str = str(int(got_year)+1)+"-01-01"
        print(next_str)
        resultValue = cur.execute(f"SELECT nev,sum(osszeg) From adatok where teljesitve = 1 and befizetes between '{now_str}' AND '{next_str}' group by nev order by sum(osszeg) desc")
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT year(befizetes) FROM adatok WHERE befizetes is not null and befizetes != 0 GROUP BY year(befizetes) order by year(befizetes) desc;")
        years = cursor.fetchall()
        year_string = []
        for item in years:
            year_string.append(str(item[0]))
        print(type(year_string[0][0]))
        if resultValue>0:
            userDetails = cur.fetchall()
            line_number = range(len(userDetails)+1)[-1]
            cur.close()
            return render_template('companies.html',userDetails=userDetails,line=line_number,years=year_string,now = got_year)
        else:
            return redirect(url_for("bills_insert"))


@app.route("/statistic",methods=["GET", "POST"])
def statistic():
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)=(Select max(year(kiallitas)) from adatok) group by month(kiallitas) ")
        years_bigger = cursor.fetchall()
        cursor.close()
        print(years_bigger[0][1])
        just_years_bigger = [0,0,0,0,0,0,0,0,0,0,0,0]
        for item in years_bigger:
            just_years_bigger[item[1]-1]=int(item[0])

        cursor_second = mysql.connection.cursor()
        cursor_second.execute(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)=(Select max(year(kiallitas)-1) from adatok) group by month(kiallitas) ")
        years_smaller = cursor_second.fetchall()
        cursor_second.close()

        just_years_smaller = [0,0,0,0,0,0,0,0,0,0,0,0]
        for item in years_smaller:
            just_years_smaller[item[1]-1]=int(item[0])


        sixty_percents = []
        for item in just_years_bigger:
            sixty_percents.append(round(item*0.6))

        comparison_percents = []
        for i in range(12):
            if just_years_smaller[i] !=0:
                comparison_percents.append(round(((just_years_bigger[i]-just_years_smaller[i])/just_years_smaller[i])*100))
            else:
                comparison_percents.append(-100)

        cursor_third =  mysql.connection.cursor()
        cursor_third.execute(f"SELECT year(kiallitas) FROM adatok WHERE befizetes is not null and befizetes != 0 GROUP BY year(kiallitas) order by year(kiallitas) desc;")
        years_for_select = cursor_third.fetchall()
        cursor_third.close()
        year_string = []
        for item in years_for_select:
            year_string.append(str(item[0]))
        first = sum(just_years_bigger)
        second = sum(just_years_smaller)
        third = first-second
        fourth = sum(sixty_percents)
        return render_template("statistic.html",bigger_year=just_years_bigger,just_years_smaller=just_years_smaller,sixty_percents=sixty_percents,comparison_percents=comparison_percents,years=year_string,now=year_string[0],before=int(year_string[0])-1,first=first,second=second,third=third,fourth=fourth)
    else:
        selected_year = int(request.form["a"])
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)={selected_year} group by month(kiallitas)")
        years_bigger = cursor.fetchall()
        cursor.close()

        just_years_bigger = [0,0,0,0,0,0,0,0,0,0,0,0]
        for item in years_bigger:
            just_years_bigger[item[1]-1]=int(item[0])

        cursor_second = mysql.connection.cursor()
        cursor_second.execute(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)={selected_year-1} group by month(kiallitas)")
        years_smaller = cursor_second.fetchall()
        print(type(years_smaller[0][1]))
        cursor_second.close()
        print(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)={selected_year-1} group by month(kiallitas)")
        just_years_smaller = [0,0,0,0,0,0,0,0,0,0,0,0]
        for item in years_smaller:
            just_years_smaller[item[1]-1]=int(item[0])

        print(years_smaller)
        sixty_percents = []
        for item in just_years_bigger:
            sixty_percents.append(round(item*0.6))

        comparison_percents = []
        for i in range(12):
            if just_years_smaller[i] !=0:
                comparison_percents.append(round(((just_years_bigger[i]-just_years_smaller[i])/just_years_smaller[i])*100))
            else:
                comparison_percents.append(-100)

        cursor_third =  mysql.connection.cursor()
        cursor_third.execute(f"SELECT year(kiallitas) FROM adatok WHERE befizetes is not null and befizetes != 0 GROUP BY year(kiallitas) order by year(kiallitas) desc;")
        years_for_select = cursor_third.fetchall()
        cursor_third.close()
        year_string = []
        for item in years_for_select:
            year_string.append(str(item[0]))
        first = sum(just_years_bigger)
        second = sum(just_years_smaller)
        third = first-second
        fourth = sum(sixty_percents)
        return render_template("statistic.html",bigger_year=just_years_bigger,just_years_smaller=just_years_smaller,sixty_percents=sixty_percents,comparison_percents=comparison_percents,years=year_string,now=str(selected_year),before=selected_year-1,first=first,second=second,third=third,fourth=fourth)

@app.route("/processUserInfo/<string:userInfo>", methods=["POST"])
def processUserInfo (userInfo):
    userInfo = json.loads(userInfo)
    global global_id 
    global_id = userInfo['global_id']
    print(global_id)
    return "Good"


if __name__ == '__main__':
    app.run(debug=True)