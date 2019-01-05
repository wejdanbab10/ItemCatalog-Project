#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, jsonify, \
    url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, BloodType, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Blood Bank App'

# Connect to Database and create database session

engine = create_engine('sqlite:///bloodTypes.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code

    code = request.data

    try:

        # Upgrade the authorization code into a credentials object

        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = \
            make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.

    access_token = credentials.access_token
    url = \
        'https://www.googleapis.com/oauth2/v2/tokeninfo?access_token=%s' \
        % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = \
            make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.

    if result['issued_to'] != CLIENT_ID:
        response = \
            make_response(json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = \
            make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info

    userinfo_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    user_id = getUserID(login_session['email'])
    if not user_id:
    	user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += \
        ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash('you are now logged in as %s' % login_session['username'])
    print 'done!'
    return output




# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


    # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = \
            make_response(json.dumps('Current user not connected.'),
                          401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return redirect(url_for('BloodBank'))
    else:
        response = \
            make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response










# JSON APIs to view Blood Bank Information

@app.route('/bloodbank/JSON')
def BloodBankJSON():
    blood_types = session.query(BloodType).all()
    return jsonify(BloodType=[i.serialize for i in blood_types])


@app.route('/bloodbank/<int:bloodtype_id>/JSON')
@app.route('/bloodbank/<int:bloodtype_id>/info/JSON')
def showBloodTypeJSON(bloodtype_id):
    blood_types = \
        session.query(BloodType).filter_by(id=bloodtype_id).one()
    items = \
        session.query(Items).filter_by(bloodType_id=bloodtype_id).all()
    return jsonify(blood_types=blood_types.serialize)



"""
    BloodBank: Is a method that allows loggedin and loggedout users to check the avilable
    blood types in the blood bank
    Args:
        no args
    Returns:
        return puplicbloodbank.html templet (If not loggedin) or bloodbank.html temple 
        (If loggedin) which shows list of the blood types in the system of the blood bank
    """
@app.route('/')
@app.route('/bloodbank')
def BloodBank():

    blood_types = session.query(BloodType).all()
    if 'username' not in login_session:
        return render_template('puplicbloodbank.html',
                               blood_types=blood_types)
    else:
        return render_template('bloodbank.html',
                               blood_types=blood_types)


"""
    showBloodType: Is a method that shows detailed information about a specific blood type
    Args:
        bloodtype_id (data type: int): Takes the blood type id as an argument to retrive
        information about this blood type only.
    Returns:
        return puplicinfo.html templet (If not loggedin) or info.html temple (If loggedin)
        which will show the detailed info about this blood type
    """

@app.route('/bloodbank/<int:bloodtype_id>')
@app.route('/bloodbank/<int:bloodtype_id>/info')
def showBloodType(bloodtype_id):
    blood_types = \
        session.query(BloodType).filter_by(id=bloodtype_id).one()
    creator = getUserInfo(blood_types.user_id)
    items = \
        session.query(Items).filter_by(bloodType_id=bloodtype_id).all()

    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('puplicinfo.html', items=items,
                               blood_types=blood_types,
                               bloodtype_id=bloodtype_id, creator=creator)
    else:
        return render_template('info.html', items=items,
                               blood_types=blood_types,
                               bloodtype_id=bloodtype_id, creator=creator)


"""
    editBloodType: Is a method that allows loggedin  users to edit info about a specific 
    blood type
    Args:
        bloodtype_id (data type: int): Takes the blood type id as an argument to retrive
        information to edit about this blood type only.
    Returns:
        return editBloodType.html temple which will show a form that allows editing the 
        status of this blood type
    """
@app.route('/bloodbank/<int:bloodtype_id>/edit', methods=['GET', 'POST'])
def editBloodType(bloodtype_id):
    typeToEdit = session.query(BloodType).filter_by(id=bloodtype_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if typeToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this blood type.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        request.form['status']
        typeToEdit.status = request.form['status']
        session.add(typeToEdit)
        session.commit()
        flash('Blood Type %s Status Successfully Edited'
              % typeToEdit.name)
        return redirect(url_for('BloodBank'))
    else:

        return render_template('editBloodType.html',
                               typeToEdit=typeToEdit,
                               bloodtype_id=bloodtype_id)


"""
    editBloodTypeInfo: Is a method that allows loggedin  users to edit a specific 
    info about the blood type
    Args:
        info_id (data type: int): Takes the info id as an argument to retrive
        the amount of this blood type to edit it only.
    Returns:
        return editInfoItem.html temple which will show a form that allows editing the
        amount about this blood type
    """

@app.route('/bloodbank/<int:info_id>/editinfo', methods=['GET', 'POST'])
def editBloodTypeInfo(info_id):
    amountToEdit = session.query(Items).filter_by(id=info_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        request.form['amount']
        amountToEdit.amount = request.form['amount']
        session.add(amountToEdit)
        session.commit()
        flash('Blood Type %s Amount Successfully Edited '
              % amountToEdit.name)
        return redirect(url_for('BloodBank'))
    else:
        return render_template('editInfoItem.html',
                               amountToEdit=amountToEdit,
                               info_id=info_id)


"""
    deleteBloodType: Is a method that allows loggedin  users to delete a specific 
    blood type
    Args:
        info_id (data type: int): Takes the blood type id as an argument to specify which
        blood type to delete.
    Returns:
        return deleteBloodType.html temple which will show a form that allows deleting 
        this blood type
    """
@app.route('/bloodbank/<int:bloodtype_id>/delete', methods=['GET',
           'POST'])
def deleteBloodType(bloodtype_id):

    BloodTypeToDelete = session.query(BloodType).filter_by(id=bloodtype_id).one()
    ItemsToDelete = session.query(Items).filter_by(id=bloodtype_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if BloodTypeToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this blood type.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(BloodTypeToDelete)
        session.delete(ItemsToDelete)
        flash('%s Successfully Deleted' % ItemsToDelete.name)
        session.commit()
        return redirect(url_for('BloodBank'))
    else:
        return render_template('deleteBloodType.html',
                               BloodTypeToDelete=BloodTypeToDelete)

"""
    newBloodType: Is a method that allows loggedin  users to add new blood type
    Args:
        no args
    Returns:
        return newBloodType.html temple which will show a form that allows adding detailed 
        info about the blood type
    """
    
@app.route('/bloodbank/new', methods=['GET', 'POST'])
def newBloodType():
	if 'username' not in login_session:
		return redirect('/login')
    	if request.method == 'POST':
        	newBloodType = BloodType(name=request.form['name'],
                                 status=request.form['status'], user_id=login_session['user_id'])
        	newInfoBloodType = Items(name=request.form['name'],
                                 description=request.form['description'],
                                 amount=request.form['amount'], user_id=login_session['user_id'],
                                 blood_type=newBloodType)
        	session.add(newBloodType)
        	session.add(newInfoBloodType)
        	flash('New Blood Type %s Successfully Created'
              % newBloodType.name)
        	session.commit()

        	return redirect(url_for('BloodBank'))
    	else:
        	return render_template('newBloodType.html')
			

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
