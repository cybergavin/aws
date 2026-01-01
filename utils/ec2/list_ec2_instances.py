###############################################################################
# Script to list EC2 instances with details including vCPUs, Memory, and Disk
# Optimized for large environments
# Usage: python list_ec2_instances.py
###############################################################################
import boto3
import csv
from collections import defaultdict

def list_instances(region_name="us-east-1"):
    """
    Retrieve EC2 instance details including:
    InstanceId, Name, PrivateIp, InstanceType, vCPUs, MemoryMiB, TotalDiskGiB
    Optimized for large environments.
    """
    ec2 = boto3.client("ec2", region_name=region_name)

    instances = []
    instance_type_cache = {}
    volume_map = {}

    # --- Step 1: Get all instances ---
    paginator = ec2.get_paginator("describe_instances")
    all_instances = []
    for page in paginator.paginate():
        for reservation in page.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                all_instances.append(instance)

    if not all_instances:
        return []

    # --- Step 2: Collect unique instance types and volume IDs ---
    instance_types = set()
    volume_ids = []
    for instance in all_instances:
        instance_types.add(instance["InstanceType"])
        for bd in instance.get("BlockDeviceMappings", []):
            if "Ebs" in bd:
                volume_ids.append(bd["Ebs"]["VolumeId"])

    # --- Step 3: Fetch instance type attributes in bulk ---
    for itype in instance_types:
        resp = ec2.describe_instance_types(InstanceTypes=[itype])
        if resp["InstanceTypes"]:
            info = resp["InstanceTypes"][0]
            instance_type_cache[itype] = {
                "vCPUs": info["VCpuInfo"]["DefaultVCpus"],
                "MemoryMiB": info["MemoryInfo"]["SizeInMiB"]
            }

    # --- Step 4: Fetch all volumes in batches ---
    for i in range(0, len(volume_ids), 500):  # API limit is 500
        batch = volume_ids[i:i+500]
        resp = ec2.describe_volumes(VolumeIds=batch)
        for vol in resp["Volumes"]:
            volume_map[vol["VolumeId"]] = vol["Size"]

    # --- Step 5: Build instance records ---
    for instance in all_instances:
        instance_id = instance["InstanceId"]
        private_ip = instance.get("PrivateIpAddress")
        instance_type = instance["InstanceType"]

        # Name tag
        name = None
        for tag in instance.get("Tags", []):
            if tag["Key"] == "Name":
                name = tag["Value"]
                break

        # vCPUs and Memory from cache
        type_info = instance_type_cache.get(instance_type, {})
        vcpus = type_info.get("vCPUs")
        memory_mib = type_info.get("MemoryMiB")

        # Sum disk sizes
        total_disk_gb = 0
        for bd in instance.get("BlockDeviceMappings", []):
            vol_id = bd.get("Ebs", {}).get("VolumeId")
            if vol_id and vol_id in volume_map:
                total_disk_gb += volume_map[vol_id]

        instances.append({
            "InstanceId": instance_id,
            "Name": name,
            "PrivateIp": private_ip,
            "InstanceType": instance_type,
            "vCPUs": vcpus,
            "MemoryMiB": memory_mib,
            "TotalDiskGiB": total_disk_gb
        })

    return instances


def write_to_csv(instances, output_file):
    """Write list of instance dicts to a CSV file."""
    if not instances:
        print("No instances found.")
        return

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=instances[0].keys())
        writer.writeheader()
        writer.writerows(instances)


if __name__ == "__main__":
    region = "us-west-2"                  # Change as needed
    output_file = "ec2_instance_details.csv"

    instances = list_instances(region)
    write_to_csv(instances, output_file)

    print(f"Saved {len(instances)} instances to {output_file}")
