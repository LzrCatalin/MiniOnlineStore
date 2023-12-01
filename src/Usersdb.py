import sqlite3
import os
from io import BytesIO
from PIL import Image

class UserDatabase:
	#
	#	Constructor
	#
	def __init__(self, path):
		self.path = path
		#
		# Create table
		#
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, password TEXT, photo BLOB)")
				
				if not self.usersTableExists():
					print("Users table successfully created")

		except sqlite3.Error as error:
			print("Failed to create Users", error)
	
	##################################################
	#												##
	# Function to convert data to binary	 		##	
	#												##
	###################################################
	def convertToBinaryData(self, filename):
		with open(filename, 'rb') as file:
			blobData = file.read()
		return blobData

	##############################################################
	#															##
	# Functions who help us to find if insert duplicates		##
	# data into databases (users, announcement)		        	##
	#	 														##	
	##############################################################
	def user_exists_with_name(self, current, name):
		#Checl if an user with the given name already exists
		current.execute("SELECT * FROM users WHERE name = ?", (name,))
		existing_user = current.fetchone()
		return existing_user is not None
	 
	def user_exists_with_password(self, current, name, password):
		# Check if an user with the given name or email already exists
		current.execute("SELECT * FROM users WHERE name = ? OR password = ?", (name, password))
		existing_user = current.fetchone()
		return existing_user is not None
	
	def user_exists_with_email(self, current, name, email):
		# Check if an user with the given name or email already exists
		current.execute("SELECT * FROM users WHERE name = ? OR email = ?", (name, email))
		existing_user = current.fetchone()
		return existing_user is not None
	
	def usersTableExists(self):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT * FROM users")
				user = cursor.fetchone()
				print("Users table exists")
				return user is not None
		except sqlite3.Error as error:
			print("Failed to retrieve from Users table", error)

	def connect(self):
		return sqlite3.connect(self.path)
	   
	@staticmethod   
	def save_profile_photo(file):
		try:
			if not file or not hasattr(file, 'filename'):
				raise ValueError("Invalid file object")

			upload_folder = 'static/profile_photos'
			os.makedirs(upload_folder, exist_ok=True)

			filename = os.path.join(upload_folder, file.filename)
			file.save(filename)
			return filename

		except Exception as e:
			print("Failed to save profile photo:", str(e))
			return None
	
	#
	#	Function for inserting into table
	#
	def insertUserIntoUsersTable(self, name, email, password, photo):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				
				if not self.user_exists_with_email(cursor, name, email):
					user_photo = self.convertToBinaryData(photo)
					sqlite_insert_with_param = "INSERT INTO users (name, email, password, photo) VALUES (?, ?, ?, ?)"
					users_tuple = (name, email, password, user_photo)

					cursor.execute(sqlite_insert_with_param, users_tuple)
					connect.commit()	

					print("User inserted successfully into users_database")
				else:
					print("User with the same name or email already exists in the database.")

		except sqlite3.Error as error:
			print("Failed to insert into Users table", error)

	#
	#	Function for primary key of the user exists in the database
	#
	def user_exists_by_id(self, user_id):
			try:
				with self.connect() as connect:
					cursor = connect.cursor()
					cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
					existing_user = cursor.fetchone()
					return existing_user is not None
			
			except sqlite3.Error as error:
				print("Failed to retrieve from Users table", error)
				return False
	#
	#	Function for checking if user exists in the database for login
	#
	def checkUserInDatabaseForLogin(self, name, password):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()

				# Check if the user with the given name and password exists
				cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
				existing_user = cursor.fetchone()

				if existing_user:
					print("User exists in the users_database")
					return True
				else:
					print("User does not exist in the users_database")
					return False

		except sqlite3.Error as error:
			print("Failed to check user in the users_database", error)
			return False

	#
	#	Function for checking if user exists in the database for sign up
	#	
	def checkUserInDatabaseForSignUp(self, name, email):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()

				# Check if the user with the given name and password exists
				cursor.execute("SELECT * FROM users WHERE name = ? OR email = ?", (name, email))
				existing_user = cursor.fetchall()

				if existing_user:
					print("User exists in the users_database")
					return True
				else:
					print("User does not exist in the users_database")
					return False

		except sqlite3.Error as error:
			print("Failed to check user in the users_database", error)
			return False

	#
	#	Function for retrieving user from the database
	#
	def retrieveUserFromUsersTable(self, name, password):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				if self.user_exists_with_password(cursor, name, password):
					cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (name, password))
					users = cursor.fetchall()
					print("Users retrieved successfully from users_database")
					return users
				else:
					print("User with the same name and password does not exist in the database.")
		
		except sqlite3.Error as error:
			print("Failed to retrieve from Users table", error)
	
	#
	#	Function for retrieveing user using username
	#
	def retrieveUserFromUsersTableByName(self, name):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				if self.user_exists_with_name(cursor, name):
					cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
					users = cursor.fetchall()
					print("Users retrieved successfully from users_database")
					return users
				else:
					print("User with the same name does not exist in the database")
		
		except sqlite3.Error as error:
			print("Failed to retrieve from Users table", error)

	#
	#	Function for retrieving id of user
	#
	def retrieveUserId(self, name):
		try: 
			with self.connect() as connect:
				cursor = connect.cursor()
				if self.user_exists_with_name(cursor, name):
					cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
					user_id = cursor.fetchone()
					if user_id:
						return user_id[0]  # Extract the ID from the tuple
					else:
						print("User with the same name does not exist in the database.")
						return None  # Return None if user not found
					
		except sqlite3.Error as error:
			print("Failed to retrieve from Users table", error)
			return None  # Return None in case of any error