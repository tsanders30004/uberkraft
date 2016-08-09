# Chirp Application

## Application Overview
"Chirp" is a Twitter-like social-media application.

### Major Features
* Users must be logged in to add content.
* User data and content is stored in a postgreSQL database.
* User passwords are encrypted before being written to the database.
* Many pages require that the user be logged in before accessing; logic is included to manage this.
* New users can create an account.  Logic is in place to ensure that user ID's are unique - which is also enforced in the database.
* The profile page shows the number of "chirps" a user has issued; and the number of followees and followers.
* Protections are used to prevent SQL injection attacks.
* A search feature is available which will return a list of search results, including user profile data and content.
* The search page includes a feature in which the logged in user to follow a user included in the list of each results.

## Technologies Used
* HTML5
* CSS3
* postgreSQL
* Python
* bcrypt (used for password encryption)
* Flask
* Sessions


## What I Learned
* postgreSQL:  I have used MySQL before, but never postgreSQL.  There are many similarities; however there are minor differences for things such as date formatting and managing tables, views, etc.  (Example:  The commands in MySQL for displaying the list of databases, showing a table structure, etc., are completely different than this in postgreSQL).
* Python:  Previously, I have only used PHP to accessing backend databases.
* GET and POST methods
* The importance of a clearly defined and comprehensive route map.  
* The importance of a properly normalized SQL database.

## Link to GutHub (https://github.com/tsanders30004/chirpApplication)
