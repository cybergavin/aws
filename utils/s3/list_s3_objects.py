###############################################################################
# Script to list all object versions and delete markers in an S3 bucket
# and detect Object Lock retention
# Usage: python list_s3_objects.py <bucket-name>
###############################################################################
import boto3
from collections import Counter
from botocore.exceptions import ClientError

def list_versions(bucket_name):
    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator("list_object_versions")
    page_iterator = paginator.paginate(Bucket=bucket_name)

    versions_count = 0
    markers_count = 0
    locked_count = 0
    key_counter = Counter()

    print(f"Bucket: {bucket_name}\n")

    for page in page_iterator:
        for v in page.get("Versions", []):
            versions_count += 1
            key_counter[v["Key"]] += 1

            try:
                resp = s3_client.get_object_retention(
                    Bucket=bucket_name,
                    Key=v["Key"],
                    VersionId=v["VersionId"]
                )
                retention = resp.get("Retention")
                if retention:
                    locked_count += 1
                    mode = retention["Mode"]
                    until = retention["RetainUntilDate"]
                    print(
                        f"LOCKED ({mode})  Key={v['Key']}  "
                        f"VersionId={v['VersionId']}  Until={until}"
                    )
            except ClientError as e:
                # Ignore if bucket has no object lock config or version not locked
                if e.response["Error"]["Code"] not in (
                    "NoSuchObjectLockConfiguration",
                    "InvalidRequest",
                ):
                    raise

        for m in page.get("DeleteMarkers", []):
            markers_count += 1
            key_counter[m["Key"]] += 1

    total_entries = versions_count + markers_count
    print("\nSummary:")
    print(f"  Total object versions : {versions_count}")
    print(f"  Total delete markers  : {markers_count}")
    print(f"  Total entries (all)   : {total_entries}")
    print(f"  Total locked objects  : {locked_count}")

    if total_entries == 0:
        print("\n✅ Bucket has no versions or delete markers.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <bucket-name>")
        sys.exit(1)
    list_versions(sys.argv[1])
