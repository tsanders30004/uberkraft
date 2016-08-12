import traceback

import pg
db=pg.DB(dbname='uberkraft')

import bcrypt

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask('MyApp')

def quoted(s):
    return "'" + s + "'"

def quoted_percent(s):
    return "'%" + s + "%'"

def like_percent(s):
    return "%" + s + "%"

comma = ","

@app.route('/')
def home():
    try:
        if len(session['lang']) == 0:
            print "language not defined...  assume english"
            lang = "en"
        elif session['lang'] == "de":
            lang = "de"
        else:
            lang = "en"
    except Exception, e:
        print "error with language assignment.  assuming english"
        lang = "en"

    print "langauge = " + lang

    sql1= "select key, " + lang + " from xlat"
    print sql1
    qry1 = db.query(sql1)
    print(dict(qry1.namedresult()))
    session['xlat'] = dict(qry1.namedresult())

    return render_template('main.html', title='Uberkraft', xlat=session['xlat'])

@app.route('/en', methods=['POST'])
def en():
    session['lang'] = "en"
    lang = "en"
    print (lang)
    sql1= "select key, " + lang + " from xlat"
    print sql1
    qry1 = db.query(sql1)
    print(dict(qry1.namedresult()))
    session['xlat'] = dict(qry1.namedresult())

    try:
        if session['last_page']['page']:
            return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=dict(qry1.namedresult()))
        else:
            return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
    except Exception, e:
        return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))

@app.route('/de', methods=['POST'])
def de():
    session['lang'] = "de"
    lang = "de"
    print (lang)
    sql1= "select key, " + lang + " from xlat"
    print sql1
    qry1 = db.query(sql1)
    print(dict(qry1.namedresult()))
    session['xlat'] = dict(qry1.namedresult())
    try:
        if session['last_page']['page']:
            return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=dict(qry1.namedresult()))
        else:
            return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
    except Exception, e:
        return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))

@app.route('/login')
def login():
    session['last_page'] = {"page" : "login.html", "title" : "Login"}
    return render_template('login.html', title='Login', xlat=session['xlat'])

@app.route('/login0')
def login0():
    session['last_page'] = {"page" : "login.html", "title" : "Login"}
    return render_template('login.html', title='Login', xlat=session['xlat'])

@app.route('/logout')
def logout():
    session['last_page'] = {"page" : "logout.html", "title" : "Logout"}
    session['userid'] = ""
    return render_template('login.html', title='Login')

@app.route('/signup')
def signup():
    # record signup.html as the last page visited
    session['last_page'] = {"page" : "signup.html", "title" : "Sign Up"}
    # temp = session['last_page']
    print session['last_page']['title']

    # return render_template('signup.html', title='Sign Up', xlat=session['xlat'])
    return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=session['xlat'])

@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        userid      = request.form['userid']
        password    = request.form['password']
        fname       = request.form['fname']
        lname       = request.form['lname']
        email       = request.form['email']

        # check to see if user id already exists
        sql1 = "select userid from users where userid = $1"
        print sql1
        qry1 = db.query(sql1, userid)

        if len(qry1.namedresult()) == 1:
            # username is already taken.  redirect user to an error page
            return render_template('tryagain.html', title='Create User', xlat=session['xlat'])
        else:
            # need to create the new user and direct the user to login.  encrypt the password
            print password
            binary_pw = password.encode('utf-8')
            print binary_pw
            hashed = bcrypt.hashpw(binary_pw, bcrypt.gensalt())
            sql2 = "insert into users (userid, fname, lname, email, pw) values (" + quoted(userid) + comma + quoted(fname) + comma + quoted(lname) + comma + quoted(email) + comma + quoted(hashed) + ");"
            qry2 = db.query(sql2)
            return redirect('/login')

    except Exception, e:
        print "unable to create new user in /create_user"
        print traceback.format_exc()
        return "Error %s" % traceback.format_exc()
        return redirect('/login')

@app.route('/check_pw', methods=['POST'])
def check_password():
    userid = request.form['userid']
    password = request.form['password']

    sql1 = "select * from users where userid = $1"
    qry1 = db.query(sql1, userid)

    if len(qry1.namedresult()) == 0:
        # user does not exist; re-route to signup page.
        return redirect('/signup')
    else:
        # user exists; continue checking password
        for user in qry1.namedresult():
            if bcrypt.hashpw(password.encode('utf-8'), user.pw) == user.pw:
                # password was correct.  create a session variable with the userid of the current user to signify that the user has logged in.
                session['userid'] = userid
                return redirect('/')
            else:
                # password was not correct.  re-route to login page.
                return render_template('badlogin.html', title='Incorrect Login', xlat=session['xlat'])

@app.route('/check_pw0', methods=['POST'])
def check_password0():
    userid = request.form['userid']
    password = request.form['password']

    sql1 = "select * from users where userid = $1"
    qry1 = db.query(sql1, userid)

    if len(qry1.namedresult()) == 0:
        # user does not exist; re-route to signup page.
        return redirect('/signup')
    else:
        # user exists; continue checking password
        for user in qry1.namedresult():
            if bcrypt.hashpw(password.encode('utf-8'), user.pw) == user.pw:
                # password was correct.  create a session variable with the userid of the current user to signify that the user has logged in.
                session['userid'] = userid
                return redirect('/')
            else:
                # password was not correct.  re-route to login page.
                return render_template('badlogin.html', title='Incorrect Login', xlat=session['xlat'])

