from sqltasks import *
file1 = open('studentlist.csv', 'r')
resetStudentDb()
Lines = file1.readlines()
for line in Lines:
	em=line.strip()
	print('Adding '+em)
	addStudent(em)
	