import io
import oci
import logging
import json
from cloudevents.http import CloudEvent
from cloudevents.conversion import to_binary, to_structured, to_dict

ENDPOINT = "https://crra7b67hza.us-ashburn-1.functions.oci.oraclecloud.com"

logging.getLogger('ocifn-events-generate').info(f"Start")

# Populate Event Spec
attributes = {}
attributes["source"] = "FSS"
attributes["type"] = "backup"
data = {}
data["resourceName"] = "Some-FSS"
extensions = {}
extensions["compartmentId"] ="123"
event = CloudEvent(attributes, data)
event["extensions"] = extensions
# Creates the HTTP request representation of the CloudEvent in structured content mode
#headers, body = to_structured(event) 
#headers, body = to_binary(event) 

full_event = to_dict(event)
print (event, flush=True)
logging.getLogger('ocifn-events-generate').info(f"Event JSON: {event}")

# Invoke OCI
config = oci.config.from_file()
functions_client = oci.functions.FunctionsInvokeClient(config=config, service_endpoint=ENDPOINT)
invoke_function_response = functions_client.invoke_function(
    function_id="ocid1.fnfunc.oc1.iad.aaaaaaaa5szzbujwi46p3balukkd2og5zterdayq2v2ldw6ljjtu3ja2dota",
    invoke_function_body=json.dumps(full_event),
    fn_intent="httprequest",
    fn_invoke_type="sync",
    
    )

# Get the data from response
print(invoke_function_response.data)