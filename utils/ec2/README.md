## `extract_ec2_name.py`

### Overview

Extracts EC2 instance **Name tags** for a list of EC2 instance IDs and saves the results to a CSV file.

### What It Does

* Reads EC2 instance IDs from a text file
* Queries AWS EC2 for each instance’s `Name` tag
* Writes `InstanceId` → `Name` mappings to a CSV file
* Handles large lists by batching API calls (up to 1000 IDs per request)

### Requirements

* Python 3.x
* `boto3`
* AWS credentials configured (IAM role, environment variables, or AWS config files)
* EC2 `DescribeInstances` permission

### Input

* `instance_ids.txt`

  * One EC2 instance ID per line

### Output

* `instance_names.csv`

  * Columns:

    * `InstanceId`
    * `Name` (empty if no Name tag exists)

### Usage

```bash
python extract_ec2_name.py
```

### Configuration

* Default AWS region: `us-west-2`
* Input file: `instance_ids.txt`
* Output file: `instance_names.csv`

Modify these values in the `__main__` block if needed.

### Notes

* Instances without a `Name` tag will have a blank value in the CSV.
* The script assumes all instance IDs exist in the specified region.

---

## `list_ec2_instances.py`

### Overview

Lists all EC2 instances in a region and exports detailed metadata, including compute and storage information, to a CSV file. Optimized for large AWS environments.

### What It Does

* Retrieves all EC2 instances using pagination
* Collects:

  * Instance ID
  * Name tag
  * Private IP address
  * Instance type
  * vCPU count
  * Memory (MiB)
  * Total attached EBS disk size (GiB)
* Minimizes API calls by caching instance type data and batching volume queries

### Requirements

* Python 3.x
* `boto3`
* AWS credentials configured
* Required IAM permissions:

  * `ec2:DescribeInstances`
  * `ec2:DescribeInstanceTypes`
  * `ec2:DescribeVolumes`

### Output

* `ec2_instance_details.csv`

  * Columns:

    * `InstanceId`
    * `Name`
    * `PrivateIp`
    * `InstanceType`
    * `vCPUs`
    * `MemoryMiB`
    * `TotalDiskGiB`

### Usage

```bash
python list_ec2_instances.py
```

### Configuration

* Default region: `us-west-2`
* Output file: `ec2_instance_details.csv`

Both can be changed in the `__main__` block.

### Notes

* Disk size reflects the sum of all attached EBS volumes (root + data).
* Instances without a Name tag will have a blank `Name` field.
* If no instances are found, no CSV is written.
* Designed to scale efficiently in accounts with large instance counts.
