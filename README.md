1.  Create a Storage Account
2.  Assign an Acct Name and Key for Blob Storage on Edge in .env
    *   EDGE_STORAGEACCT_NAME
    *   EDGE_STORAGEACCT_KEY
3.  On Edge create a directory for Files
    *   mythicalstore
4.  Assign permissions for absie (11000) - the userid use by Azure Blob Store
    *   sudo chown -R 11000:11000 ./mythicalstore
    *   sudo chmod -R 700 ./mythicalstore
5.  Add desired properties for Azure Blob Storage on Edge Module
6.  On Edge create a directory as in ${FILEMANAGER_BIND_MOUNT}
7.  Assign permissions for ${FILEMANAGER_USERID_GROUPID}
    *   sudo chown -R 12000:0 ./filemanager
    *   sudo chmod -R 700 ./filemanager


### Send File from Edge to Cloud
This is implemented as a Direct Method
1.  Initiate a Direct Method call to pyFileManagerModule
    *   Method: Add
    *   Payload: {"name":"<FILENAME>", "size":<SIZE IN MiB>}
        *   examples
            *   100MiB {"name":"100MiB.txt", "size":100}
            *   200MiB {"name":"200MiB.txt", "size":200}
2.  On EdgeModule receiving the call, it acknowledges receipt to IoTHub
3.  Generates a File of specified size and name on the local mounted directory ${FILEMANAGER_BIND_MOUNT}
4.  Establishes a connection to Azure Blob Storage on Edge. Connection String to Blob on Edge is injected via ENV
5.  Writes Blob to Azure Blob Storage Container on Edge : EDGE_BLOB_CONTAINER_NAME

### Send File from Cloud to Edge
1. An Azure Blob Trigger Function subscribing to Blob triggers
2. Azure function creates a SAS for the blob and sends to Edge the SAS_URL
3. Edge Module receives the SAS_URL and downloads the blob to local machine

### Create a AzureVM with IoTEdgee 1.2.0
`az deployment group create \
  --resource-group MythicalNestedEdge_RG \
  --template-uri "https://raw.githubusercontent.com/Azure/iotedge-vm-deploy/1.2.0/edgeDeploy.json" \
  --parameters dnsLabelPrefix='mythicalft' \
  --parameters adminUsername='azureuser' \
  --parameters authenticationType='sshPublicKey' \
  --parameters adminPasswordOrKey="$(< ~/.ssh/id_rsa.pub)" \
  --query "properties.outputs.[publicFQDN.value, publicSSH.value]" -o tsv
  `