###############################################################################
# Script to extract EC2 instance names from a list of instance IDs and save to CSV
# Usage: python extract_ec2_name.py
###############################################################################
import boto3
import csv

def get_instance_names(instance_ids, region_name="us-west-2"):
    """
    Retrieve EC2 instance names (from the 'Name' tag) for given instance IDs.
    Returns a dict mapping instance_id -> instance_name (or None if no Name tag).
    """
    ec2 = boto3.client("ec2", region_name=region_name)
    names = {}

    # AWS describe_instances allows up to 1000 instance IDs per call
    for i in range(0, len(instance_ids), 1000):
        batch = instance_ids[i:i + 1000]
        response = ec2.describe_instances(InstanceIds=batch)

        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instance_id = instance["InstanceId"]
                name = None
                for tag in instance.get("Tags", []):
                    if tag["Key"] == "Name":
                        name = tag["Value"]
                        break
                names[instance_id] = name

    return names


def read_instance_ids(file_path):
    """Read instance IDs from a file (one per line)"""
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def write_to_csv(data, output_file):
    """Write a dict of instance_id -> name to a CSV file"""
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["InstanceId", "Name"])
        for instance_id, name in data.items():
            writer.writerow([instance_id, name])


if __name__ == "__main__":
    file_path = "instance_ids.txt"      # Input file with instance IDs
    output_file = "instance_names.csv"  # Output CSV file

    instance_ids = read_instance_ids(file_path)
    instance_names = get_instance_names(instance_ids)
    write_to_csv(instance_names, output_file)

    print(f"Instance names saved to {output_file}")
