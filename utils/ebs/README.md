# EBS Utilities

This folder contains utilities for **detecting, reporting, and safely deleting unattached (orphaned) AWS EBS volumes**.  
Unattached volumes can accumulate over time, leading to unnecessary AWS costs. These scripts help identify and clean them up safely.

---

## 📂 Contents

- **`delete_unattached_volumes.py`**  
  Python script to:
  - Find unattached (`available`) EBS volumes.
  - Skip recently created volumes (grace period configurable).
  - Skip volumes tagged with `DoNotDelete=true` or any custom tag.
  - Create a snapshot before deletion (for recovery).
  - Delete the volume after successful snapshot.

- **`report_unattached_ebs.py`**  
  Python reporting script with options to:
  - List unattached EBS volumes.
  - Apply a grace period filter.
  - Skip `DoNotDelete=true` or custom tagged volumes.
  - Output results in a **table** (default) or **CSV** file.

- **`report_unattached_ebs.sh`**  
  Bash script using **AWS CLI** for quick reporting of unattached EBS volumes.  
  Useful for users without Python dependencies.

---

## ⚙️ Requirements

- **AWS Authentication**
  - AWS credentials configured (via environment, `~/.aws/credentials`, or IAM role). Using [`saml2aws`](https://usc-its-jira-cloud.atlassian.net/wiki/spaces/testcsetea/pages/2197717039/HOW-TO+Use+AWS+CLI+SSO+with+Shibboleth) is recommended.

- **Python scripts (`.py`)**
  - Python 3.8+
  - [`boto3`](https://pypi.org/project/boto3/)
  - [`tabulate`](https://pypi.org/project/tabulate/) (for table output in `report_unattached_ebs.py`)

- **Shell script (`.sh`)**
  - AWS CLI v2

---

## 🚀 Usage

### 1. Report unattached volumes (Python)

```bash
# Basic report in table format
python3 report_unattached_ebs.py

# Report with grace period of 7 days
python3 report_unattached_ebs.py --grace-days 7

# Report to CSV
python3 report_unattached_ebs.py --output csv --csv-file my_volumes.csv
```

Example Output:
```markdown
+------------+---------+-------------+----------------------------+---------------+
| VolumeId   | Size_GB | AZ          | CreateTime                 | LastInstance  |
+============+=========+=============+============================+===============+
| vol-012345 |     100 | us-west-2a  | 2025-08-15T18:25:43+00:00  | None          |
+------------+---------+-------------+----------------------------+---------------+

NOTE: LastInstance = None → the volume has never been attached.

Total unattached volumes: 1
```

### 2. Report unattached volumes (Shell / AWS CLI)

```bash
./report_unattached_ebs.sh
```

### 3. Delete unattached volumes safely

```bash
# Delete volumes older than 7 days (default in script)
python3 delete_unattached_volumes.py
```

####  What it does:

- Finds unattached (available) volumes.
- Skips:
    - Volumes created within the grace period (default: 7 days).
    - Volumes tagged with DoNotDelete=true.
- Creates a snapshot before deletion.
- Tags the snapshot with the original SourceVolume.
- Deletes the volume.

---
## 🔒 Safety Mechanisms

- **Grace period:** Prevents accidental deletion of recently created volumes.
- **Protected tag:** Volumes tagged with DoNotDelete=true or a custom tag are never deleted.
- **Automatic snapshot:** Every deleted volume is snapshotted first for rollback.

---
⚠️ Caution

- Some of these utilities **delete** AWS resources.
- Use with caution and test in non-production environments first.