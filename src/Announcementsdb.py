import sqlite3
import os
from io import BytesIO
from PIL import Image
import uuid

#
#	Add the path to the project so that the imports work
#
import sys
sys.path.append("/home/catalin/workspace/git/MiniOnlineStore/src")
#
#	Import the database classes
#
from Usersdb import UserDatabase
#
#	Establish connection to the databases
#
UserDatabase_path = "src/data_bases/users_database.db"
user_db = UserDatabase(UserDatabase_path)

class AnnouncementDataBase:
	#
	#	Constructor
	#
	def __init__(self, path):
		self.path = path
		#
		#	Create table
		#
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				
				cursor.execute('''CREATE TABLE announcements (
				   				id INTEGER PRIMARY KEY AUTOINCREMENT,
								id_user INTEGER,
								category TEXT,
								name TEXT,
								description TEXT,
								price REAL,
								main_photo BLOB,
								second_photo_1 BLOB,
								second_photo_2 BLOB,
								second_photo_3 BLOB,
				   				FOREIGN KEY(id_user) REFERENCES users(id)
								)''')
								
				if not self.announcementTableExists:
					print("Announcement table successfully created")

		except sqlite3.Error as error:
			print("Failed to create Announcements", error)
			 
	#
	# 	Establish connection to the database
	#
	def connect(self):
		return sqlite3.connect(self.path)
	
	#
	# 	Check table exists
	#
	def announcementTableExists(self):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT * FROM announcements")
				annoucement = cursor.fetchone()
				print("Announcement table exists")
				return annoucement is not None
		
		except sqlite3.Error as error:
			print("Failed to retrieve from Announcement table", error)


	#												
	#	Function to convert data to binary	 		
	#												
	@staticmethod
	def convertToBinaryData(filename):
		try:
			if filename is None or not os.path.exists(filename):
				raise ValueError("Invalid file name or file does not exist")

			with open(filename, 'rb') as file:
				blobData = file.read()
			return blobData

		except Exception as e:
			print("Failed to convert data to binary:", str(e))
			return None

	
	#
	#	Function for searching existing announcement
	#
	def announcement_exists(self, current, category, name):
		# Check if an announcement with the given category or name already exists
		current.execute("SELECT * FROM announcements WHERE category = ? AND name = ?", (category, name))
		existing_announcement = current.fetchone()
		return existing_announcement is not None
		  
	#
	#	Function for inserting into table
	#
	def insertAnnouncementIntoAnnouncementsTable(self, id_user, category, name, description, price, main_photo, second_photo_1, second_photo_2, second_photo_3):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				#
				#	Check if an announcement with the given category or name already exists
				#
				if not self.announcement_exists(cursor, category, name):
					announcement_main_photo = self.convertToBinaryData(main_photo)
					announcement_second_photo_1 = self.convertToBinaryData(second_photo_1)
					announcement_second_photo_2 = self.convertToBinaryData(second_photo_2)
					announcement_second_photo_3 = self.convertToBinaryData(second_photo_3)

					sqlite_inser_with_param = '''INSERT INTO announcements (id_user, category, name, description, price, 
												main_photo, second_photo_1, second_photo_2, second_photo_3) 
												VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
												'''
					if not user_db.user_exists_by_id(id_user):
						print("User with id = {} does not exist".format(id_user))
						return
					
					else:
						announcement_tuple = (id_user, category, name, description, price, announcement_main_photo, announcement_second_photo_1, announcement_second_photo_2, announcement_second_photo_3)

					cursor.execute(sqlite_inser_with_param, announcement_tuple)
					connect.commit()

					print("Announcement inserted successfully into announcements table")
				else:
					print("Announcement already exists in announcements table")

		except sqlite3.Error as error:
			print("Failed to insert data into announcements table", error)

	#
	#	Function 
	#
	def checkAnnouncementForAddIntoDataBase(self, category, name):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()

				# Check if the user with the given name and password exists
				cursor.execute("SELECT * FROM announcements WHERE category = ? and name = ?", (category, name))
				existing_announcement = cursor.fetchall()

				if existing_announcement:
					print("Announcement exists in the announcements_database")
					return True
				else:
					print("Announcement does not exist in the announcements_database")
					return False

		except sqlite3.Error as error:
			print("Failed to check announcement in the announcements_database", error)
			return False
	
	#
	#	Saving photos for announcement
	#
	@staticmethod   
	def save_main_photo(file):
		try:
			if not file or not hasattr(file, 'filename'):
				raise ValueError("Invalid file object")

			upload_folder = 'static/announcement_photos'
			os.makedirs(upload_folder, exist_ok=True)

			filename = os.path.join(upload_folder, file.filename)
			file.save(filename)
			return filename

		except Exception as e:
			print("Failed to save main photo:", str(e))
			return None
	
	@staticmethod
	def save_secondary_photo1(file):
		try:
			if not file or not hasattr(file, 'filename'):
				raise ValueError("Invalid file object")

			upload_folder = 'static/announcement_photos'
			os.makedirs(upload_folder, exist_ok=True)

			filename = os.path.join(upload_folder, file.filename)
			file.save(filename)
			return filename

		except Exception as e:
			print("Failed to save main photo:", str(e))
			return None

	@staticmethod
	def save_secondary_photo2(file):
		try:
			if not file or not hasattr(file, 'filename'):
				raise ValueError("Invalid file object")

			upload_folder = 'static/announcement_photos'
			os.makedirs(upload_folder, exist_ok=True)

			filename = os.path.join(upload_folder, file.filename)
			file.save(filename)
			return filename

		except Exception as e:
			print("Failed to save main photo:", str(e))
			return None

	@staticmethod
	def save_secondary_photo3(file):
		try:
			if not file or not hasattr(file, 'filename'):
				raise ValueError("Invalid file object")

			upload_folder = 'static/announcement_photos'
			os.makedirs(upload_folder, exist_ok=True)

			filename = os.path.join(upload_folder, file.filename)
			file.save(filename)
			return filename

		except Exception as e:
			print("Failed to save main photo:", str(e))
			return None
		
	#
	#	Function for searching if exists announcement by id_user	
	#
	def announcement_exists_by_id_user(self, id_user):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT * FROM announcements WHERE id_user = ?", (id_user,))
				existing_announcement = cursor.fetchall()
				return len(existing_announcement) > 0
			
		except sqlite3.Error as error:
			print("Failed to retrieve from Announcements table", error)
			return False

	#
	#	Retrieving announcements using id_user
	#
	def retrieveAnnouncementsFromAnnTableByIdUser(self, id_user):
		try:
			if self.announcement_exists_by_id_user(id_user):  # Call the existence check directly
				with self.connect() as connect:
					cursor = connect.cursor()
					cursor.execute("SELECT category, name, description, price FROM announcements WHERE id_user=?", (id_user,))
					announcements = cursor.fetchall()
					print("Announcements retrieved successfully from announcements_database")
					return announcements
			else:
				print(f"No announcements posted by user: {id_user}")
				return []  # Return an empty list if no announcements exist
		except sqlite3.Error as error:
			print("Failed to retrieve from announcements table", error)
			return []

	#
	#	Function for searching if exists announcement by id of announcement
	#
	def announcement_exists_by_id(self, id):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT * FROM announcements WHERE id = ?", (id,))
				existing_announcement = cursor.fetchone()
				return len(existing_announcement) > 0
			
		except sqlite3.Error as error:
			print("Failed to retrieve from Announcements table", error)
			return False
	#
	#	Retrieving announcements using id of announcement
	#
	def retrieveAnnouncementsFromAnnTableById(self, id):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				if self.announcement_exists_by_id(id):
						cursor.execute("SELECT * FROM announcements WHERE id = ?", (id,))
						announcement = cursor.fetchone()
						print(f"Announcement {id} retrieved succesfully from announcements_database")
						return announcement
				else:
					print("Announcement not found!")

		except sqlite3.Error as error:
			print("Failed to retrieve from announcements table")

	#
	#	Function for finding category
	#
	def category_exists(self, category):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT COUNT(*) FROM announcements WHERE category = ?", (category,))
				count = cursor.fetchone()[0]
				if count > 0:
					print(f"Category {category} found!")
					return True  
				else:
					print(f"Category {category} not found!")
					return False  

		except sqlite3.Error as error:
			print("Failed to retrieve from Announcements table", error)

	
	#
	#	Retrieveing announcements using category 
	#
	def retrieveAnnouncementsFromAnnTableByCategory(self, category):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				if self.category_exists(category):
					cursor.execute("SELECT * FROM announcements WHERE category = ?", (category,))
					existing_announcements = cursor.fetchall()
					print(f"Succesfully returning announcements for category: {category}")
					return existing_announcements
				
		except sqlite3.Error as error:
			print("Failed to retrieve from announcements table")
	
	#
	#	Searching announcements inside database
	#
	def search_announcements(self, category, name):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				if category == 'all':
					cursor.execute("SELECT * FROM announcements WHERE name LIKE ?", ('%' + name + '%',))
					existing_announcements = cursor.fetchall()
					print(f"Found announcements for {name} in all categories")
				
				elif self.category_exists(category):
					cursor.execute("SELECT * FROM announcements WHERE category = ? AND name LIKE ?", (category, '%' + name + '%',))
					existing_announcements = cursor.fetchall()
					print(f"Found announcements for {category} and {name}")

				return existing_announcements
			
		except sqlite3.Error as error:
			print("Failed to retrieve from announcements table")
				
if __name__ == '__main__':

	# Run my function: category_exists
	announcement_db = AnnouncementDataBase("src/data_bases/announcements_database.db")
	#announcement_db.category_exists("imobiliare")
	#print(announcement_db.retrieveAnnouncementsFromAnnTableByCategory("imobiliare")[3][3])
	print(announcement_db.retrieveAnnouncementsFromAnnTableById(8)[1])
	existing_ads = announcement_db.search_announcements('imobiliare', 'mercedes')
	print(existing_ads[0][3])	