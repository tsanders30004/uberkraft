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

    # return render_template('xlat.html', title='Translate Test', xlat_rows=dict(qry1.namedresult()))
    # this was the original
    return render_template('main.html', title='Uberkraft', xlat=session['xlat'])

# @app.route('/xlat')
# def xlat():
#     try:
#         if len(session['lang']) == 0:
#             print "language not defined...  assume english"
#             lang = "en"
#         elif session['lang'] == "de":
#             lang = "de"
#         else:
#             lang = "en"
#     except Exception, e:
#         print "error with language assignment.  assuming english"
#         lang = "en"
#
#     print "langauge = " + lang
#
#     sql1= "select key, " + lang + " from xlat"
#     print sql1
#     qry1 = db.query(sql1)
#     print(dict(qry1.namedresult()))
#     session['xlat'] = dict(qry1.namedresult())
#
#     return render_template('xlat.html', title='Translate Test', xlat_rows=dict(qry1.namedresult()))

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
    return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))

@app.route('/profile')
def profile():

    # is user logged in?
    if len(session['userid']) == 0:
        # user is not logged in; reroute.
        return render_template('login.html', title='Login')

    # user is logged in; general SQL data to display the profile.
    sql1 = "select user_id, handle, fname, lname, num_chirps, num_following, num_being_followed from v_chirp_follow_summary where handle='" + session['userid'] + "'"
    query1 = db.query(sql1)

    sql2 = "select chirper_id, fname, lname, handle, to_char(chirp_date, 'MM/DD/YYYY: ') as chirp_date2, chirp from chirps join users on chirper_id = users.id where handle='" + session['userid'] + "' order by chirp_date desc;"
    query2 = db.query(sql2)
    return render_template('profile.html', title='Profile', profile_rows=query1.namedresult(), chirp_rows=query2.namedresult())

@app.route('/timeline')
def timeline():
    # is user logged in?
    if len(session['userid']) == 0:
        # user is not logged in; reroute.
        return render_template('login.html', title='Login')

    # user is logged in; general SQL data to display the profile.
    query1 = db.query("select chirper_id, chirp_date, to_char(chirp_date, 'MM/DD/YYYY: ') as chirp_date2, chirp, fname, lname, handle from chirps left join users on chirper_id = users.id where chirper_id in (select leader_id from follows where follower_id = 4) or chirper_id = 4 order by chirp_date desc;")

    return render_template('timeline.html', title='Timeline', profile_rows=query1.namedresult(), timeline_rows=query1.namedresult())

@app.route('/login')
def login():
    return render_template('login.html', title='Login', xlat=session['xlat'])

@app.route('/logout')
def logout():
    session['userid'] = ""
    return render_template('login.html', title='Login')

@app.route('/signup')
def signup():
    return render_template('signup.html', title='Sign Up', xlat=session['xlat'])

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
                # password was correct.  re-route to profile page
                session['userid'] = userid
                return redirect('/')
            else:
                # password was not correct.  re-route to login page.
                return render_template('badlogin.html', title='Incorrect Login', xlat=session['xlat'])

@app.route('/rma')
def rma():
    return render_template('rma.html', title='RMA', xlat=session['xlat'])

@app.route('/process_rma', methods=['POST'])
def process_rma():
    try:
        customer = request.form['customer']
        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        email = request.form['email']
        sn = request.form['sn']
        prob = request.form['prob']

        print customer
        print fname
        print lname
        print phone
        print email
        print sn
        print prob

        # find the customer id whose customer name was selected
        sql1 = "select id from customers where cname = $1"
        qry1 = db.query(sql1, customer)

        # convert the postgreSQL format of the customer ID [Row(id=1)] to a simple integer via dictresult()...
        cust_id = qry1.dictresult()[0]['id']

        sql2 = "insert into rma(fname, lname, email, prob, sn, cust_id, phone) VALUES(" + quoted(fname) + comma + quoted(lname) + comma + quoted(email) + comma + quoted(prob) + comma + str(sn) + comma + str(cust_id) + comma + quoted(phone) + ")"
        qry2 = db.query(sql2)

        return render_template('rma.html', title='RMA', xlat=session['xlat'])




        # if len(qry1.namedresult()) == 1:
        #     # username is already taken.  redirect user to an error page
        #     return render_template('tryagain.html', title='Create User', xlat=session['xlat'])
        # else:
        #     # need to create the new user and direct the user to login.  encrypt the password
        #     print password
        #     binary_pw = password.encode('utf-8')
        #     print binary_pw
        #     hashed = bcrypt.hashpw(binary_pw, bcrypt.gensalt())
        #     sql2 = "insert into users (userid, fname, lname, email, pw) values (" + quoted(userid) + comma + quoted(fname) + comma + quoted(lname) + comma + quoted(email) + comma + quoted(hashed) + ");"
        #     qry2 = db.query(sql2)
        #     return redirect('/login')

    except Exception, e:
        print "unable to create new rma in /rma"
        print traceback.format_exc()
        return "Error %s" % traceback.format_exc()
        return redirect('/login')

@app.route('/search', methods=['POST'])
def search():
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


@app.route('/add_follow', methods=['POST'])
def add_follow():

    user_to_follow = request.form['user_to_follow']
    logged_in_user = session['userid']

    sql = "insert into follows (follower_id, leader_id) values ((select id from users where users.handle = " + quoted(logged_in_user)+ "), (select id from users where users.handle = " + quoted(user_to_follow)+ "));"

    try:
        db.query(sql)
        print "follow table was updated"
        return redirect('/profile')
    except Exception, e:
        print "unique constraint violated; follow table not updated"
        return redirect('/profile')

app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

app.debug = True

if __name__ == '__main__':
     app.run(debug=True)
