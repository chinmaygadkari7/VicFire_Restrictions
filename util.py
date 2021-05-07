import mysql.connector
from datetime import datetime

CONNECTION = False

def connector():
    if CONNECTION == False:
        mydb = mysql.connector.connect(host="localhost", user="chinmay", password="foopass")
        global CONNECTION = True
        cursor = mydb.cursor()
        cursor.execute("USE firesafe;")

    return cursor

def get_data(locality):
    cursor = conector()
    query = "SELECT fire_ban, start, end FROM restriction WHERE locality='{locality}'"
    _ = cursor.execute(query.format(locality))
    result = cursor.fetchone()

    if result is None:
        raise LookupError("Locality not found.")

    fire_ban, start, end = result
    result = {
        "locality": locality,
        "fire_ban": True if fire_ban.lower() == 'true' else False,
        "start": datetime.strftime(start, "%Y-%m-%d"),
        "end": datetime.strftime(end, "%Y-%m-%d")
    }
    return result
