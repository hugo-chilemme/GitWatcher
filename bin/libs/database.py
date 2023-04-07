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


def get_table(name, params=None):
    cursor = cnx.cursor()
    cursor.execute(f"SELECT * FROM {name}")
    return cursor.fetchall()

def execute(query, params=()):
    cursor = cnx.cursor()
    cursor.execute(query, params)
    cnx.commit()

