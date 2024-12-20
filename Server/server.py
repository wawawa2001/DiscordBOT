import sys
sys.path.append('../')
from settings import *
from flask import Flask, render_template, request

import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

hostname = HOSTNAME
username = USERNAME
password = PASSWORD
dbname = DBNAME


def create_connection(hostname, username, password, dbname):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            passwd=password,
            database=dbname,
            port=3306,
        )
    except Error as e:
        print("Connection Error :(")
    
    return connection

def execute_param_query(query, params):
    connection = create_connection(hostname, username, password, dbname)
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
    except Error as e:
        print("Execute Error :(")
    finally:
        cursor.close()

def execute_read_query(query, params=None):
    connection = create_connection(hostname, username, password, dbname)
    cursor = connection.cursor()

    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("Execute Error :(")
    finally:
        cursor.close()

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/Pomodoro_history")
def Pomodoro_history():
    query = """
        SELECT *
        FROM Pomodoro_history;
    """

    result = execute_read_query(query)

    return render_template("history.html", data=result)

@app.route("/Pomodoro_process")
def Pomodoro_Process():
    query = """
        SELECT * FROM Pomodoro;
    """

    result = execute_read_query(query)

    return render_template("process.html", data=result)

@app.route("/delete_user/<string:username>", methods=["DELETE"])
def Delete_user(username):
    query = """
        DELETE FROM Pomodoro_history WHERE username = %s;
    """

    params = (username, )

    execute_param_query(query, params)

    return "OK"

@app.route("/delete_process/<int:no>", methods=["DELETE"])
def Delete_Process(no):
    query = """
        DELETE FROM Pomodoro WHERE id = %s;
    """

    params = (no, )

    execute_param_query(query, params)

    return "OK"

@app.route("/delete_history/<int:no>", methods=["DELETE"])
def Delete_history(no):
    query = """
        DELETE FROM Pomodoro_history WHERE id = %s;
    """

    params = (no, )

    execute_param_query(query, params)

    return "OK"

@app.route("/Pomodoro_total_time")
def Pomodoro_total_time():
    query = """
        SELECT username, SUM(minutes) as total_value
        FROM Pomodoro_history
        GROUP BY username;
    """

    result = execute_read_query(query)
    data = []
    for item in result:
        list_item = list(item)
        minutes = int(list_item[-1])
        hour = int(minutes / 60)
        minutes = minutes - (hour * 60)
        list_item[-1] = str(hour) + "時間 " + str(minutes) + "分"
        data.append(list(list_item))
    
    return render_template("total.html", data=data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=22245)