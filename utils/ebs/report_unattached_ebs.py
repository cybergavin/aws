import boto3
import argparse
import csv
from datetime import datetime, timezone, timedelta
from tabulate import tabulate

def list_unattached_volumes(grace_days: int, protected_tag: str) -> list[dict]:
    """
    List unattached EBS volumes that are older than the grace period and not protected by a tag.
    Flags orphaned volumes, VM-Import snapshots, and AMI copy snapshots.
    """
    ec2 = boto3.client("ec2")
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=grace_days)

    paginator = ec2.get_paginator("describe_volumes")
    pages = paginator.paginate(Filters=[{"Name": "status", "Values": ["available"]}])

    results = []
    for page in pages:
        for vol in page["Volumes"]:
            vol_id = vol["VolumeId"]
            size = vol["Size"]
            az = vol["AvailabilityZone"]
            created = vol["CreateTime"]
            attachments = vol.get("Attachments", [])
            last_instance = attachments[-1]["InstanceId"] if attachments else None

            # Skip volumes within grace period
            if created > cutoff_time:
                continue

            # Skip volumes with protected tag
            tags = {t["Key"]: t["Value"] for t in vol.get("Tags", [])}
            if tags.get(protected_tag, "").lower() == "true":
                continue

            # Snapshot checks
            source_snap_id = vol.get("SnapshotId")
            snap_exists = "N/A"
            ami_copy = "No"

            if source_snap_id:
                try:
                    snap = ec2.describe_snapshots(SnapshotIds=[source_snap_id])["Snapshots"][0]
                    snap_exists = "Yes"
                    desc = snap.get("Description", "").lower()

                    # if "vm import" in desc or "import-ami" in desc:
                    #     vm_import = "Yes"
                    if "copied for destinationami" in desc:
                        ami_copy = "Yes"

                except ec2.exceptions.ClientError as e:
                    if "InvalidSnapshot.NotFound" in str(e):
                        snap_exists = "No"
                    else:
                        snap_exists = "Unknown"

            # Determine if truly orphaned
            orphaned =  ((last_instance is None and snap_exists == "No") or
                (last_instance is None and snap_exists == "Yes" and ami_copy == "Yes"))
            

            results.append({
                "VolumeId": vol_id,
                "Size_GB": size,
                "CreateTimeRaw": created,
                "LastInstance": last_instance or "None",
                "SourceSnapshotId": source_snap_id or "None",
                "SnapshotExists": snap_exists,
                "AMICopySnapshot": ami_copy,
                "Orphaned": "Yes" if orphaned else "No"
            })
    
    # Sort results by creation time
    results.sort(key=lambda x: x["CreateTimeRaw"], reverse=True)  # sort descending by datetime

    # Convert datetime back to ISO string for display/CSV
    for r in results:
        r["CreateTime"] = r["CreateTimeRaw"].isoformat()
        del r["CreateTimeRaw"]
    return results



def output_table(volumes):
    if not volumes:
        print("No unattached volumes found.")
        return

    print(tabulate(volumes, headers="keys", tablefmt="grid"))
    print("\nNOTE:")
    print(" - LastInstance = None → volume has never been attached")
    print(" - Orphaned = Yes → safe to delete without affecting AMIs or snapshots\n")
    print(f"Total unattached volumes: {len(volumes)}")
    orphan_count = sum(1 for v in volumes if v["Orphaned"] == "Yes")
    print(f"Truly orphaned volumes: {orphan_count}")

def output_csv(volumes, filename="unattached_volumes.csv"):
    if not volumes:
        print("No unattached volumes found.")
        return
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=volumes[0].keys())
        writer.writeheader()
        writer.writerows(volumes)
    print(f"CSV output written to {filename}")
    print(f"Total unattached volumes: {len(volumes)}")
    orphan_count = sum(1 for v in volumes if v["Orphaned"] == "Yes")
    print(f"Truly orphaned volumes: {orphan_count}")

def main():
    parser = argparse.ArgumentParser(description="Report unattached EBS volumes.")
    parser.add_argument("--grace-days", type=int, default=0,
                        help="Grace period in days (skip volumes younger than this).")
    parser.add_argument("--protected-tag", type=str, default="DoNotDelete",
                        help="Tag key to skip deletion (value must be 'true').")
    parser.add_argument("--output", choices=["table", "csv"], default="table",
                        help="Output format: table (default) or csv.")
    parser.add_argument("--csv-file", type=str, default="unattached_volumes.csv",
                        help="CSV filename if --output csv is chosen.")

    args = parser.parse_args()

    volumes = list_unattached_volumes(args.grace_days, args.protected_tag)

    if args.output == "table":
        output_table(volumes)
    else:
        output_csv(volumes, args.csv_file)

if __name__ == "__main__":
    main()