@app.route('/rma')
def rma():
    session['last_page'] = {"page" : "rma.html", "title" : "RMA"}

    sql1="select cname from customers order by cname"
    qry1 = db.query(sql1)

    return render_template('rma.html', title='RMA', xlat=session['xlat'], clist=qry1.dictresult())

@app.route('/process_rma', methods=['POST'])
def process_rma():
    try:
        customer = request.form['customer']
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        email = request.form['email']

        prob = request.form['prob']
        notes = request.form['notes']

        # find the customer id whose customer name was selected
        sql1 = "select id from customers where cname = $1"
        qry1 = db.query(sql1, customer)

        # convert the postgreSQL format of the customer ID [Row(id=1)] to a simple integer via dictresult()...
        cust_id = qry1.dictresult()[0]['id']

        sql2 = "insert into rma(fname, lname, email, prob, cust_id, phone, notes) VALUES(" + quoted(fname) + comma + quoted(lname) + comma + quoted(email) + comma + quoted(prob) + comma + str(cust_id) + comma + quoted(phone) + comma + quoted(notes) + ")"
        qry2 = db.query(sql2)

        return render_template('rma.html', title='RMA', xlat=session['xlat'])

    except Exception, e:
        print "unable to create new rma in /rma"
        print traceback.format_exc()
        return "Error %s" % traceback.format_exc()
        return redirect('/login')


@app.route('/process_fa', methods=['POST'])
def process_fa():
    try:
        rma_num = request.form['rma_num_select'][:6]
        serial_num = request.form['serial_num']
        rcvd_date = request.form['received']
        ship_date = request.form['shipped']
        suspect_part_num = request.form['suspect_part_num']
        notes = request.form['notes']
        root_cause2 = request.form['root_cause2']
        qry2 = db.query("select id from xlat where en = $1", root_cause2)
        root_id = qry2.dictresult()[0]['id']
        print root_id
        db.query('INSERT INTO fa(rma_no, ship_date, root_id, suspect_pn, rcvd_date, sn, notes) VALUES($1, $2, $3, $4, $5, $6, $7)', rma_num, ship_date, root_id, suspect_part_num, rcvd_date, serial_num, notes)

        # convert the postgreSQL format of the customer ID [Row(id=1)] to a simple integer via dictresult()...
        # cust_id = qry1.dictresult()[0]['id']

        return render_template('fa_closed.html', title='Failure Analysis Closed', xlat=session['xlat'])

    except Exception, e:
        print "unable to create new failure analysis in /fa"
        print traceback.format_exc()
        return "Error %s" % traceback.format_exc()
        return redirect('/')

@app.route('/analysis')
def analysis():
    session['last_page'] = {"page" : "analysis.html", "title" : "Failure Analysis"}

    sql1="select rma_info from v_rma_dropdown"
    qry1 = db.query(sql1)
    print qry1.namedresult()

    return render_template('analysis.html', title='RMA', xlat=session['xlat'], rma_info=qry1.dictresult())

@app.route('/search', methods=['POST'])
def search():
    session['last_page'] = {"page" : "search.html", "title" : "Search"}
    search_list = request.form['search_str'].split()

    userid = session['userid']

    if len(userid) == 0:
        return redirect('/login')

    # create temp table to facilate search results display.  name the temp table the same as the (unique) userid so that temp tables can be created in parallel for simultaneous users
    try:
        sql1 = "DROP TABLE " + userid
        db.query(sql1)
    except Exception, e:
        print "something went wrong trying to drop a temp table"
        print traceback.format_exc()

    try:
        sql2 = 'CREATE TABLE "public"."' + userid + '" ("handle" varchar, "name" varchar, "chirp" varchar)'
        db.query(sql2)
    except Exception, e:
        print "something went wrong trying to create a temp table"
        print traceback.format_exc()

    for n in range(len(search_list)):
        print n

        sql1 = "insert into " + userid + " select handle, fname || ' ' || lname as name, chirp from users left join chirps on users.id = chirps.chirper_id where lower(fname) like $1 or lower(lname) like $1 or lower(handle) like $1 or lower(chirp) like $1"
        search_results = db.query(sql1, like_percent(search_list[n].lower()))

        sql2 = "select distinct * from " + userid + ";"
        search_results = db.query(sql2)

    try:
        sql1 = "DROP TABLE " + userid
        db.query(sql1)
    except Exception, e:
        print "something went wrong trying to drop a temp table"
        print traceback.format_exc()

    # print search_results
    return render_template('search_results.html', title='Show Search Results', search_results = search_results.namedresult())


@app.route('/graph')
def graph():
    session['last_page'] = {"page" : "graph.html", "title" : "Graph"}
    return render_template('graph.html', title='Graph', xlat=session['xlat'])


@app.route('/db_total_by_rootid', methods=['POST'])
def db_total_by_rootid():
    sql1="select en, count(root_id) as total from xlat join fa on xlat.id = fa.root_id group by en order by total desc, en"
    qry1=db.query(sql1)
    print qry1.dictresult()
    print qry1.namedresult()

    # return render_template('search_results.html', title='Show Search Results', search_results = search_results.namedresult())
    return render_template('bar_stacked.html', title='Stacked Bar', search_results = qry1.namedresult(), xlat=session['xlat'])
    # return render_template('fa_closed.html', title='Failure Analysis Closed', xlat=session['xlat'])

app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

app.debug = True

if __name__ == '__main__':
     app.run(debug=True)
