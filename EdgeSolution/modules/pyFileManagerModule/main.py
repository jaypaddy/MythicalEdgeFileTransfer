# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import Message
from azure.iot.device import MethodRequest
from azure.iot.device import MethodResponse
import json
from bloboperator import BlobOperator
import datetime


async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        async def addfile(fileinfo):
            filename = fileinfo["name"]
            filesize = fileinfo["size"]
            edgeblobconnstring = os.environ.get("EDGE_BLOB_CONNSTRING")
            bloboperator = BlobOperator(edgeblobconnstring)
            bloboperator.addfile(filename, filesize)
            return

        # define behavior for receiving an input message on input1
        async def input1_message_handler(input_message):
            return

        # define behavior for receiving an method message on method
        async def method_request_handler(method_request):
            print("Direct Method Call Received...")
            # Determine how to respond to the method request based on the method name
            if method_request.name == "AddFile":
                payload = {"result": True, "data": "some data"}  # set response payload
                status = 200  # set return status code
                print("executed AddFile")
            else:
                payload = {"result": False, "data": "unknown method"}  # set response payload
                status = 400  # set return status code
                print("executed unknown method: " + method_request.name)
                
            # Send the response
            method_response = MethodResponse.create_from_method_request(method_request, status, payload)
            await module_client.send_method_response(method_response)

            if method_request.name == "AddFile":
                #method_request.payload is dict that contains the JSON payload being sent with the request.
                await addfile(method_request.payload)

        # set the message handler on the client
        module_client.on_message_received = input1_message_handler
        module_client.on_method_request_received = method_request_handler

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        print ( "The sample is now waiting for messages. ")
        print(os.environ.get("EDGE_BLOB_CONNSTRING"))

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished


        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    asyncio.run(main())