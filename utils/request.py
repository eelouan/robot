from dotenv import load_dotenv
import time

from utils.Assert import *

def get_last_order_athena(conn):
    db = conn.cursor()
    db.execute(
        "SELECT TOP 1 c.NumTicCDC FROM CMD_CLIENT c ORDER BY c.DateCDC DESC"
    )
    return db.fetchone()[0]

def get_last_order(conn):
    db = conn.cursor()
    db.execute(
        "SELECT reference FROM `order` ORDER BY id DESC LIMIT 1"
    )
    return db.fetchone()

def get_web_order(conn, num):
    sql = "SELECT * FROM `order` o WHERE o.reference = %s LIMIT 1"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (num,))
        row = cur.fetchone()
    return row

def get_web_order_carrier_address(conn, id):
    sql = "SELECT * FROM `order_carrier_address` o WHERE o.order_carrier_id = %s LIMIT 1"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (id,))
        row = cur.fetchone()
    return row

def get_web_order_carrier(conn, id):
    sql = "SELECT * FROM `order_carrier` oc WHERE oc.order_id = %s LIMIT 1"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (id,))
        row = cur.fetchone()
    return row

def get_web_order_adress(conn, id):
    sql = "SELECT * FROM `order_address` oa WHERE oa.order_id = %s LIMIT 1"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (id,))
        row = cur.fetchone()
    return row

def get_web_customer(conn, id):
    sql = "SELECT * FROM `customer` c WHERE c.id = %s LIMIT 1"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (id,))
        row = cur.fetchone()
    return row

def get_order_status_num_tic(conn, num_tic):
    db = conn.cursor()
    db.execute(
        "SELECT c.CodStatutCC FROM CMD_CLIENT c WHERE c.NumTicCDC = ?",
        (num_tic,)
    )
    result = db.fetchall()
    return [row[0] for row in result] if result else None

def get_supplier(conn, num_cmd):
    db = conn.cursor()
    db.execute(
        "SELECT TOP 1 c.CodeFouCDC FROM CMD_CLIENT c WHERE c.NumCmdClient = ?",
        (num_cmd,)
    )
    result = db.fetchone()
    return result[0] if result else None

def get_order_status_num_cmd(conn, num_cmd):
    db = conn.cursor()
    db.execute(
        "SELECT TOP 1 c.CodStatutCC FROM CMD_CLIENT c WHERE c.NumCmdClient = ?",
        (num_cmd,)
    )
    result = db.fetchone()
    return result[0] if result else None

def get_code_intern(conn, num_cmd):
    db = conn.cursor()
    db.execute(
        "SELECT TOP 1 c.CodeIntArtCDC FROM CMD_CLIENT c WHERE c.NumCmdClient = ?",
        (num_cmd,)
    )
    result = db.fetchone()
    return result[0] if result else None
    
def get_cmd_client(conn, numtic, index):
    db = conn.cursor()
    db.execute(
        "SELECT c.NumCmdClient FROM CMD_CLIENT c WHERE c.NumTicCDC = ?",
        (numtic,)
    )
    result = db.fetchall()
    return result[index][0] if result else None

def get_supplier_order(conn, num_cmd_client, max_retries=5, delay=1):
    db = conn.cursor()
    attempt = 0

    while attempt < max_retries:
        db.execute(
            "SELECT c.NumCdeFouCDC FROM CMD_CLIENT c WHERE c.NumCmdClient = ?",
            (num_cmd_client,)
        )
        result = db.fetchone()

        if result[0]:
            return result[0]

        attempt += 1
        time.sleep(delay)

    return None

def is_supplier_order(conn, num_cmd_client):
    db = conn.cursor()

    db.execute(
        "SELECT c.NumCdeFouCDC, c.ExporteYakaEdiCDC FROM CMD_CLIENT c WHERE c.NumCmdClient = ?",
        (num_cmd_client,)
    )
    result = db.fetchone()

    if result[0]["ExporteYakaEdiCDC"] == 1 and not result[0]["NumCdeFouCDC"]:
        Assert.set_intercept("dispo_supplier")
    if result[0]["ExporteYakaEdiCDC"] == 1:
        Assert.set_intercept("error_job_supplier_order")
    return True


def update_eligible_yakaedi(conn, eligible, tic_cdc):
    db = conn.cursor()
    db.execute(
        "UPDATE CMD_CLIENT SET EligibleYakaEdiCDC = ? WHERE NumTicCDC = ?",
        (eligible, tic_cdc)
    )
    conn.commit()
    return db.rowcount