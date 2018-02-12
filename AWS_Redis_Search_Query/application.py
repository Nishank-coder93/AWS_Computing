from __future__ import print_function
from flask import Flask, render_template, request
import  MySQLdb as mdb
import redis
import time
import hashlib
import cPickle
import random

application = Flask(__name__)
application.config.from_object('config')

# Connecting with DB
try:
    con = mdb.connect(
        host=application.config["MYSQL_HOST"],
        user=application.config["MYSQL_USER"],
        passwd=application.config["MYSQL_PASSWORD"],
        db=application.config["MYSQL_DATABASE_NAME"]
    )
except mdb.Error, e:
    print("Error %s" % (e.args[1]))

# Redis Connection and Redis Object creation
pool = redis.ConnectionPool(host='', port=0000, db=0)
redis_server = redis.Redis(connection_pool=pool)

# Start time
startTime = time.time()

# SQL Cursor
cur = con.cursor()

@application.route('/', methods=['GET','POST'])
def init_method():
    if request.method == 'GET':
        return render_template('first_page.html')
    elif request.method == 'POST':

        cur.execute("SELECT * FROM people")
        result = cur.fetchone()

        cur.execute("SELECT COUNT(*) FROM people")
        res = cur.fetchall()

        return render_template('first_page.html', query=result, numOfEnt=res[0][0])

@application.route('/query1', methods=['GET','POST'])
def query_one():
    if request.method == 'GET':
        return render_template("query_one.html")
    elif request.method == "POST":
        surname = request.form['surname']


        query = "SELECT GivenName,Telephone,State  FROM people WHERE Surname = '" + surname + "'"
        hash  = hashlib.sha224(query).hexdigest()
        key = "sql_cache:" + hash

        # check if data is in Cache
        if (redis_server.get(key)):
            time_before_call = time.time()
            data = cPickle.loads(redis_server.get(key))
            time_after_call = time.time()

            call_time   = (time_after_call - time_before_call) * 1000
            #print(data)
            return render_template("query_one.html", datainfo=data, qDoneBy="Redis", calltime=call_time)
        else:
            # Execute the Query
            time_before_call = time.time()
            cur.execute(query)
            data = cur.fetchall()
            time_after_call = time.time()
            call_time = (time_after_call - time_before_call) * 1000

            # Put data in cache for an hour
            redis_server.set(key,cPickle.dumps(data))
            redis_server.expire(key, 36)

            # Set data in redis and load Data
            redis_data = cPickle.loads(redis_server.get(key))
            #print(redis_data)

            return render_template("query_one.html", datainfo = redis_data, qDoneBy="MySQL", calltime=call_time )


# Height From and To and State Code
@application.route('/query2', methods=['GET','POST'])
def query_2():
    if (request.method == 'GET'):
        return render_template("query_two.html")
    elif (request.method == 'POST'):
        height_from = request.form['ht_from']
        height_to = request.form['ht_to']
        state_code = request.form['st_code']

        query = "SELECT * FROM people WHERE State = '" + state_code + "' AND Centimeters BETWEEN " + height_from + " AND " + height_to
        print(query)

        hash = hashlib.sha224(query).hexdigest()
        key = "sql_cache:" + hash

        # check if data is in Cache
        if (redis_server.get(key)):
            time_before_call = time.time()
            data = cPickle.loads(redis_server.get(key))
            time_after_call = time.time()

            call_time = (time_after_call - time_before_call) * 1000
            # print(data)
            return render_template("query_two.html", datainfo=data, qDoneBy="Redis", calltime=call_time)
        else:
            # Execute the Query
            time_before_call = time.time()
            cur.execute(query)
            data = cur.fetchall()
            time_after_call = time.time()
            call_time = (time_after_call - time_before_call) * 1000

            # Put data in cache for an hour
            redis_server.set(key, cPickle.dumps(data))
            redis_server.expire(key, 36)

            # Set data in redis and load Data
            redis_data = cPickle.loads(redis_server.get(key))
            # print(redis_data)

            return render_template("query_two.html", datainfo=redis_data, qDoneBy="MySQL", calltime=call_time)

