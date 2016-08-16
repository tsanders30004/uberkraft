import traceback

import pg
db=pg.DB(dbname='uberkraft')

import bcrypt

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask, render_template, request, redirect, session, jsonify

app = Flask('MyApp')

# configure email settings
# see http://bit.ly/py-email and "Introducing Python (Bill Lubanovic, page 297) for details.
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders



import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# fromaddr = "tsanders30004@gmail.com"
# from_pw = "Langlitz2015!"
# toaddr = "tim.sanders@web-caffeine.com"

fromaddr = os.environ.get('FROM_EMAIL_ADDR')
from_pw = os.environ.get('FROM_EMAIL_PW')
toaddr = os.environ.get('TO_EMAIL_ADDR')




def quoted(s):
    return "'" + s + "'"

def quoted_percent(s):
    return "'%" + s + "%'"

def like_percent(s):
    return "%" + s + "%"

comma = ","

def login_status():
    if session.get('userid'):
        if len(session['userid']) == 0:
            return False
        else:
            return True
    else:
        return False

def show_debug_info(pg):
    print '********************************************************************************'
    print 'from page ' + pg + ':'

    print 'login status:'
    print login_status()

    try:
        print '   userid      = ' + session['userid']
    except Exception, e:
        print '   userid      = UNDEFINED'

    try:
        print '   lang =      ' + session['lang']
    except Exception, e:
        print '   lang        = UNDEFINED'

    try:
        print '   last_page   = ' + session['last_page']
    except Exception, e:
        print '   last_page   = UNDEFINED'

    try:
        print '   login_route = ' + session['login_route']
    except Exception, e:
        print '   login_route = UNDEFINED'

    print '********************************************************************************'

def set_login_route_status(s):
    session['login_route'] = s
    print 'login_route = ' + s

@app.route('/')
def home():
    show_debug_info('/main')
    session['last_page'] = {"page" : "main.html", "title" : "Home"}

    try:
        if len(session['lang']) == 0:
            session['lang'] = "en"
            lang = "en"
        elif session['lang'] == "de":
            session['lang'] = "de"
            lang = "de"
        else:
            session['lang'] = "en"
            lang = "en"
    except Exception, e:
        lang = "en"

    sql1= "select key, " + lang + " from xlat"
    # print sql1
    qry1 = db.query(sql1)
    # print(dict(qry1.namedresult()))
    session['xlat'] = dict(qry1.namedresult())

    return render_template('main.html', title='Uberkraft', xlat=session['xlat'])

@app.route('/en', methods=['POST'])
def en():
    show_debug_info('/en')
    session['lang'] = "en"
    lang = "en"
    # print (lang)
    sql1= "select key, " + lang + " from xlat"
    # print sql1
    qry1 = db.query(sql1)
    # print(dict(qry1.namedresult()))
    session['xlat'] = dict(qry1.namedresult())

    # try:
    #     if session['last_page']['page']:
    #         return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=dict(qry1.namedresult()))
    #     else:
    #         return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
    # except Exception, e:
    #     return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))

    if session.get('last_page'):
        if session['last_page']['page'] == 'login.html':
            return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
        else:
            return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=dict(qry1.namedresult()))
    else:
        return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))

@app.route('/de', methods=['POST'])
def de():
    show_debug_info('/de')
    session['lang'] = "de"
    lang = "de"
    # print (lang)
    sql1= "select key, " + lang + " from xlat"
    # print sql1
    qry1 = db.query(sql1)
    # print(dict(qry1.namedresult()))
    session['xlat'] = dict(qry1.namedresult())


    # try:
    #     if session['last_page']['page']:
    #         return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=dict(qry1.namedresult()))
    #     else:
    #         return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
    # except Exception, e:
    #     return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))

    if session.get('last_page'):
        if session['last_page']['page'] == 'login.html':
            return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
        else:
            return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=dict(qry1.namedresult()))
    else:
        return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))




@app.route('/login')
def login():
    show_debug_info('/login')

    session['last_page'] = {"page" : "login.html", "title" : "Login"}

    # set_login_route_status('/login')

    session['userid'] = ''
    return render_template('login.html', title='Login', xlat=session['xlat'])

