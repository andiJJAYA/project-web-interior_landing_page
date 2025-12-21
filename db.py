import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",      
        database="interior_db",
        cursorclass=pymysql.cursors.DictCursor  
    )