@application.route('/query3', methods=['GET','POST'])
def query_3():
    if (request.method == 'GET'):
        return render_template("query_two.html")
    elif (request.method == 'POST'):
        height_from = request.form['ht_form']
        height_to = request.form['ht_to']
        state_code = request.form['st_code']

        query = "SELECT * FROM boat WHERE State = '" + state_code + "' AND Centimeters BETWEEN " + height_from + " AND " + height_to + ""
        hash = hashlib.sha224(query).hexdigest()
        key = "sql_cache:" + hash

        # check if data is in Cache
        if (redis_server.get(key)):
            time_before_call = time.time()
            data = cPickle.loads(redis_server.get(key))
            time_after_call = time.time()

            call_time = (time_after_call - time_before_call) * 1000
            # print(data)
            return render_template("query_two.html", datainfo=data, qDoneBy="Redis", calltime=call_time)
        else:
            # Execute the Query
            time_before_call = time.time()
            cur.execute(query)
            data = cur.fetchall()
            time_after_call = time.time()
            call_time = (time_after_call - time_before_call) * 1000

            # Put data in cache for an hour
            redis_server.set(key, cPickle.dumps(data))
            redis_server.expire(key, 36)

            # Set data in redis and load Data
            redis_data = cPickle.loads(redis_server.get(key))
            # print(redis_data)

            return render_template("query_two.html", datainfo=redis_data, qDoneBy="MySQL", calltime=call_time)

## Update to 'new' table
@application.route('/query4', methods=['GET','POST'])
def query_4():
    if (request.method == 'GET'):
        return render_template("query_two.html")
    elif (request.method == 'POST'):
        height_from = request.form['ht_from']
        height_to = request.form['ht_to']

        query = "SELECT * FROM boat WHERE  Centimeters BETWEEN " + height_from + " AND " + height_to + ""
        hash = hashlib.sha224(query).hexdigest()
        key = "sql_cache:" + hash

        # check if data is in Cache
        if (redis_server.get(key)):
            time_before_call = time.time()
            data = cPickle.loads(redis_server.get(key))
            time_after_call = time.time()

            call_time = (time_after_call - time_before_call) * 1000
            # print(data)
            return render_template("query_two.html", datainfo=data, qDoneBy="Redis", calltime=call_time)
        else:
            # Execute the Query
            time_before_call = time.time()
            cur.execute(query)
            data = cur.fetchall()
            time_after_call = time.time()
            call_time = (time_after_call - time_before_call) * 1000

            # Put data in cache for an hour
            redis_server.set(key, cPickle.dumps(data))
            redis_server.expire(key, 36)

            # Set data in redis and load Data
            redis_data = cPickle.loads(redis_server.get(key))
            # print(redis_data)

            return render_template("query_two.html", datainfo=redis_data, qDoneBy="MySQL", calltime=call_time)


@application.route('/query5', methods=['GET','POST'])
def query_5():
    if (request.method == 'GET'):
        return render_template("query_five.html")
    elif (request.method == 'POST'):
        height_from = request.form['ht_from']
        height_to = request.form['ht_to']
        state_code = request.form['st_code']
        rand_number = request.form['rand_number']

        query = "SELECT * FROM people WHERE State = '" + state_code + "' AND Centimeters BETWEEN " + height_from + " AND " + height_to + ""
        hash = hashlib.sha224(query).hexdigest()
        key = "sql_cache:" + hash

        call_time = 0

        for i in range(int(rand_number)):
            if(redis_server.get(key)):
                time_before_call = time.time()
                data = cPickle.loads(redis_server.get(key))
                time_after_call = time.time()
                call_time = (time_after_call - time_before_call) * 1000
            else:
                # Execute the Query
                time_before_call = time.time()
                cur.execute(query)
                data = cur.fetchall()
                time_after_call = time.time()
                call_time = (time_after_call - time_before_call) * 1000

                # Put data in cache for an hour
                redis_server.set(key, cPickle.dumps(data))
                redis_server.expire(key, 36)

            call_time += call_time

        print(call_time)
        # check if data is in Cache
        if (redis_server.get(key)):
            data = cPickle.loads(redis_server.get(key))
            # print(data)
            return render_template("query_five.html", datainfo=data, qDoneBy="Redis", calltime=call_time)
        else:
            # Execute the Query
            cur.execute(query)
            data = cur.fetchall()

            # Put data in cache for an hour
            redis_server.set(key, cPickle.dumps(data))
            redis_server.expire(key, 36)

            # Set data in redis and load Data
            redis_data = cPickle.loads(redis_server.get(key))
            # print(redis_data)

            return render_template("query_five.html", datainfo=redis_data, qDoneBy="MySQL", calltime=call_time)



if __name__ == '__main__':
    application.run(debug=True)
