#!/usr/bin/env python3
import boto3
import argparse
import csv
from datetime import datetime, timezone, timedelta
from tabulate import tabulate

def list_unattached_volumes(grace_days: int, protected_tag: str) -> list[dict]:
    """
    List unattached EBS volumes that are older than the grace period,
    not protected by a tag, and classify into patterns.
    """
    ec2 = boto3.client("ec2")
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=grace_days)

    paginator = ec2.get_paginator("describe_volumes")
    page_iterator = paginator.paginate(Filters=[{"Name": "status", "Values": ["available"]}])

    results = []
    for page in page_iterator:
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

            # Skip protected volumes
            tags = {t["Key"]: t["Value"] for t in vol.get("Tags", [])}
            if tags.get(protected_tag, "").lower() == "true":
                continue

            # Source snapshot analysis
            snapshot_id = vol.get("SnapshotId")
            snapshot_exists = False
            ami_copy_snapshot = False

            if snapshot_id:
                try:
                    snap = ec2.describe_snapshots(SnapshotIds=[snapshot_id])["Snapshots"][0]
                    snapshot_exists = True
                    desc = snap.get("Description", "").lower()
                    if "copied for" in desc and "ami" in desc:
                        ami_copy_snapshot = True
                except Exception:
                    snapshot_exists = False

            # Determine pattern
            if not attachments and not snapshot_id:
                pattern = "Pattern1"  # Never attached, no snapshot
            elif not attachments and snapshot_exists and ami_copy_snapshot:
                pattern = "Pattern2"  # Never attached, AMI copy snapshot
            else:
                pattern = "Other"

            results.append({
                "VolumeId": vol_id,
                "Size_GB": size,
                "AZ": az,
                "CreateTime": created.isoformat(),
                "LastInstance": last_instance or "None",
                "SnapshotId": snapshot_id or "None",
                "SnapshotExists": "Yes" if snapshot_exists else "No",
                "Pattern": pattern
            })

    # Sort newest first
    results.sort(key=lambda x: x["CreateTime"], reverse=True)
    return results

def tag_volumes(volumes):
    ec2 = boto3.client("ec2")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for vol in volumes:
        if vol["Pattern"] in ["Pattern1", "Pattern2"]:
            ec2.create_tags(
                Resources=[vol["VolumeId"]],
                Tags=[
                    {"Key": "SafeToDelete", "Value": "True"},
                    {"Key": "DeleteReason", "Value": vol["Pattern"]},
                    {"Key": "DeleteMarkedOn", "Value": now},
                ]
            )
            print(f"Tagged {vol['VolumeId']} as SafeToDelete ({vol['Pattern']})")

def delete_tagged_volumes():
    ec2 = boto3.client("ec2")
    paginator = ec2.get_paginator("describe_volumes")
    page_iterator = paginator.paginate(
        Filters=[{"Name": "tag:SafeToDelete", "Values": ["True"]},
                 {"Name": "status", "Values": ["available"]}]
    )

    for page in page_iterator:
        for vol in page["Volumes"]:
            vol_id = vol["VolumeId"]
            print(f"Deleting volume {vol_id}...")
            ec2.delete_volume(VolumeId=vol_id)

def output_table(volumes):
    if not volumes:
        print("No unattached volumes found.")
    else:
        print(tabulate(volumes, headers="keys", tablefmt="grid"))
        print("\nNOTE: LastInstance = None → the volume has never been attached.\n")
        # Totals
        total = len(volumes)
        pattern_counts = {}
        for v in volumes:
            pattern_counts[v["Pattern"]] = pattern_counts.get(v["Pattern"], 0) + 1

        print(f"Total unattached volumes: {total}")
        for pattern, count in pattern_counts.items():
            print(f"Total volumes - {pattern}: {count}")

def output_csv(volumes, filename="unattached_volumes.csv"):
    if not volumes:
        print("No unattached volumes found.")
        return
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=volumes[0].keys())
        writer.writeheader()
        writer.writerows(volumes)
    print(f"CSV output written to {filename}")
    # Totals
    total = len(volumes)
    pattern_counts = {}
    for v in volumes:
        pattern_counts[v["Pattern"]] = pattern_counts.get(v["Pattern"], 0) + 1

    print(f"Total unattached volumes: {total}")
    for pattern, count in pattern_counts.items():
        print(f"Total volumes - {pattern}: {count}")

def main():
    parser = argparse.ArgumentParser(description="Report and clean up unattached EBS volumes.")
    parser.add_argument("--grace-days", type=int, default=0,
                        help="Grace period in days (skip volumes younger than this).")
    parser.add_argument("--protected-tag", type=str, default="DoNotDelete",
                        help="Tag key to skip deletion (value must be 'true').")
    parser.add_argument("--output", choices=["table", "csv"], default="table",
                        help="Output format: table (default) or csv.")
    parser.add_argument("--csv-file", type=str, default="unattached_volumes.csv",
                        help="CSV filename if --output csv is chosen.")
    parser.add_argument("--tag-only", action="store_true",
                        help="Tag volumes safe to delete (Pattern1/Pattern2).")
    parser.add_argument("--delete-tagged", action="store_true",
                        help="Delete volumes previously tagged SafeToDelete=True.")

    args = parser.parse_args()

    if args.delete_tagged:
        delete_tagged_volumes()
        return

    volumes = list_unattached_volumes(args.grace_days, args.protected_tag)

    if args.tag_only:
        tag_volumes(volumes)

    if args.output == "table":
        output_table(volumes)
    else:
        output_csv(volumes, args.csv_file)

if __name__ == "__main__":
    main()
