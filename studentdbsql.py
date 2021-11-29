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

def createStudentTable():
	try:
		cursor.execute("CREATE TABLE [Student](email VARCHAR(40))")
		cursor.commit()
	except:
		pass

def addStudent(email):
	try:
		command = 'INSERT INTO [Student] VALUES (?)'	
		cursor.execute(email)
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
		cursor.execute(reg)
		retValue=cursor.fetchone()[0]
		return retValue
	except:
		return "Error"