@app.route('/contact')
def contact():
    show_debug_info('/contact')
    session['last_page'] = {"page" : "contact.html", "title" : "Contact Me"}
    return render_template('contact.html', title='Contact Me', xlat=session['xlat'])

@app.route('/send_mail', methods=['POST'])

# email messages must be utf-8 encoded; otherwise, email with non-ACSII (i.e., letters with umlauts) will not be sent.
# for more information, see https://docs.python.org/2/howto/unicode.html
def send_mail():
    try:
        name = request.form['name'].encode('utf-8')
    except Exception, e:
        name = 'UNDEFINED'
    try:
        from_email = request.form['email'].encode('utf-8')
    except Exception, e:
        from_email = 'UNDEFINED'
    try:
        comments = request.form['comments'].encode('utf-8')
    except Exception, e:
        comments = 'UNDEFINED'


    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Ueberkraft:  Message from Ueberkraft Visitor"

    body = "Message from " + fromaddr + "\n" + comments
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, from_pw)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

    # create a text file with RMA data...
    # sql1 = "select cname as customer, rma.id as rma_number, fname as first_name, lname as last_name, email as email_address, prob as issue, ship_date is null as open from customers join rma on customers.id = rma.cust_id left join fa on rma.id = fa.rma_no where extract(year from now()) = extract(year from rma.ts) and extract(month from now()) = extract(month from rma.ts) and extract(day from now()) = extract(day from rma.ts) order by rma.ts"
    # file_text = str(db.query(sql1))
    # print len(file_text)
    # print file_text.count('\n', 0, len(file_text))
    #
    # print "*************"
    # fout = open ('text_files/test_file.txt', 'w')
    # fout.write(file_text)



    return render_template('email_sent.html', title='Thank You', xlat=session['xlat'])

@app.route('/logout')
def logout():
    show_debug_info('/logout')
    print 'logged out'
    session['userid'] = ''

    # set_login_route_status('/')

    session['last_page'] = {"page" : "login.html", "title" : "Login"}
    # return render_template('main.html', title='Uberkraft', xlat=dict(qry1.namedresult()))
    return redirect('/')

@app.route('/signup')
def signup():
    show_debug_info('/signup')
    session['last_page'] = {"page" : "signup.html", "title" : "Register"}

    return render_template(session['last_page']['page'], title=session['last_page']['title'], xlat=session['xlat'])

@app.route('/create_user', methods=['POST'])
def create_user():
    show_debug_info('/create_user')
    session['last_page'] = {"page" : "signup.html", "title" : "Sign Up"}

    try:
        userid      = request.form['userid']
        password    = request.form['password']
        fname       = request.form['fname']
        lname       = request.form['lname']
        email       = request.form['email']

        # check to see if user id already exists
        sql1 = "select userid from users where userid = $1"
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
    show_debug_info('/check_pw')
    session['last_page'] = {"page" : "login.html", "title" : "Login"}

    # check password

    userid = request.form['userid']
    password = request.form['password']

    sql1 = "select * from users where userid = $1"
    qry1 = db.query(sql1, userid)

    if len(qry1.namedresult()) == 0:
        # user does not exist; re-route to signup page.
        print "need to handle non-existent user with an error page"
        session['login_route'] = ''
        return redirect('/signup')
    else:
        # user exists; continue checking password
        for user in qry1.namedresult():
            if bcrypt.hashpw(password.encode('utf-8'), user.pw) == user.pw:
                # password was correct.  create a session variable with the userid of the current user to signify that the user has logged in.
                session['userid'] = userid
                print 'login was successul in /check_pw...'
                show_debug_info('/check_pw')
                # need to route user back where they came from
                # if session['login_route'] == '/login':
                #     session['login_route'] = ''
                #     return redirect('/')
                try:
                    if session['login_route'] == '/rma':
                        # session['login_route'] = ''
                        print 'password was correct; rendering rma.html'
                        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                        show_debug_info('pw correct for rma page')
                        sql1="select cname from customers order by cname"
                        qry1 = db.query(sql1)
                        print qry1.dictresult()
                        return render_template('rma.html', title='RMA', xlat=session['xlat'], clist=qry1.dictresult())
                        # return redirect('/rma')

                    elif session['login_route'] == '/analysis':
                        sql1="select rma_info from v_rma_dropdown"
                        qry1 = db.query(sql1)
                        print qry1.namedresult()
                        return render_template('analysis.html', title='RMA', xlat=session['xlat'], rma_info=qry1.dictresult())

                    elif session['login_route'] == '/g_rootcause':
                        return render_template('g_rootcause.html', title='Root Cause Statistics', xlat=session['xlat'])
                    elif session['login_route'] == '/g_partno':
                        return render_template('g_partno.html', title='Part Number Statistics', xlat=session['xlat'])
                except Exception, e:
                    return render_template('main.html', title='Uberkraft', xlat=session['xlat'])
            else:
                # password was not correct.  re-route to login page.
                return render_template('badlogin.html', title='Incorrect Login', xlat=session['xlat'])

