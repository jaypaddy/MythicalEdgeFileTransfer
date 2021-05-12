import logging
import azure.functions as func
import os
import datetime
import json
import time
import datetime
import requests

from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient
from datetime import datetime, timedelta
from azure.storage.blob import BlobClient, generate_blob_sas, BlobSasPermissions



###
# Opportunity to think of this as an Event Based Data Processing pipeline. Such as
# Plugins with Durable Functions
# Durable pipelines using Servicee Bus Queues
# Event driven Architecture
# Etc.
# ####
# In this case this function will trigger a DirectMethod to the specified Edge and Module


class EdgeConnector:
    """Class for Edge Connector
    """    
    def __init__(self, deviceid, iothubname, moduleid):
        super().__init__()
        self.deviceid = deviceid
        self.moduleid = moduleid
        self.iothubname = iothubname
    
    def NotifyCloud2EdgeBlobCreate(self, blob_info, iothubmethod_info):
            # Get SAS Token for IoTHub
        sas_string=dict({"token":iothubmethod_info["iothubsastoken"]})
        headers = {'Content-type': 'application/json',
                    'Authorization': sas_string["token"]
                    }
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("%m/%d/%Y, %H:%M:%S", named_tuple)
        message_json = json.dumps(blob_info)
        payload_json = json.dumps(dict({
                    "methodName": iothubmethod_info["methodName"],
                    "responseTimeoutInSeconds": iothubmethod_info["responseTimeoutInSeconds"],
                    "payload": message_json
                }))
        url = "https://{}.azure-devices.net/twins/{}/modules/{}/methods?api-version={}" \
                        .format(self.iothubname, \
                        self.deviceid, \
                        self.moduleid, \
                        os.getenv('APIVERSION') )
        r = requests.post( url, data=payload_json, headers=headers, verify=False)
        logging.info(r.content)
        return r.content


def get_blob_sas(account_name,account_key, container_name, blob_name):
    sas_blob = generate_blob_sas(account_name=account_name, 
                                container_name=container_name,
                                blob_name=blob_name,
                                account_key=account_key,
                                permission=BlobSasPermissions(read=True),
                                expiry=datetime.utcnow() + timedelta(hours=1))
    return sas_blob




def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    

    logging.info('blobname: %s', myblob.name)
    #split blob.name into container and blob name
    #hardcoded to work with onee level of directory... should be adapted as needed
    splitstring = myblob.name.split("/",1)
    blobname =splitstring[1]


    edgeConn = EdgeConnector(os.environ["EDGE_DEVICEID"], os.environ["IOTHUB_NAME"],os.environ["EDGE_MODULEID"])


    blobsas = get_blob_sas( os.environ["STORAGEACCT_NAME"],
                            os.environ["STORAGEACCT_KEY"], 
                            os.environ["CLOUD_CONTAINERNAME"], 
                            blobname)
    blobsas_url = "https://{}.blob.core.windows.net/{}/{}?{}".format(
                        os.environ["STORAGEACCT_NAME"],os.environ["CLOUD_CONTAINERNAME"],
                        blobname,blobsas)


    #sas_url = "https://account.blob.core.windows.net/container/blob-name?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D"

    blob_info = {
                    "blobname" : blobname,
                    "size" : 0,
                    "hash" : "verification signature",
                    "blobsas_url": blobsas_url
    }

    iothubmethod_info = {
                    "iothubsastoken" : os.getenv("IOTHUB_SAS_TOKEN"),
                    "methodName": os.getenv('METHODNAME'),
                    "responseTimeoutInSeconds": os.getenv('TIMEOUT_SECS'),
    }
    edgeConn.NotifyCloud2EdgeBlobCreate(blob_info, iothubmethod_info)

