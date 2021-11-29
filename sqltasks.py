import pyodbc
from io import StringIO
import csv
server = 'reverseproxyserver.database.windows.net'
database = 'reverseproxy_sql'
username = 'sql_user'
password = '{Password12345*}'   
driver= '{ODBC Driver 17 for SQL Server}'
conn=pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor=conn.cursor()

def createTable():
	try:
		cursor.execute("CREATE TABLE [Attendance](key_reg VARCHAR(30) , class_id VARCHAR(10) CONSTRAINT info UNIQUE (key_reg, class_id))")
		cursor.commit()
	except:
		pass

def addUser(key_reg, class_id):
	try:
		command = 'INSERT INTO [Attendance] VALUES (?,?)'	
		cursor.execute(command,key_reg,class_id)
		cursor.commit()
	except:
		createTable()
		try:
			command = 'INSERT INTO [Attendance] VALUES (?,?)'	
			cursor.execute(command,key_reg,class_id)
			cursor.commit()
		except:
			pass


def getReg_nobyclass_id(class_id):
	try:
		command ='SELECT key_reg FROM [Attendance] WHERE class_id=?'
		cursor.execute(command,class_id)
		retValue=cursor.fetchall()
		cursor.commit()
		si="Attendance report\n"
		for i in retValue:
			si=si+i[0]+"\n"
		#print(retValue)
		#print(si)
		return si
		 
	except:
		return "Error"


def deleteFromUser(class_id):
	command='DELETE FROM [Attendance] WHERE class_id=?'
	cursor.execute(command,class_id)
	cursor.commit()

def dropTable():
	cursor.execute("DROP TABLE IF EXISTS [Attendance]")
	cursor.commit()
		
def resetDb():
	dropTable()
	createTable()
	
def createStudentTable():
	try:
		cursor.execute("CREATE TABLE [Student](email VARCHAR(30) UNIQUE)")
		cursor.commit()
	except:
		pass

def addStudent(email):
	try:
		command = 'INSERT INTO [Student] VALUES (?)'	
		cursor.execute(command,email)
		cursor.commit()
	except:
		createStudentTable()
		try:
			command = 'INSERT INTO [Student] VALUES (?)'	
			cursor.execute(email)
			cursor.commit()
		except:
			pass


def getEmail(reg):
	try:
		command ='SELECT email FROM [Student] WHERE email like ?'
		reg='%'+reg+'%'
		cursor.execute(command,reg)
		retValue=cursor.fetchone()[0]
		return retValue
	except:
		return "Error"

def dropStudentTable():
	cursor.execute("DROP TABLE IF EXISTS [Student]")
	cursor.commit()
		
def resetStudentDb():
	dropStudentTable()
	createStudentTable()
