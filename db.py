import mysql.connector

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'secret',
)

cursor = mydb.cursor()

cursor.execute('CREATE DATABASE example')

cursor.execute('SHOW DATABASES')

for db in cursor:
    print(db)