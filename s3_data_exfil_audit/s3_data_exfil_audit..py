import time
import sys
import csv
import json
from pathlib import Path, PurePath
import boto3
from config import *


# Validate input arguments
if len(sys.argv) != 2:
    print(f"\nMissing input argument!\nUSAGE: python3 {sys.argv[0]} <file name>\nwhere <file name> is the name of the file containing a single column of authorized AWS Account IDs.\n")
    exit(1)

accounts = sys.argv[1]
script_dir = Path((PurePath(sys.argv[0]).parent)).resolve(strict=True)
results_json = script_dir / f'{PurePath(accounts).stem}_s3audit.json'
results_csv = script_dir / f'{PurePath(accounts).stem}_s3audit.csv'

# Create CloudTrail client
client = boto3.client('cloudtrail')

# Prepare CloudTrail Lake Query
cloudtrail_lake_query = (f"SELECT eventTime, eventSource, sourceIPAddress, eventName, element_at(requestParameters, 'bucketName') AS DestinationBucket, userIdentity.accountid AS SourceAccountID, element_at(resources,2).accountid AS RecipientAccountID" # Select specific columns from event data store
                         f" FROM {event_data_store_id}" 
                         f" WHERE eventTime > '{event_time_filter}'"
                         f" AND eventName IN ('PutObject','CopyObject','CreateMultipartUpload','UploadPart','UploadPartCopy','CompleteMultipartUpload','PostObject')" # check data exfiltration to S3
                         f" ORDER BY eventTime DESC"
                         )

# Execute CloudTrail Lake Query
start_query = client.start_query(QueryStatement=cloudtrail_lake_query)
query_id = start_query['QueryId']

# Wait for query execution to complete
while client.get_query_results(QueryId=query_id)['QueryStatus'] != "FINISHED":
    time.sleep(1)

# Write query results to JSON file - don't need this step, but useful for analysis/troubleshooting
with open(results_json,'w') as rj:
    data = client.get_query_results(QueryId=query_id)
    rj.write(json.dumps(data))

# Read list of authorized AWS Account IDs
with open(accounts,'r') as a:
    a_list = a.read().splitlines()

# Parse query results and extract data for unauthorized AWS Account IDs in CSV format
with open(results_csv,'w',newline='') as r:
    writer = csv.writer(r)
    writer.writerow(["eventTime","eventSource","sourceIPAddress","eventName","DestinationBucket","SourceAccountID","RecipientAccountID"])
    for qrr in data['QueryResultRows']:
        for qr in qrr:
            if "RecipientAccountID" in qr and qr['RecipientAccountID'] not in a_list:
                writer.writerow([qrr[0]['eventTime'],qrr[1]['eventSource'],qrr[2]['sourceIPAddress'],qrr[3]['eventName'],qrr[4]['DestinationBucket'],qrr[5]['SourceAccountID'],qrr[6]['RecipientAccountID']])
