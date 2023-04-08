#!/usr/bin/python3
from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

cnx = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)


def get_table(name, params=""):
    cursor = cnx.cursor()
    cursor.execute(f"SELECT * FROM {name} {params}")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    result = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        result.append(row_dict)
    return result


def execute(query, params=()):
    cursor = cnx.cursor()
    cursor.execute(query, params)
    cnx.commit()

