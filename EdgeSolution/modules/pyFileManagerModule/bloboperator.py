# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os, uuid
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__

import time

class BlobOperator:
    """Class for Blob operations
    """

    def __init__(self, connstring):
        """Initialize the class

        Args:
        """
        self.connstring = connstring

    def generate_file_with_content(self, filenamewithpath,size):
        """Generate a file of specified name and size in MiB

        Args:
            filename (str): Name of the file with path to create
            size (int): size of the file in MiB
        """


        print("\nGenerating {} of size {}".format(filenamewithpath,size))

        t0 = time.time()
        file = open(filenamewithpath, "wb")
        #1MB = 1000000 Bytes
        chunk="a"*(size*1048576)
        file.write(bytes(chunk, 'utf-8'))
        d = time.time() - t0
        print ("file generation duration: {}s".format(d))
        file.close
        return True

    def addfile(self, filename, size ):
        """Add a file of specified size on Local Edge Blob

        Args:
            filename (str): Name of thee file to create
            size (int): size of the file in MiB
        """

        # Create a file in the local data directory to upload and download
        upload_file_path = os.path.join(os.environ.get("FILEMANAGER_EDGE_ROOT"), filename)

        if  self.generate_file_with_content(upload_file_path,size) == True :
            blob_service_client = BlobServiceClient.from_connection_string(self.connstring)
            blob_client = blob_service_client.get_blob_client(container=os.environ.get("EDGE_BLOB_CONTAINER_NAME"), blob=filename)
            print("\nUploading to Azure Blob Storage on Edge as blob:\n\t" + filename)
            # Upload the created file
            with open(upload_file_path, "rb") as data:
                blob_client.upload_blob(data)
            print("\nDONE Uploading to Azure Blob Storage on Edge as blob:\n\t" + filename)
            return True
        else:
            return False

