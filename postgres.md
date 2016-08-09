# postgreSQL Summary

## Connecting to postgreSQL from Python

import pg
db = pg.DB(dbname="name_of_database")

## SQL Statements

my_sql_statement = "select ..."
my_sql_query = db.query(my_sql_query)

### shows results like in the terminal
print my_sql_query    

### shows results...       
print my_sql_query.namedresult()  

### shows a dictionary; i.e., [Row(user_id=1, handle='tsanders', fname='Tim', ...)]
print my_sql_query.dictresult()   

### shows the col_name field for row n
print my_sql_query.dictresult()[n]['col_name']

## Passing Data from postgreSQL to xxxxx.html
return render_template('xxxxx.html', title='Some Title', sql_data=my_sql_query.namedresult())

## Processing postgreSQL Data in HTML
{% for one_row in sql_data %}
     ...
     ...{sql_data.field_name}
     ...
{$ endfor %}
