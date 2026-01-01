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

### 3. `s3_copy.py`
- Copies all objects from a source S3 bucket to a destination bucket while retaining their prefix paths.
- Supports pagination for buckets with large numbers of objects.
- Uses parallel threading for efficient copying of multiple objects.
- Includes dry-run mode to preview what will be copied without executing the operation.
- Usage:
```bash
  # Dry run to preview objects that would be copied
  python s3_copy.py source-bucket destination-bucket --dry-run
  
  # Copy all objects
  python s3_copy.py source-bucket destination-bucket
  
  # Copy only objects with a specific prefix
  python s3_copy.py source-bucket destination-bucket --prefix folder/subfolder/
  
  # Use more parallel workers for faster copying
  python s3_copy.py source-bucket destination-bucket --max-workers 20