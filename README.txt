Note:
	Normally for security purposes I would not leave the Oauth key in a public
	repo, but I have left it in for the sake of simplifying install since this
	app is for educational purposes and not meant to be used commercially.

	This application must be run with Python 3

Dependencies:

	Setup instructions:
		Python 3
        SQL Alchemy
        Flask
        fleep
        titlecase
        passlib.hash
        oauth2client.client
	sudo SetUp.sh
	
    Install all of the dependencies:
        Python 3
        SQL Alchemy
        Flask
        fleep
        titlecase
        passlib.hash
        oauth2client.client

    Run Setup.py to setup the database

    Optionally
        you can run Populate.py to add some fake profiles for viewing purposes the passwords
        The log-ins and passwords for each fake user is in plane text in the file

    Run Application.py to start the Flask server

    Access the web page at http:\\LocalHost:8000

Admin Mode
    For security purposes all users are restricted to editing their own items and profiles in the website.
    To edit the database as an admin with root like super powers:
        start the python3 interpreter and type in from Application import *
        This will load the database, but not the server you can then access the admin interface with out any restrictions
        for a list of available functions and there docstrings type Man()

API
    You must be logged in to use the API.
    Available commands are listed with their syntax on the API link found in your home page.