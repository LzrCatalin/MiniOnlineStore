import sqlite3
import os
from io import BytesIO
from PIL import Image

class CommentDatabase:
	# Constructor
	def __init__(self, path):
		self.path = path
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute('''
					CREATE TABLE comments (
						id INTEGER PRIMARY KEY AUTOINCREMENT,
						id_user INTEGER,
						id_announcement INTEGER,
						comment_text TEXT,
						parent_comment_id INTEGER,  -- Field for parent comment
						FOREIGN KEY(id_user) REFERENCES users(id),
						FOREIGN KEY(id_announcement) REFERENCES announcements(id),
						FOREIGN KEY(parent_comment_id) REFERENCES comments(id) 
					)
				''')
				if not self.commentsTableExists:
					print("Comments table successfully created")
		
		except sqlite3.Error as error:
			print("Failed to create Comments Table", error)


	#
	# 	Establish connection to the database
	#
	def connect(self):
		return sqlite3.connect(self.path)
	
	#
	# 	Check table exists
	#
	def commentsTableExists(self):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT * FROM comments")
				annoucement = cursor.fetchone()
				print("Comments table exists")
				return annoucement is not None
		
		except sqlite3.Error as error:
			print("Failed to retrieve from Comments table", error)

	#
	#	Insert into comments table
	#
	def insertCommentIntoCommentsTable(self, id_user, id_announcements, comment_text):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				sqlite_insert_with_param = '''
											INSERT INTO comments (id_user, id_announcement, comment_text)
											VALUES (?, ?, ?)
											'''
				comment_tuple = (id_user, id_announcements, comment_text)
				cursor.execute(sqlite_insert_with_param, comment_tuple)
				connect.commit()
				print("Comment inserted succesfully into comments table")

		except sqlite3.Error as error:
			print("Failed to insert data into comments table", error)

	#
	#	Retrieving comments from table
	#
	def retrieveCommentsFromTableByIdAd(self, id_announcement):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute("SELECT * FROM comments WHERE id_announcement =?", (id_announcement,))
				existing_comments = cursor.fetchall()
				return existing_comments
			
		except sqlite3.Error as error:
			print("Failed to retrieve from comments table", error)

	#
	#	Function for adding replies to database
	#
	def addReplyToComment(self, id_user, id_announcement, comment_text, parent_comment_id):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute(
					'''
					INSERT INTO comments (id_user, id_announcement, comment_text, parent_comment_id)
					VALUES (?, ?, ?, ?)
					''',
					(id_user, id_announcement, comment_text, parent_comment_id)
				)
				connect.commit()
				return True

		except sqlite3.Error as error:
			print("Failed to add reply to comment:", error)
			return False

	#
	#	Function for retrieving replies from database for comment
	#
	def retrieveRepliesForComment(self, comment_id):
		try:
			with self.connect() as connect:
				cursor = connect.cursor()
				cursor.execute(
					'''
					SELECT * FROM comments
					WHERE parent_comment_id = ?
					''',
					(comment_id,)
				)
				replies = cursor.fetchall()
				return replies

		except sqlite3.Error as error:
			print("Failed to retrieve replies for comment:", error)
			return []
		
if __name__ == '__main__':

	print("This is a module, not a script!")
	commentsdb = CommentDatabase("src/data_bases/comments_database.db")
	commentsdb.connect()
	commentsdb.commentsTableExists()
	commentsdb.insertCommentIntoCommentsTable(1, 1, "This is a comment")