from datetime import datetime,date
import MySQLdb
from flask import Flask, render_template, request, redirect,session
from flask.helpers import url_for
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import json

from itsdangerous import exc

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "szamla"

mysql = MySQL(app)

selected_year = int(datetime.now().strftime("%Y"))

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


@app.route("/bills", methods=["GET", "POST","PUT"])
def bills():
    global selected_year
    if request.method == "GET":
        print(selected_year)
        now_str = str(int(selected_year))+"-01-01"
        next_str = str(int(selected_year)+1)+"-01-01"
        user_details = my_msql_executer(f"SELECT szam,nev,osszeg,kiallitas,hatarido,teljesitve,befizetes FROM adatok  where kiallitas between '{now_str}' and '{next_str}' order by teljesitve,kiallitas")
        user_details = sorted(user_details,key=lambda col: col[0][0])
        if len(user_details)>0:
            line_number = len(user_details)
            years = get_years("kiallitas")
            return render_template('bills.html',user_details=user_details,line=line_number,today=date.today().strftime('%Y-%m-%d'),years=years,now=str(selected_year))
        else:
            return redirect(url_for("bills_insert"))
    elif request.method == "POST":
        print(f"{request.form}")
        if len(request.form) != 1:
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
        else:
            years = get_years("kiallitas")
            got_year = request.form["a"]
            selected_year = int(got_year)
            now_str = str(int(got_year))+"-01-01"
            next_str = str(int(got_year)+1)+"-01-01"
            user_details = my_msql_executer(f"SELECT szam,nev,osszeg,kiallitas,hatarido,teljesitve,befizetes FROM adatok  where kiallitas between '{now_str}' and '{next_str}' order by teljesitve,kiallitas")
            user_details = sorted(user_details,key=lambda col: col[0][0])
            return render_template('bills.html',user_details=user_details,line=len(user_details),today=date.today().strftime('%Y-%m-%d'),years=years,now=got_year)



@app.route("/companies",methods=["GET", "POST"])
def companies():
    if request.method == "GET":
        now = int(datetime.now().strftime("%Y"))
        print(now)
        now_str = str(int(now))+"-01-01"
        next_str = str(int(now)+1)+"-01-01"
        print(next_str)
        user_details = my_msql_executer(f"SELECT nev,sum(osszeg) From adatok where teljesitve = 1 and befizetes between '{now_str}' AND '{next_str}' group by nev order by sum(osszeg) desc")
        years = get_years("befizetes")#cursor.fetchall()
        if len(user_details)>0:
            line_number = range(len(user_details)+1)[-1]
            selected_datee = now
            return render_template('companies.html',user_details=user_details,line=line_number,years=years,now = str(selected_datee))
        else:
            return redirect(url_for("bills_insert"))
    else:
        got_year = request.form["a"]
        print(f"a{type(got_year)}")
        now_str = str(int(got_year))+"-01-01"
        next_str = str(int(got_year)+1)+"-01-01"
        print(next_str)
        user_details = my_msql_executer(f"SELECT nev,sum(osszeg) From adatok where teljesitve = 1 and befizetes between '{now_str}' AND '{next_str}' group by nev order by sum(osszeg) desc")
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT year(befizetes) FROM adatok WHERE befizetes is not null and befizetes != 0 GROUP BY year(befizetes) order by year(befizetes) desc;")
        years = get_years("befizetes")
        if len(user_details)>0:
            line_number = range(len(user_details)+1)[-1]
            return render_template('companies.html',user_details=user_details,line=line_number,years=years,now = got_year)
        else:
            return redirect(url_for("bills_insert"))


@app.route("/statistic",methods=["GET", "POST"])
def statistic():
    if request.method == "GET":
        years_bigger = my_msql_executer(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)=(Select max(year(kiallitas)) from adatok) group by month(kiallitas) ")
        print(years_bigger[0][1])
        just_years_bigger = [0,0,0,0,0,0,0,0,0,0,0,0]
        for item in years_bigger:
            just_years_bigger[item[1]-1]=int(item[0])

        years_smaller = my_msql_executer(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)=(Select max(year(kiallitas)-1) from adatok) group by month(kiallitas) ")
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

        years_for_select = get_years("kiallitas")
        first = sum(just_years_bigger)
        second = sum(just_years_smaller)
        third = first-second
        fourth = sum(sixty_percents)
        return render_template("statistic.html",bigger_year=just_years_bigger,just_years_smaller=just_years_smaller,sixty_percents=sixty_percents,comparison_percents=comparison_percents,years=years_for_select,now=years_for_select[0],before=int(years_for_select[0])-1,first=first,second=second,third=third,fourth=fourth)
    else:
        selected_year = int(request.form["a"])

        years_bigger = my_msql_executer(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)={selected_year} group by month(kiallitas)")
        just_years_bigger = [0,0,0,0,0,0,0,0,0,0,0,0]
        for item in years_bigger:
            just_years_bigger[item[1]-1]=int(item[0])


        years_smaller = my_msql_executer(f"SELECT sum(osszeg),month(kiallitas) FROM adatok WHERE year(kiallitas)={selected_year-1} group by month(kiallitas)")
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

        year_string = get_years("kiallitas")
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


def get_years(name_of_year):
    years = my_msql_executer(f"SELECT year({name_of_year}) FROM adatok WHERE befizetes is not null and {name_of_year} != 0 GROUP BY year({name_of_year}) order by year({name_of_year}) desc;")
    year_string = []
    for item in years:
        year_string.append(str(item[0]))
    return year_string


def my_msql_executer(command):
    cursor = mysql.connection.cursor()
    cursor.execute(command)
    datas = cursor.fetchall()
    cursor.close()
    return datas

#a

if __name__ == '__main__':
    app.run(debug=True)

