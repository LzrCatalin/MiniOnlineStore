import io
import base64
from PIL import Image

from flask import Flask, request, render_template, session

#
#	Add the path to the project so that the imports work
#
import sys
sys.path.append("/home/catalin/workspace/project_individual/src")

#
#	Import the database classes
#
from Usersdb import UserDatabase
from Announcementsdb import AnnouncementDataBase

#
#	Establish connection to the databases
#
UserDatabase_path = "/home/catalin/workspace/project_individual/src/data_bases/users_database.db"
user_db = UserDatabase(UserDatabase_path)

AnnouncementsDatabase_path = "/home/catalin/workspace/project_individual/src/data_bases/announcements_database.db"
announcement_db = AnnouncementDataBase(AnnouncementsDatabase_path)

#
#	MAIN 
#
if __name__ == '__main__':

	user_db.insertUserIntoUsersTable("carmen", "carmen@gmail.com", "1234", "/home/catalin/workspace/project_individual/src/users_photos/images.png")
	
	announcement_db.insertAnnouncementIntoAnnouncementsTable(2, "Automobile", "BMW", "Laptop in perfect condition", 1000, 
														  "/home/catalin/workspace/project_individual/src/users_photos/images.png",
														  "/home/catalin/workspace/project_individual/src/users_photos/images.png",
														  "/home/catalin/workspace/project_individual/src/users_photos/images.png",
														  "/home/catalin/workspace/project_individual/src/users_photos/images.png")
	

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

#
#	Home page
#
@app.route('/')
def home():

	print(session)

	if 'logged_in' in session:
		print ("Intra pe loggedin")
		username = session['username']
		print(username)
		return render_template('index.html', username = username)
	
	else:
		return render_template('login.html')

#
#	Login page
#
@app.route('/login', methods=['GET', 'POST'])
def login():
	error_message = None

	if request.method == 'POST':
		print("POST method called")
		username = request.form['username']
		password = request.form['password']

		if user_db.checkUserInDatabaseForLogin(username, password):
			session['logged_in'] = True
			session['username'] = username
			
			users = user_db.retrieveUserFromUsersTable(username, password)
			return render_template('index.html', users=users)
		else:
			error_message = "Username not found or incorrect password"
	
	print("GET method called")
	return render_template('login.html', error_message = error_message)

#
#	Register page
#
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		password = request.form['password']

		# Handle file upload
		profile_photo = None
		if 'profilePhoto' in request.files:
			file = request.files['profilePhoto']
			if file.filename != '':
				profile_photo = user_db.save_profile_photo(file)

		# Insert user into the database
		if profile_photo is not None:
			if user_db.checkUserInDatabaseForSignUp(username, email) == True:
				return render_template('register.html', error_message="User with the same name or email already exists in the database.")
			else:
				user_db.insertUserIntoUsersTable(username, email, password, profile_photo)
				return render_template('login.html')
		else:
			# Handle the case when no profile photo is uploaded
			return render_template('register.html', error_message="Please upload a profile photo.")
	else:
		print("Back to register")
		return render_template('register.html')

#
#	My profile page
#
@app.route('/myprofile')
def myprofile():
	if 'logged_in' in session:
		username = session['username']
		user_data = user_db.retrieveUserFromUsersTableByName(username)

		if user_data and len(user_data) > 0:
			user_info = user_data[0]
			user = {
				'name': user_info[1],
				'email': user_info[2],
				'photo': user_info[4]
			}
			
			#
			#	Convert the image to base64 for displaying it in the HTML
			#
			if user['photo']:
				image = Image.open(io.BytesIO(user['photo']))
				# Convert to RGB mode if the image mode is 'P' (palette mode)
				if image.mode != 'RGB':
					image = image.convert('RGB')

				buffered = io.BytesIO()
				image.save(buffered, format="JPEG") 
				img_str = base64.b64encode(buffered.getvalue()).decode()

				return render_template('myprofile.html', user=user, img_str=img_str)
			else:
				return render_template('myprofile.html', user=user, img_str=None)
		else:
			return render_template('error.html', message="User data not found. Please log in again.")
	else:
		return render_template('login.html')

#
#	Add announcement page
#
@app.route('/add_announcement', methods=['GET', 'POST'])
def add_announcement():
	# User logged_in 
	if 'logged_in' in session:
		username = session['username']

		if request.method == 'POST':
			id_user = user_db.retrieveUserId(username)
			category = request.form['category']
			name = request.form['name']
			description = request.form['description']
			price = request.form['price']

			# Main photo
			main_photo = None
			if 'main_photo' in request.files:
				file = request.files['main_photo']
				if file.filename != '':
					main_photo = announcement_db.save_main_photo(file)
			
			# Secondary photos
			secondary_photo_1 = None
			secondary_photo_2 = None
			secondary_photo_3 = None
			if 'secondary_photo_1' in request.files and 'secondary_photo_2' in request.files and 'secondary_photo_3' in request.files:
				file1 = request.files['secondary_photo_1']
				file2 = request.files['secondary_photo_2']
				file3 = request.files['secondary_photo_3']
				if file1.filename != '' and file2.filename != '' and file3.filename != '':
					secondary_photo_1 = announcement_db.save_secondary_photo1(file1)
					secondary_photo_2 = announcement_db.save_secondary_photo2(file2)
					secondary_photo_3 = announcement_db.save_secondary_photo3(file3)
			
			# Insert announcement into database
			if main_photo is not None:
				if announcement_db.checkAnnouncementForAddIntoDataBase(category, name) == True:
					return render_template('add_announcement.html', error_message="Announcement with the same category and name already exists in the database.")
				else:
					announcement_db.insertAnnouncementIntoAnnouncementsTable(id_user, category, name, description, price, main_photo, secondary_photo_1, secondary_photo_2, secondary_photo_3)
					return render_template('index.html')
			else:
				# Handle the case when no profile photo is uploaded
				return render_template('add_announcement.html', error_message="Please upload photos for announcement.")
		else:
			return render_template('add_announcement.html')

#		
# 	Main
# 	
if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')

#
#	TO RESOLVE:
#		SECONDARY PHOTOS FAILED TO CONVERT INTO BINARY FOR ADDIND INSIDE DATABASE (DONE)
#

