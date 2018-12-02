from flask import *
from datetime import date,time, datetime
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename

app=Flask(__name__)
app.secret_key ='random string'
UPLOAD_FOLDER ='static/uploads'
# ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def getLoginDetails():
	if 'email' not in session:
		loggedin = False
		firstname=''
		lastname=''
		email=''
		return (loggedin, firstname, lastname,email)
	else:
		with sqlite3.connect('database.db') as conn:
			cur=conn.cursor()
			loggedin=True
			cur.execute("SELECT firstname,lastname, email FROM userdetails WHERE email='"+session['email']+"'")
			firstname,lastname,email = cur.fetchone()
		conn.close()
		return (loggedin, firstname,lastname,email)

@app.route("/")
def root():
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	with sqlite3.connect('database.db') as conn:
		if loggedin:
			if email=='admin@g.com':
				cur=conn.cursor()
				cur.execute('SELECT firstname,lastname, title, paragraph, tag1, tag2, blogcreateddate, blogid from blogsdata where validblog=? Order By blogcreateddate',(False,))
				itemData=cur.fetchall()
				itemData=parse(itemData)
				return render_template('adminhomepage.html', itemData=itemData, loggedin=loggedin, firstname=firstname, lastname=lastname, email=email)
			cur=conn.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE validblog=? ORDER BY blogcreateddate DESC',(True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
			tagdata=cur.fetchall()
			print(tagdata)
			tagdata=parse(tagdata)
			print(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			print(taglist)
			return render_template('homepage.html',taglist=taglist,itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
		else:
			cur=conn.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE validblog=? ORDER BY blogcreateddate DESC',(True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate LIKE ?',(today+'%',))
			tagdata=cur.fetchall()
			tagdata=parse(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			return render_template('homepage.html', taglist=taglist , itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)

@app.route("/blogpost/message=<string:message>")
def root1(message):
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	with sqlite3.connect('database.db') as conn:
		if loggedin:
			cur=conn.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE validblog=? ORDER BY blogcreateddate DESC',(True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
			tagdata=cur.fetchall()
			tagdata=parse(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			return render_template('homepage.html',message=message, taglist=taglist ,itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
		else:
			cur=conn.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE validblog=? ORDER BY blogcreateddate DESC',(True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate=?',(today+'%',))
			tagdata=cur.fetchall()
			tagdata=parse(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			return render_template('homepage.html',message=message, taglist=taglist , itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)

def parse(data):
	ans=[]
	i=0
	while i<len(data):
		cur=[]
		for j in range(1):
			if i>=len(data):
				break
			cur.append(data[i])
			i+=1
		ans.append(cur)
	return ans

@app.route("/logout")
def logout():
	session.pop('email', None)
	return redirect(url_for('root'))

@app.route("/loginForm")
def loginForm():
	if 'email' in session:
		return redirect(url_for('root'))
	else:
		return render_template('loginregister.html', error='')


@app.route("/login", methods=['POST','GET'])
def login():
	if request.method=='POST':
		email=request.form['email']
		password = request.form['password']
		if is_valid(email,password):
			session['email'] = email
			message="Logged In Successfully"
			return redirect(url_for('root'))
		else:
			error='Invalid UserID/Password'
			return render_template('loginregister.html', error=error)

@app.route("/createthepost")
def createpost():
	if 'email' not in session:
		return render_template('loginregister.html', error='')
	else:
		return render_template('add.html')

@app.route("/createthepost", methods=['POST','GET'])
def createthepost():
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	if request.method=='POST':
		title=request.form['title']
		paragraph=request.form['paragraph']
		tag1=request.form['tag1']
		tag1=tag1.title()
		tag2=request.form['tag2']
		tag2=tag2.title()
		validblog=False
		with sqlite3.connect('database.db') as con:
			try:
				cur=con.cursor()
				cur.execute('INSERT INTO blogsdata (email,firstname, lastname, title, tag1, tag2, paragraph,blogcreateddate, validblog) VALUES(?,?,?,?,?,?,?,?,?)', (email, firstname, lastname,title, tag1, tag2, paragraph,today,validblog))
				con.commit()
				message="Blog Submitted, Waiting For Approval from Admin"
				cur.execute('INSERT INTO tagstable (tagname, countofflag,tagcreateddate) VALUES (?,?,?)', (tag1,1,today))
				con.commit()
				cur.execute('INSERT INTO tagstable (tagname, countofflag,tagcreateddate) VALUES (?,?,?)', (tag2,1,today))
				con.commit()
			except:
				con.rollback()
				message="Adding to blog failed"
		con.close()
		return redirect(url_for('root1', message=message))

@app.route("/viewingsinglepost/blogid=<int:blogid>")
def watchingfullpost(blogid):
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	if loggedin:
		with sqlite3.connect('database.db') as con:
			cur=con.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE blogid=? and validblog = ?',(blogid,True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
			tagdata=cur.fetchall()
			print(tagdata)
			tagdata=parse(tagdata)
			print(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			cur.execute('SELECT firstname,lastname,email,comment,commentcreateddate from comments where blogid=?',(blogid,))
			commentdata=cur.fetchall()
			commentdata=parse(commentdata)
			cur.execute('SELECT count(comment) from comments where blogid=?',(blogid,))
			count=cur.fetchone()
			c=count[0]
			cur.execute('SELECT count(likes) from likes where blogid=?',(blogid,))
			totlikes=cur.fetchone()
			totallikes=totlikes[0]
			cur.execute('SELECT likes from likes where blogid=? and email=? ',(blogid,email))
			likes=cur.fetchone()
			if likes:
				liked=True
				disliked=False
				cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
				dislikes=cur.fetchone()
				totaldislikes=dislikes[0]
				if totaldislikes:
					return render_template('viewingsinglepost.html',taglist=taglist,liked=liked, disliked=disliked,totallikes=totallikes-1, totaldislikes=totaldislikes, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
				else:
					return render_template('viewingsinglepost.html',taglist=taglist,liked=liked, disliked=disliked,totallikes=totallikes, totaldislikes=totaldislikes, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
			else:
				liked=False
				cur.execute('SELECT dislikes from dislikes where blogid=? and email=?',(blogid,email))
				totdislikes=cur.fetchone()
				if totdislikes:
					disliked=True
					cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
					dislikes=cur.fetchone()
					totaldislikes=dislikes[0]
					if totaldislikes:
						return render_template('viewingsinglepost.html',taglist=taglist,liked=liked, disliked=disliked,totallikes=totallikes, totaldislikes=totaldislikes-1, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
					else:
						return render_template('viewingsinglepost.html',taglist=taglist,liked=liked, disliked=disliked,totallikes=totallikes, totaldislikes=totaldislikes, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
				else:
					disliked=False
					cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
					dislikes=cur.fetchone()
					totaldislikes=dislikes[0]
					if totaldislikes:
						return render_template('viewingsinglepost.html',liked=liked, taglist=taglist,disliked=disliked,totallikes=totallikes-1, totaldislikes=totaldislikes-1, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
					else:
						return render_template('viewingsinglepost.html',liked=liked, taglist=taglist,disliked=disliked,totallikes=totallikes, totaldislikes=totaldislikes, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
	else:
		with sqlite3.connect('database.db') as con:
			cur=con.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid,validblog FROM blogsdata WHERE blogid=? and validblog=?',(blogid,True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
			tagdata=cur.fetchall()
			print(tagdata)
			tagdata=parse(tagdata)
			print(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			cur.execute('SELECT firstname,lastname,email,comment,commentcreateddate from comments where blogid=? ',(blogid,))
			commentdata=cur.fetchall()
			commentdata=parse(commentdata)
			cur.execute('SELECT count(comment) from comments where blogid=?',(blogid,))
			count=cur.fetchone()
			c=count[0]
			cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
			dislikes=cur.fetchone()
			totaldislikes=dislikes[0]
			liked=False
			disliked=False
			cur.execute('SELECT count(likes) from likes where blogid=?',(blogid,))
			totlikes=cur.fetchone()
			totallikes=totlikes[0]
			return render_template('viewingsinglepost.html',liked=liked,taglist=taglist, disliked=disliked,totallikes=totallikes,totaldislikes=totaldislikes,itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)

@app.route("/validblog/blogid=<int:blogid>/val=<int:val>")
def validblog(blogid,val):
	loggedin,firstname,lastname,email=getLoginDetails()
	if loggedin:
		if val:
			with sqlite3.connect('database.db') as con:
				cur=con.cursor()
				cur.execute('UPDATE blogsdata SET validblog=? WHERE blogid=?',(val,blogid,))
				con.commit()
				return redirect(url_for('root'))
		else:
			return redirect(url_for('root'))
	else:
		return redirect(url_for('loginForm'))

@app.route("/viewingsinglepostlike/blogid=<int:blogid>/val=<int:val>")
def watchingfullpostlike(blogid,val):
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	if loggedin:
		if val:
			with sqlite3.connect('database.db') as con:
				cur=con.cursor()
				cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE blogid=? and validblog=?',(blogid,True,))
				itemData=cur.fetchall()
				itemData=parse(itemData)
				cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
				tagdata=cur.fetchall()
				print(tagdata)
				tagdata=parse(tagdata)
				print(tagdata)
				tagset=set()
				taglist=[]
				for row in tagdata:
					for data in row:
						tagset.add(data[0])
				for i in range(len(tagset)):
					tagvalue=tagset.pop()
					cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
					tagc=cur.fetchone()
					tagcount=tagc[0]
					taglist.append([tagvalue,tagcount])
				cur.execute('SELECT firstname,lastname,email,comment,commentcreateddate from comments where blogid=? ',(blogid,))
				commentdata=cur.fetchall()
				commentdata=parse(commentdata)
				cur.execute('SELECT count(comment) from comments where blogid=?',(blogid,))
				count=cur.fetchone()
				c=count[0]
				cur.execute('SELECT likes from likes where blogid=? and email=?',(blogid,email))
				likes=cur.fetchone()
				if likes:
					cur.execute('SELECT count(likes) from likes where blogid=?',(blogid,))
					totlikes=cur.fetchone()
					totallikes=totlikes[0]
					liked =True
					cur.execute('DELETE from dislikes where blogid=? and email=?',(blogid,email))
					con.commit()
					cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
					dislikes=cur.fetchone()
					totaldislikes=dislikes[0]
					disliked=False
					return render_template('viewingsinglepost.html',taglist=taglist,totallikes=totallikes-1,liked=liked,disliked=disliked,totaldislikes=totaldislikes, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
				else:
					cur.execute('INSERT INTO likes(likes,blogid,email) VALUES (?,?,?)',(val,blogid,email))
					con.commit()
					cur.execute('SELECT count(likes) from likes where blogid=?',(blogid,))
					totlikes=cur.fetchone()
					totallikes=totlikes[0]
					liked =True
					cur.execute('DELETE from dislikes where blogid=? and email=?',(blogid,email))
					con.commit()
					cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
					dislikes=cur.fetchone()
					totaldislikes=dislikes[0]
					disliked=False
					return render_template('viewingsinglepost.html',taglist=taglist,totallikes=totallikes-1,liked=liked,totaldislikes=totaldislikes,disliked=disliked, itemData=itemData,count=c, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
		else:
			with sqlite3.connect('database.db') as con:
				cur=con.cursor()
				cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid, validblog FROM blogsdata WHERE blogid=? and validblog=?',(blogid,True,))
				itemData=cur.fetchall()
				itemData=parse(itemData)
				cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
				tagdata=cur.fetchall()
				tagdata=parse(tagdata)
				tagset=set()
				taglist=[]
				for row in tagdata:
					for data in row:
						tagset.add(data[0])
				for i in range(len(tagset)):
					tagvalue=tagset.pop()
					cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
					tagc=cur.fetchone()
					tagcount=tagc[0]
					taglist.append([tagvalue,tagcount])
				cur.execute('SELECT firstname,lastname,email,comment,commentcreateddate from comments where blogid=?',(blogid,))
				commentdata=cur.fetchall()
				commentdata=parse(commentdata)
				cur.execute('SELECT count(comment) from comments where blogid=?',(blogid,))
				count=cur.fetchone()
				c=count[0]
				cur.execute('SELECT dislikes from dislikes where blogid=? and email=?',(blogid,email))
				distotal=cur.fetchone()
				if distotal:
					cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
					dislikes=cur.fetchone()
					totaldislikes=dislikes[0]
					disliked=True
					cur.execute('DELETE from likes where blogid=? and email=?',(blogid,email))
					con.commit()
					cur.execute('SELECT count(likes) from likes where blogid=?',(blogid,))
					totlikes=cur.fetchone()
					totallikes=totlikes[0]
					liked=False
					return render_template('viewingsinglepost.html',taglist=taglist, itemData=itemData,count=c,liked=liked, disliked=disliked,totallikes=totallikes,totaldislikes=totaldislikes-1, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)
				else:
					cur.execute('INSERT into dislikes(dislikes,blogid,email) VALUES (?,?,?)',(val,blogid,email))
					con.commit()
					cur.execute('SELECT count(dislikes) from dislikes where blogid=?',(blogid,))
					dislikes=cur.fetchone()
					totaldislikes=dislikes[0]
					disliked=True
					cur.execute('DELETE from likes where blogid=? and email=?',(blogid,email))
					con.commit()
					cur.execute('SELECT count(likes) from likes where blogid=?',(blogid,))
					totlikes=cur.fetchone()
					totallikes=totlikes[0]
					liked =False
					return render_template('viewingsinglepost.html', taglist=taglist,itemData=itemData,count=c,liked=liked, disliked=disliked,totallikes=totallikes,totaldislikes=totaldislikes-1, commentdata=commentdata, loggedin=loggedin,firstname=firstname, email=email)

	else:
		return redirect(url_for('loginForm'))

@app.route("/iaminsinglepost/commentadded/blogid=<int:blogid>", methods=['POST','GET'])
def commentinginsinglepost(blogid):
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	todayslice=today[:13]
	if loggedin:
		if request.method=='POST':
			comm=request.form['comment']
			with sqlite3.connect('database.db') as con:
				try:
					cur=con.cursor()
					cur.execute('INSERT INTO comments(firstname, lastname,email,blogid, comment,commentcreateddate) VALUES (?,?,?,?,?,?)',(firstname,lastname,email,blogid,comm,today))
					con.commit()
					cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid,validblog FROM blogsdata WHERE blogid=? and validblog=?',(blogid,True,))
					itemData=cur.fetchall()
					itemData=parse(itemData)
					cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(todayslice+'%',))
					tagdata=cur.fetchall()
					tagdata=parse(tagdata)
					tagset=set()
					taglist=[]
					for row in tagdata:
						for data in row:
							tagset.add(data[0])
					for i in range(len(tagset)):
						tagvalue=tagset.pop()
						cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
						tagc=cur.fetchone()
						tagcount=tagc[0]
						taglist.append([tagvalue,tagcount])
					cur.execute('SELECT firstname,lastname,email,comment,commentcreateddate from comments where blogid=? and validblog=?',(blogid,True,))
					commentdata=cur.fetchall()
					commentdata=parse(commentdata)
					cur.execute('SELECT count(comment) from comments where blogid=?',(blogid,))
					count=cur.fetchone()
					c=count[0]
				except:
					con.rollback()
			con.close()
			return redirect(url_for('watchingfullpost', blogid=blogid))
	else:
		 return redirect(url_for('loginForm'))

def is_valid(email,password):
	con = sqlite3.connect('database.db')
	cur=con.cursor()
	cur.execute('SELECT email, password FROM userdetails')
	data= cur.fetchall()
	for row in data:
		if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
			return True
	return False

@app.route("/registrationForm")
def registrationForm():
	return render_template("loginregister.html")

@app.route("/register", methods=['GET','POST'])
def register():
	if request.method=='POST':
		password=request.form['password']
		email=request.form['email']
		firstname=request.form['firstname']
		lastname=request.form['lastname']
		with sqlite3.connect('database.db') as con:
			try:
				cur=con.cursor()
				cur.execute('INSERT INTO userdetails (password, email, firstname, lastname) VALUES(?,?,?,?)', (hashlib.md5(password.encode()).hexdigest(), email, firstname, lastname))
				con.commit()
				message="Please Enter Your LogIn Credentials"
			except:
				con.rollback()
				message='User ALready Exists'
		con.close()
		return render_template("loginregister.html", message=message)

@app.route("/searchposts", methods=['POST','GET'])
def searchpost():
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	if request.method=='POST':
		search=request.form['search']
		search=search.title()
		with sqlite3.connect('database.db') as con:
			cur=con.cursor()
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE validblog=? and tag1=?',(True,search,))
			itemData=cur.fetchall()
			if itemData:
				itemData=parse(itemData)
				cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
				tagdata=cur.fetchall()
				tagdata=parse(tagdata)
				tagset=set()
				taglist=[]
				for row in tagdata:
					for data in row:
						tagset.add(data[0])
				for i in range(len(tagset)):
					tagvalue=tagset.pop()
					cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
					tagc=cur.fetchone()
					tagcount=tagc[0]
					taglist.append([tagvalue,tagcount])
				return render_template('homepage.html',taglist=taglist, itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
			else:
				cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid FROM blogsdata WHERE validblog=? and tag2=?',(True,search,))
				itemData=cur.fetchall()
				if itemData:
					itemData=parse(itemData)
					cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
					tagdata=cur.fetchall()
					tagdata=parse(tagdata)
					tagset=set()
					taglist=[]
					for row in tagdata:
						for data in row:
							tagset.add(data[0])
					for i in range(len(tagset)):
						tagvalue=tagset.pop()
						cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
						tagc=cur.fetchone()
						tagcount=tagc[0]
						taglist.append([tagvalue,tagcount])
					return render_template('homepage.html',taglist=taglist, itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
				else:
					message="No search elements found"
					cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
					tagdata=cur.fetchall()
					tagdata=parse(tagdata)
					tagset=set()
					taglist=[]
					for row in tagdata:
						for data in row:
							tagset.add(data[0])
					for i in range(len(tagset)):
						tagvalue=tagset.pop()
						cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
						tagc=cur.fetchone()
						tagcount=tagc[0]
						taglist.append([tagvalue,tagcount])
					return render_template('homepage.html', taglist=taglist,message=message,loggedin=loggedin,firstname=firstname, email=email)


@app.route("/searchposts/tagstr=<string:tagstr>")
def searchpostmytag(tagstr):
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	with sqlite3.connect('database.db') as con:
		cur=con.cursor()
		cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid , validblog FROM blogsdata WHERE validblog=? and tag2=?',(True,tagstr,))
		itemData=cur.fetchall()
		if itemData:
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
			tagdata=cur.fetchall()
			tagdata=parse(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
			return render_template('homepage.html',taglist=taglist, itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
		else:
			cur.execute('SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid , validblog FROM blogsdata WHERE validblog=? and tag1=?',(True,tagstr,))
			itemData=cur.fetchall()
			if itemData:
				itemData=parse(itemData)
				cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
				tagdata=cur.fetchall()
				tagdata=parse(tagdata)
				tagset=set()
				taglist=[]
				for row in tagdata:
					for data in row:
						tagset.add(data[0])
				for i in range(len(tagset)):
					tagvalue=tagset.pop()
					cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
					tagc=cur.fetchone()
					tagcount=tagc[0]
					taglist.append([tagvalue,tagcount])
				return render_template('homepage.html',taglist=taglist, itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
			else:
				message="No search elements found"
				cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
				tagdata=cur.fetchall()
				tagdata=parse(tagdata)
				tagset=set()
				taglist=[]
				for row in tagdata:
					for data in row:
						tagset.add(data[0])
				for i in range(len(tagset)):
					tagvalue=tagset.pop()
					cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
					tagc=cur.fetchone()
					tagcount=tagc[0]
					taglist.append([tagvalue,tagcount])
				return render_template('homepage.html', taglist=taglist,message=message,loggedin=loggedin,firstname=firstname, email=email)

@app.route("/viewmine")
def viewmine():
	loggedin,firstname,lastname,email=getLoginDetails()
	d=datetime.today()
	today=d.strftime("%d-%B-%Y %H:%M:%S")
	today=today[:13]
	if loggedin:
		with sqlite3.connect('database.db') as conn:
			cur=conn.cursor()
			cur.execute("SELECT firstname, lastname, title,paragraph,tag1,tag2,blogcreateddate,blogid, validblog FROM blogsdata WHERE email='"+session['email']+ "' and validblog=?",(True,))
			itemData=cur.fetchall()
			itemData=parse(itemData)
			cur.execute('SELECT tagname from tagstable where tagcreateddate like ?',(today+'%',))
			tagdata=cur.fetchall()
			tagdata=parse(tagdata)
			tagset=set()
			taglist=[]
			for row in tagdata:
				for data in row:
					tagset.add(data[0])
			for i in range(len(tagset)):
				tagvalue=tagset.pop()
				cur.execute('SELECT count(tagname) from tagstable where tagcreateddate like ? and tagname like ?',(today+'%',tagvalue,))
				tagc=cur.fetchone()
				tagcount=tagc[0]
				taglist.append([tagvalue,tagcount])
		return render_template('homepage.html',taglist=taglist,tagdata=tagdata, itemData=itemData, loggedin=loggedin,firstname=firstname, email=email)
	else:
		return redirect(url_for('root'))

@app.route("/sellitems")
def sellitem():
	return render_template('sellitem.html')
# @app.route("/changepassword", methods=['GET','POST'])
# def changepassword():
# 	loggedin,firstname,lastname,email=getLoginDetails()
# 	if loggedin:
# 		if request.form=='POST':

@app.route("/changepass")
def changepass():
	if 'email' in session:
		return render_template('changepassword.html')
	else:
		return render_template('loginregister.html', error='')

@app.route("/changepassword", methods=['POST','GET'])
def changepassword():
	loggedin,firstname,lastname,email=getLoginDetails()
	if loggedin:
		if request.method=='POST':
			oldpassword=request.form['oldpassword']
			newpassword=request.form['newpassword']
			with sqlite3.connect('database.db') as con:
				cur=con.cursor()
				cur.execute('SELECT email,password FROm userdetails where email=?',(email,))
				data = cur.fetchall()
				for row in data:
					if row[0]== email and row[1]==hashlib.md5(oldpassword.encode()).hexdigest():
						cur.execute("UPDATE userdetails SET password = ? where email=?",(hashlib.md5(newpassword.encode()).hexdigest(),email,))
						con.commit()
						logout()
						return render_template('loginregister.html')
					else:
						message="Old password is Not Correct"
						return render_template('changepassword.html', message=message)
		else:
			return redirect(url_for('root'))
	else:
		return redirect(url_for('loginForm'))

if __name__=='__main__':
	app.run(debug=True)