@app.route('/rma')
def rma():
    show_debug_info('/rma')
    session['last_page'] = {"page" : "rma.html", "title" : "RMA"}

    set_login_route_status('/rma')
    show_debug_info('/rma')



    if login_status() != True:
        return redirect('/login')

    print "inside /rma *****"
    sql1="select cname from customers order by cname"
    qry1 = db.query(sql1)
    print qry1.dictresult()

    return render_template('rma.html', title='RMA', xlat=session['xlat'], clist=qry1.dictresult())

@app.route('/process_rma', methods=['POST'])
def process_rma():
    show_debug_info('/process_rma')
    session['last_page'] = {"page" : "rma.html", "title" : "RMA"}



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

        # create a text file with RMA data...
        # sql1 = "select cname as customer, rma.id as rma_number, fname as first_name, lname as last_name, email as email_address, prob as issue, ship_date is null as open from customers join rma on customers.id = rma.cust_id left join fa on rma.id = fa.rma_no where extract(year from now()) = extract(year from rma.ts) and extract(month from now()) = extract(month from rma.ts) and extract(day from now()) = extract(day from rma.ts) order by rma.ts"
        # file_text = str(db.query(sql1))
        # print len(file_text)
        # print file_text.count('\n', 0, len(file_text))
        #
        # print "*************"
        # fout = open ('text_files/test_file.txt', 'w')
        # fout.write(file_text)

        # ####################################################################################################
        # create a text file with RMA data...
        sql3 = "select cname as customer, rma.id as rma_number, rma.ts as date_created, fname as first_name, lname as last_name, email as email_address, prob as issue, ship_date is null as open from customers join rma on customers.id = rma.cust_id left join fa on rma.id = fa.rma_no where extract(year from now()) = extract(year from rma.ts) and extract(month from now()) = extract(month from rma.ts) and extract(day from now()) = extract(day from rma.ts) order by rma.ts"

        file_text = str(db.query(sql3))

        path = "text_files/"
        filename = "rma_data.txt"

        if file_text.count('\n', 0, len(file_text)) >= 5:

            fout = open (path + filename, 'w')
            fout.write(file_text)
            fout.close()

            msg = MIMEMultipart()

            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Ueberkraft:  Daily RMA Threshold Exceeded"

            body = "The number of RMA's received today has been exceeded.  Current list of RMA's is attached.\n"

            msg.attach(MIMEText(body, 'plain'))


            attachment = open(path + filename, "rb")

            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, from_pw)
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()

        # return render_template('rma.html', title='RMA', xlat=session['xlat'])
        return render_template('rma_closed.html', title='RMA Created', xlat=session['xlat'])
        # ####################################################################################################

    except Exception, e:
        print "unable to create new rma in /rma"
        print traceback.format_exc()
        return "Error %s" % traceback.format_exc()
        return redirect('/login')


