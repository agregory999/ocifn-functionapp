import io
import json
import logging

from fdk import response


def handler(ctx, data: io.BytesIO = None):
    logging.getLogger("oci-serviceconnector-process-events").setLevel(logging.INFO)
    try:
        body = json.loads(data.getvalue())
        logging.getLogger("oci-serviceconnector-process-events").debug("List as JSON: " + str(body))
        logging.getLogger("oci-serviceconnector-process-events").info(f"Metrics received: {len(body)}")
        
        # Parse JSON List
        for item in body:
            # Each item looks like this
            # {"namespace":"oci_computeagent",
            #  "resourceGroup":null,
            #  "compartmentId":"ocid1.compartment.oc1..aaaaaaaa56cet4engnkah7pnrtljo3h55slitvhpmln4lpsi7toeri3qoeqq",
            #  "name":"NetworksBytesIn",
            #  "dimensions":{"instancePoolId":"Default",
            #                "resourceDisplayName":"stuff",
            #                "faultDomain":"FAULT-DOMAIN-1",
            #                "resourceId":"ocid1.instance.oc1.iad.anuwcljrytsgwaycm37hliihvwqk7cqp5ko6vdyemj66i47zm3n7iuvkliza",
            #                "availabilityDomain":"UWQV:US-ASHBURN-AD-1",
            #                "imageId":"ocid1.image.oc1.iad.aaaaaaaapcf3o54qeigj22nowwdtceyepisigpz3fho67l3xm7lmqkrgb62q",
            #                "region":"us-ashburn-1",
            #                "shape":"VM.Standard.E4.Flex"},
            #  "metadata":{"displayName":"Network Receive Bytes",
            #              "unit":"Bytes"},
            #  "datapoints":[{"timestamp":1665673151004,"value":1410196.0,"count":1},
            #                {"timestamp":1665673161009,"value":1410262.0,"count":1},
            #                {"timestamp":1665673171010,"value":1410422.0,"count":1},
            #                {"timestamp":1665673181000,"value":1410648.0,"count":1},
            #                {"timestamp":1665673191009,"value":1410804.0,"count":1},
            #                {"timestamp":1665673201010,"value":1411020.0,"count":1}]
            # }
            ns = item['namespace']
            vmname = item['dimensions']['resourceDisplayName']

            # Post value to Nagios endpoint
            logging.getLogger("oci-serviceconnector-process-events").info(f"NS: {ns} VM: {vmname}")
            
    except (Exception, ValueError) as ex:
        logging.getLogger("oci-serviceconnector-process-events").error('error parsing json payload: ' + str(ex))

    return