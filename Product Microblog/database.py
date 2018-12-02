import sqlite3

conn=sqlite3.connect('database.db')

conn.execute('''CREATE TABLE userdetails
			(email TEXT PRIMARY KEY,
			password TEXT,
			firstname TEXT,
			lastname TEXT,
			userid INTEGER AUTO INCREMENT
			)''')


conn.execute('''CREATE TABLE likes
			(likes INTEGER,
			blogid INTEGER,
			email TEXT,
			FOREIGN KEY(blogid) REFERENCES userdetails(blogid),
			FOREIGN KEY(email) REFERENCES blogsdata(email)
			)''')

conn.execute('''CREATE TABLE dislikes
			(dislikes INTEGER,
			blogid INTEGER,
			email TEXT,
			FOREIGN KEY(blogid) REFERENCES userdetails(blogid),
			FOREIGN KEY(email) REFERENCES blogsdata(email)
			)''')

conn.execute('''CREATE TABLE blogsdata
			(email TEXT,
			firstname TEXT,
			lastname TEXT,
			title TEXT,
			tag1 TEXT,
			tag2 TEXT,
			paragraph TEXT,
			blogid INTEGER PRIMARY KEY,
			blogcreateddate DATETIME,
			validblog BOOLEAN,
			FOREIGN KEY(email) REFERENCES userdetails(email),
			FOREIGN KEY(firstname) REFERENCES userdetails(firstname),
			FOREIGN KEY(lastname) REFERENCES userdetails(lastname)
			)''')

conn.execute('''CREATE TABLE comments
			(firstname TEXT,
			lastname TEXT,
			email TEXT,
			blogid INTEGER,
			comment TEXT,
			commentcreateddate DATETIME,
			valid BOOLEAN,
			FOREIGN KEY(blogid) REFERENCES blogsdata(blogid)
			)''')

conn.execute('''CREATE TABLE tagstable
			(tagname TEXT,
			countofflag INTEGER,
			tagcreateddate DATETIME,
			tagid INTEGER PRIMARY KEY
			)''')


conn.close()