@app.route('/process_fa', methods=['POST'])
def process_fa():
    show_debug_info('/process_fa')
    session['last_page'] = {"page" : "analysis.html", "title" : "Failure Analysis"}

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
    show_debug_info('/analysis')
    session['last_page'] = {"page" : "analysis.html", "title" : "Failure Analysis"}

    set_login_route_status('/analysis')

    if login_status() != True:
        return redirect('/login')

    sql1="select rma_info from v_rma_dropdown"
    qry1 = db.query(sql1)
    print qry1.namedresult()

    return render_template('analysis.html', title='RMA', xlat=session['xlat'], rma_info=qry1.dictresult())

@app.route('/search', methods=['POST'])
def search():
    show_debug_info('/search')
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


# @app.route('/trends')
# def graph():
#     show_debug_info('/graph')
#     session['last_page'] = {"page" : "trends.html", "title" : "Trends"}
#
#     if login_status() == 'logged_out':
#         return redirect('/login')
#
#     return render_template('trends.html', title='Graph', xlat=session['xlat'])

@app.route('/g_rootcause')
def g_rootcause():
    show_debug_info('/g_rootcause')
    session['last_page'] = {"page" : "g_rootcause.html", "title" : "Root Cause Statistics"}

    set_login_route_status('/g_rootcause')

    if login_status() == 'logged_out':
        return redirect('/login')

    return render_template('g_rootcause.html', title='Root Cause Statistics', xlat=session['xlat'])

@app.route('/g_partno')
def g_partno():
    show_debug_info('/g_partno')
    session['last_page'] = {"page" : "g_partno.html", "title" : "Part Number Statistics"}

    set_login_route_status('/g_partno')

    if login_status() == 'logged_out':
        return redirect('/login')

    return render_template('g_partno.html', title='Part Number Statistics', xlat=session['xlat'])


@app.route('/data_routecause', methods=['POST'])
def data_routecause():
    show_debug_info('/data_routecause')
    session['last_page'] = {"page" : "g_rootcause.html", "title" : "Root Cause"}

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

    if lang == "en":
        sql1="select en, count(root_id) as total from xlat join fa on xlat.id = fa.root_id group by en order by total desc, en"
    else:
        sql1="select de as en, count(root_id) as total from xlat join fa on xlat.id = fa.root_id group by de order by total desc, de"   # 'de as en' is needed to make the translation on the graph work.

    qry1=db.query(sql1)
    return jsonify(qry1.dictresult())

@app.route('/data_partno', methods=['POST'])
def data_partno():
    show_debug_info('/data_partno')
    session['last_page'] = {"page" : "g_partno.html", "title" : "Part Number"}

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

    if lang == "en":
        sql1="select en as desc, count(fa.suspect_pn) as total from xlat join xlat_pn on xlat.id = xlat_pn.xlat_id join fa on xlat_pn.pn = fa.suspect_pn group by en order by count(fa.suspect_pn) desc"

    else:
        sql1="select de as desc, count(fa.suspect_pn) as total from xlat join xlat_pn on xlat.id = xlat_pn.xlat_id join fa on xlat_pn.pn = fa.suspect_pn group by de order by count(fa.suspect_pn) desc"

    qry1=db.query(sql1)

    return jsonify(qry1.dictresult())

# @app.route('/db_total_by_rootid', methods=['POST'])
# def db_total_by_rootid():
#     show_debug_info('/db_total_by_rootid')
#     session['last_page'] = {"page" : "analysis.html", "title" : "Failure Analysis"}
#     sql1="select en, count(root_id) as total from xlat join fa on xlat.id = fa.root_id group by en order by total desc, en"
#     qry1=db.query(sql1)
#     print qry1.dictresult()
#     print qry1.namedresult()

    # return render_template('search_results.html', title='Show Search Results', search_results = search_results.namedresult())
    # return render_template('bar_stacked.html', title='Stacked Bar', search_results = qry1.namedresult(), xlat=session['xlat'])
    # return render_template('fa_closed.html', title='Failure Analysis Closed', xlat=session['xlat'])

app.secret_key = 'CSF686CCF85C6FRTCHQDBJDXHBHC1G478C86GCFTDCR'

app.debug = True

if __name__ == '__main__':
     app.run(debug=True)
