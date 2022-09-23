import io
import json
import logging
import oracledb
import subprocess
import datetime

from fdk import response


def handler(ctx, data: io.BytesIO=None):
    # Grab from config
    cfg = dict(ctx.Config())

    try:
        un = cfg['PYTHON_USERNAME']
        pw = cfg['PYTHON_PASSWORD']
        cs = cfg['PYTHON_CONNECTSTRING']
    except Exception as ex:
        logging.getLogger().info(f"Unable to get Config - quitting: {ex}")
    logging.getLogger().info("Inside Python DB function")

    resp = ""
    # Load JSON Data
    body = json.loads(data.getvalue())
    
    try:
        # Enable thick mode
        oracledb.init_oracle_client()
        

        with oracledb.connect(user=un, password=pw, dsn=cs) as connection:
            with connection.cursor() as cursor:
                sql = """SELECT UNIQUE CLIENT_DRIVER
                    FROM V$SESSION_CONNECT_INFO
                    WHERE SID = SYS_CONTEXT('USERENV', 'SID')"""
                for r, in cursor.execute(sql):
                    print(r)

            with connection.getSodaDatabase() as sodadb:
                collection = sodadb.createCollection("mycollection")
                returned = collection.insertOneAndGet(body)
                resp += str(returned)
            # with connection.cursor() as cursor:
            #     insert_sql = "insert into BACKUP_EVENTS values (:1, :2, :3, :4, :5)"
            #     sql_resp = cursor.execute(insert_sql, [1, "a", 2, datetime.datetime.now(), 3, datetime.datetime.now(), 4, "1", 5, body])
            #     #sql = """select count(*) from BACKUP_EVENTS"""
            #     #for r in cursor.execute(sql):
            #     #    print(r)
            #     #    resp += str(r)
            #     resp += str(sql_resp)
    except Exception as ex:
        logging.getLogger().error('error parsing json payload: ' + str(ex))
        resp += str(ex)

    return response.Response(
        ctx, response_data=json.dumps(
            {"message": f"SQL Res: {resp}"}),
        headers={"Content-Type": "application/json"}
    )
