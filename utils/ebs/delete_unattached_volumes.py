#!/usr/bin/env python3
import boto3
from datetime import datetime, timezone, timedelta

# ===== CONFIGURATION =====
GRACE_PERIOD_DAYS = 7   # Only delete unattached volumes older than this
PROTECTED_TAG = "DoNotDelete"
REGION = "us-west-2"    # Or set via AWS_REGION env var
# =========================

ec2 = boto3.client("ec2", region_name=REGION)

def main():
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=GRACE_PERIOD_DAYS)

    # Find unattached (available) volumes
    volumes = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )["Volumes"]

    if not volumes:
        print("No unattached volumes found.")
        return

    for vol in volumes:
        vol_id = vol["VolumeId"]
        create_time = vol["CreateTime"]

        # Skip recent volumes within grace period
        if create_time > cutoff_time:
            print(f"Skipping {vol_id} (created {create_time}, within grace period).")
            continue

        # Check tags
        tags = {t["Key"]: t["Value"] for t in vol.get("Tags", [])}
        if tags.get(PROTECTED_TAG, "").lower() == "true":
            print(f"Skipping {vol_id} (tagged {PROTECTED_TAG}).")
            continue

        # Create snapshot
        desc = (
            f"Auto-snapshot before deletion of {vol_id} "
            f"({datetime.now(timezone.utc).isoformat()})"
        )
        try:
            snap = ec2.create_snapshot(VolumeId=vol_id, Description=desc)
            snap_id = snap["SnapshotId"]
            print(f"Snapshot {snap_id} creation started for {vol_id}.")

            # Wait for snapshot to complete
            waiter = ec2.get_waiter("snapshot_completed")
            print(f"Waiting for snapshot {snap_id} to complete...")
            waiter.wait(SnapshotIds=[snap_id])
            print(f"Snapshot {snap_id} completed.")

            # Tag snapshot for traceability
            ec2.create_tags(
                Resources=[snap_id],
                Tags=[{"Key": "SourceVolume", "Value": vol_id}]
            )

            # Delete volume after snapshot is confirmed complete
            ec2.delete_volume(VolumeId=vol_id)
            print(f"Deleted unattached volume {vol_id}.")

        except Exception as e:
            print(f"ERROR: Could not snapshot/delete {vol_id} → {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
