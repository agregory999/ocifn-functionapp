import io
import json
import logging
import oracledb


from fdk import response


def handler(ctx, data: io.BytesIO=None):
    # Grab from config
    cfg = dict(ctx.Config())

    try:
        un = cfg['PYTHON_USERNAME']
        pw = cfg['PYTHON_PASSWORD']
        cs = cfg['PYTHON_CONNECTSTRING']
        debug = cfg['DEBUG']
        event_collection = cfg['EVENT_COLLECTION']
    except Exception as ex:
        logging.getLogger('ocifn-events-adbjson').info(f"Unable to get Config - quitting: {ex}")
    logging.getLogger('ocifn-events-adbjson').info("Inside Python DB function")

    # Process values from config
    if debug and debug.lower() == "true":
        logging.getLogger('ocifn-events-adbjson').setLevel(logging.DEBUG)
        logging.getLogger('ocifn-events-adbjson').debug(f"DEBUG level set")

    if not un or not pw or not cs or not event_collection:
        logging.getLogger('ocifn-events-adbjson').error(f"Error: No Config set")

        return response.Response(
            ctx, response_data=json.dumps(
                {"message": f"Error: missing configs for function"}),
            headers={"Content-Type": "application/json"}
        )

    resp = ""
    # Load JSON Data
    body = json.loads(data.getvalue())
    
    try:
        # Enable thick mode
        oracledb.init_oracle_client()
        
        with oracledb.connect(user=un, password=pw, dsn=cs, tcp_connect_timeout=10) as connection:
            # The general recommendation for simple SODA usage is to enable autocommit
            connection.autocommit = True
            
            # SODA insert
            logging.getLogger('ocifn-events-adbjson').debug(f"Getting SODA")
            sodadb = connection.getSodaDatabase()
            logging.getLogger('ocifn-events-adbjson').debug(f"Got SODA: {sodadb}")
            collection = sodadb.createCollection(event_collection)
            logging.getLogger('ocifn-events-adbjson').debug(f"Created Collection: {collection}")
            returned = collection.insertOneAndGet(body)
            logging.getLogger('ocifn-events-adbjson').debug(f"Inserted: {returned}")
            resp += str(returned)

    except Exception as ex:
        logging.getLogger('ocifn-events-adbjson').error('error parsing json payload: ' + str(ex))
        resp += str(ex)

    logging.getLogger('ocifn-events-adbjson').debug(f"Completed - returning response")
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": f"Response: {resp}"}),
        headers={"Content-Type": "application/json"}
    )
