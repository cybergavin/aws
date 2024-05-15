# Auditing S3 Data exfiltration

The script `s3-data-exfil-audit.py` uses [CloudTrail Lake](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-lake.html) to audit all S3 API calls that result in transferring data from your AWS account to an **external S3 bucket** (in an unauthorized/unknown AWS account). A list of authorized AWS accounts is provided in the file `accounts.txt`.

# Usage

## STEP 1: CloudTrail Lake setup

Create a CloudTrail Lake [event data store](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/query-event-data-store-cloudtrail.html) for your AWS Organization or account, as required and configure the data store to receive S3 data events.


## STEP 2: Authorized accounts setup

Edit the file `accounts.txt` and add a list of authorized AWS accounts.


## STEP 3: Update config

Update the file `config.py` with the appropriate CloudTrail Lake event_data_store_id and event_time_filter.

## STEP 4: Execute script

```
python s3-data-exfil-audit.py accounts.txt
```

**NOTE:** The script has been tested with python 3.9