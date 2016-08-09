import traceback

import pg
db=pg.DB(dbname='uberkraft')

import bcrypt

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
        print session['userid']
        return redirect('/profile')
    except Exception, e:
        print "not logged in"
        return redirect('/login')

@app.route('/xlat')
def xlat():
    sql1= "select key, en, de from xlat"
    qry1 = db.query(sql1)
    return render_template('xlat.html', title='Translate Test', xlat_rows=qry1.namedresult())

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
    return render_template('login.html', title='Login')

@app.route('/logout')
def logout():
    session['userid'] = ""
    return render_template('login.html', title='Login')

@app.route('/signup')
def signup():
    return render_template(
    'signup.html',
    title='Sign Up')

@app.route('/check_pw', methods=['POST'])
def check_password():
    userid = request.form['userid']
    password = request.form['password']

    sql = "select * from users where handle = $1"
    query = db.query(sql, userid)

    if len(query.namedresult()) == 0:
        # user does not exist; re-route to signup page.
        return redirect('/signup')
    else:
        # user exists; continue checking password
        for user in query.namedresult():
            if bcrypt.hashpw(password.encode('utf-8'), user.password) == user.password:
                # password was correct.  re-route to profile page
                session['userid'] = userid
                return redirect('/profile')
            else:
                # password was not correct.  re-route to login page.
                return render_template(
                'badlogin.html',
                title='Incorrect Login')

@app.route('/new_chirp', methods=['POST'])
def new_chirp():
    # add a new chirp
    new_chirp = request.form['new_chirp']

    sql1 = "select id from users where handle = " + quoted(session['userid']) + ";"
    userid = db.query(sql1).dictresult()[0]["id"]

    sql2 = "insert into chirps (chirper_id, chirp) values($1, $2)"
    db.query(sql2, str(userid), new_chirp)

    return redirect('/timeline')

@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        userid = request.form['userid']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']

        # check to see if user id already exists
        sql = "select handle from users where handle = $1"
        query = db.query(sql, userid)

        if len(query.namedresult()) == 1:
            # username is already taken.  redirect user to an error page
            return render_template('tryagain.html', title='Create User')
        else:
            # need to create the new user and direct the user to login.  encrypt the password
            binary_pw = password.encode('utf-8')
            hashed = bcrypt.hashpw(binary_pw, bcrypt.gensalt())
            sql = "insert into users (handle, fname, lname, password) values (" + quoted(userid) + comma + quoted(fname) + comma + quoted(lname) + comma + quoted(hashed) + ");"
            query = db.query(sql)

            #create a chirp at signin
            sql = "select id from users where handle = " + quoted(userid) + ";"
            print sql
            query = db.query(sql)
            new_userid = query.dictresult()[0]['id']

            sql = "insert into chirps (chirper_id, chirp) values (" + str(new_userid) + ", 'Welcome me to Chirp!')"
            db.query(sql)

            return redirect('/login')

    except Exception, e:
        print "something went wrong in /create_user route."
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
