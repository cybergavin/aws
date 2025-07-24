# AMI Management Scripts

This folder contains scripts to manage Amazon Machine Images (AMIs) for EC2 instances backup and cleanup workflows. Designed for safe, repeatable use in automation or operational tasks.


## Prerequisites
- AWS CLI configured with appropriate permissions:
- Bash shell (tested with version 5.2.21)



## Scripts

### 🔹 `backup-instances-parallel.sh`

Creates AMI backups of multiple EC2 instances in parallel.

- Reads a list of instance names from a text file
- Stops running instances safely
- Creates bootable AMIs with specified prefix
- Waits for AMI creation to complete
- Restarts instances after backup

#### Usage:
```bash
chmod +x backup-instances-parallel.sh
./backup-instances-parallel.sh [--prefix <ami_prefix>] [--file <instances_file>] [--batch <max_parallel_jobs>]
```

### 🔹 `cleanup-ami.sh`

Deletes a specific AMI and its associated snapshots.

- Deregisters the given AMI
- Identifies and deletes all associated EBS snapshots

#### Usage:
```bash
chmod +x cleanup-ami.sh
./cleanup-ami.sh --ami-id <ami-xxxxxxxxxxxxxxxxx>
```
