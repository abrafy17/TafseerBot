# example-config

#make a folder name config add config.py file in it and have following format

import mysql.connector

TOKEN = "" # Your discord application token

def get_mysql_connection():
    db_connection = mysql.connector.connect(
        host="", #sql host
        user="", #sql user-name
        password="", #sql password
        database="",
        port=
    )
    return db_connection