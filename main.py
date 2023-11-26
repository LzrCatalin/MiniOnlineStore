import io
import base64
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

#
#	Add the path to the project so that the imports work
#
import sys
sys.path.append("/home/catalin/workspace/git/MiniOnlineStore/src")

#
#	Import the database classes
#
from Usersdb import UserDatabase
from Announcementsdb import AnnouncementDataBase


###############################################################################
UserDatabase_path = "git/src/data_bases/users_database.db"
AnnouncementsDatabase_path = "src/data_bases/announcements_database.db"

user_db = None
announcement_db = None


###############################################################################
#
# Application config
#

app = Flask(__name__)
app.secret_key = 'my_secret_key'

#
# Login config
#
login_manager = LoginManager(app)
login_manager.login_view = 'login'


###############################################################################
#
# Logged in users
#
users = {}

class User(UserMixin):
	def __init__(self, user_id):
		self.id = user_id


###############################################################################

@login_manager.user_loader
def load_user(user_id):
	return users.get(user_id)


# Home
@app.route('/')
def index():
	global user_db
	global announcement_db

	# If user not authenticated, force authentication
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	# TODO: Debug
	print(f'Current user = {current_user.id}')
	return render_template('index.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	global user_db
	global announcement_db
	error_message = None

	if request.method == 'POST':
		print("POST method called")
		username = request.form['username']
		password = request.form['password']

		# Validate user in database
		if user_db.checkUserInDatabaseForLogin(username, password):
			# If does not exist in logged users, create a new user and
			# add it to the logged users list
			new_logged_user = User(username)
			users[username] = new_logged_user

			# Log user in
			login_user(users[username])

			# Move to home page
			return redirect(url_for('index'))
		else:
			error_message = "Username not found or incorrect password"

	return render_template('login.html', error_message = error_message)


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
	global user_db
	global announcement_db

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
				return redirect(url_for('login'))
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
	global user_db
	global announcement_db

	# TODO: Use current_user as in index (DONE)
	if current_user.is_authenticated:
		username = current_user.id
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
	global user_db
	global announcement_db

	# TODO: Use current_user as in index
	if current_user.is_authenticated:
		username = current_user.id

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


###############################################################################

def db_init():
	global user_db
	global announcement_db

	# users data base
	user_db = UserDatabase(UserDatabase_path)
	if user_db is None:
		exit(1)

	# announcement data base
	announcement_db = AnnouncementDataBase(AnnouncementsDatabase_path)
	if announcement_db is None:
		exit(1)

def demo_db_add():
	user_db.insertUserIntoUsersTable("catalin", "catalin@gmail.com", "1234", "src/users_photos/images.png")
	user_db.insertUserIntoUsersTable("razvan", "razvan@gmail.com", "1234", "src/users_photos/images.png")
	announcement_db.insertAnnouncementIntoAnnouncementsTable(2, "Automobile", "BMW", "Laptop in perfect condition", 1000,
														  "src/users_photos/images.png",
														  "src/users_photos/images.png",
														  "src/users_photos/images.png",
														  "src/users_photos/images.png")

if __name__ == '__main__':
	# Initialize data bases
	db_init()

	# TODO: Demo to add entries in databases
	demo_db_add()

	# Start application
	app.run(debug=True, host='0.0.0.0')
