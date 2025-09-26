###############################################################################
# Script to empty an S3 bucket including all object versions and delete markers
# Skips objects locked under Object Lock (Compliance or Governance)
# Usage: python empty_s3_bucket.py <bucket-name>
###############################################################################
import boto3
from botocore.exceptions import ClientError

def empty_bucket(bucket_name):
    s3_client = boto3.client("s3")

    while True:
        versions_to_delete = []
        locked_objects = []

        paginator = s3_client.get_paginator("list_object_versions")
        for page in paginator.paginate(Bucket=bucket_name):
            # Collect object versions
            for v in page.get("Versions", []):
                if is_locked(s3_client, bucket_name, v["Key"], v["VersionId"]):
                    locked_objects.append((v["Key"], v["VersionId"]))
                else:
                    versions_to_delete.append(
                        {"Key": v["Key"], "VersionId": v["VersionId"]}
                    )

            # Collect delete markers
            for m in page.get("DeleteMarkers", []):
                if is_locked(s3_client, bucket_name, m["Key"], m["VersionId"]):
                    locked_objects.append((m["Key"], m["VersionId"]))
                else:
                    versions_to_delete.append(
                        {"Key": m["Key"], "VersionId": m["VersionId"]}
                    )

        if not versions_to_delete and not locked_objects:
            print(f"✅ Bucket {bucket_name} is already empty.")
            return

        confirm = input(
            f"About to permanently delete {len(versions_to_delete)} objects "
            f"(and skip {len(locked_objects)} locked objects) from '{bucket_name}'. Proceed? [y/N]: "
        ).strip().lower()
        if confirm != "y":
            print("Aborted by user.")
            return

        # Delete in chunks of 1000
        if versions_to_delete:
            print(f"Deleting {len(versions_to_delete)} objects from bucket {bucket_name} ...")
            try:
                for i in range(0, len(versions_to_delete), 1000):
                    chunk = versions_to_delete[i : i + 1000]
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={"Objects": chunk}
                    )
            except ClientError as e:
                print(f"Error deleting objects: {e}")
                return

        # Print locked summary
        if locked_objects:
            print(f"\n⚠️ Skipped {len(locked_objects)} locked objects:")
            for key, vid in locked_objects[:10]:  # show only first 10
                print(f"  {key} (VersionId={vid})")
            if len(locked_objects) > 10:
                print(f"  ... and {len(locked_objects) - 10} more")

        # Check if bucket is now empty (ignoring locked objects)
        remaining = 0
        for page in paginator.paginate(Bucket=bucket_name):
            remaining += len(page.get("Versions", [])) + len(page.get("DeleteMarkers", []))

        if remaining == len(locked_objects):
            print(f"\n✅ Bucket {bucket_name} emptied (except {len(locked_objects)} locked objects).")
            return
        else:
            print(f"\n{remaining} objects still remain (retrying ...)")


def is_locked(s3_client, bucket, key, version_id):
    """Check if a specific version is under Object Lock retention or legal hold."""
    try:
        resp = s3_client.get_object_retention(
            Bucket=bucket,
            Key=key,
            VersionId=version_id
        )
        if resp.get("Retention"):
            return True
    except ClientError as e:
        if e.response["Error"]["Code"] not in (
            "NoSuchObjectLockConfiguration",
            "InvalidRequest",
        ):
            raise

    try:
        resp = s3_client.get_object_legal_hold(
            Bucket=bucket,
            Key=key,
            VersionId=version_id
        )
        if resp.get("LegalHold", {}).get("Status") == "ON":
            return True
    except ClientError as e:
        if e.response["Error"]["Code"] not in (
            "NoSuchObjectLockConfiguration",
            "InvalidRequest",
        ):
            raise

    return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <bucket-name>")
        sys.exit(1)
    empty_bucket(sys.argv[1])
