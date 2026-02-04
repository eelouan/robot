import subprocess
import time
import os
import sys, io
import mysql.connector
import pyodbc

from dotenv import load_dotenv

load_dotenv()


def connect_web_pp():
    conn = mysql.connector.connect(
        host=os.getenv("pp_host_web"),
        port=int(os.getenv("pp_port_web")),
        user=os.getenv("pp_user_web"),
        password=os.getenv("pp_passwd_web"),
        database=os.getenv("pp_name_web")
    )

    return conn

def connect_athena_rec():
    conn_str = (
        f"DRIVER={{SQL Server}};"
        f"SERVER={os.getenv('rec_host_athena')},{os.getenv('rec_port_athena')};"
        f"DATABASE={os.getenv('rec_name_athena')};"
        f"UID={os.getenv('rec_user_athena')};"
        f"PWD={os.getenv('rec_passwd_athena')}"
    )
    return pyodbc.connect(conn_str)