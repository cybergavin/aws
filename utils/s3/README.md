# S3 Utilities

## 📜 Scripts

### 1. `list_s3_objects.py`
- Lists all object versions and delete markers in an S3 bucket.
- Summarizes counts by object type, including locked objects (Object Lock) with compliance mode.
- Usage:
  ```bash
  python list_s3_objects.py <bucket-name>
  ```

### 2. `empty_s3_bucket.py`
- Supports buckets with versioning enabled.
- Empties an S3 bucket by deleting all objects and versions (including delete markers).
- Lists objects that cannot be deleted due to object lock.
- Usage:
  ```bash
  python empty_s3_bucket.py <bucket-name>
  ```