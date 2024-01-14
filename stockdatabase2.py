import mysql.connector
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="8848613225",
    )
mycursor=mydb.cursor()
try: 
    mycursor.execute("create database stockpro")
    print("database created")
except Exception as e:
    print(e)
