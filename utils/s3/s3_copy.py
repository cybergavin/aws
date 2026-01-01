import boto3
from botocore.exceptions import ClientError
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize S3 client once at module level
s3_client = boto3.client('s3')


def list_all_objects(bucket: str, prefix: str = '') -> list:
    """
    List all objects in an S3 bucket.
    
    Args:
        bucket: Bucket name
        prefix: Optional prefix to filter objects
        
    Returns:
        List of object keys
    """
    objects = []
    paginator = s3_client.get_paginator('list_objects_v2')
    
    try:
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects.append(obj['Key'])
                    
        logger.info(f"Found {len(objects)} objects in source bucket")
        return objects
        
    except ClientError as e:
        logger.error(f"Error listing objects: {e}")
        raise


def copy_object(source_bucket: str, dest_bucket: str, key: str) -> bool:
    """
    Copy a single object from source to destination bucket.
    
    Args:
        source_bucket: Source bucket name
        dest_bucket: Destination bucket name
        key: Object key to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        copy_source = {'Bucket': source_bucket, 'Key': key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=key
        )
        logger.info(f"Successfully copied: {key}")
        return True
        
    except ClientError as e:
        logger.error(f"Error copying {key}: {e}")
        return False


def copy_bucket(
    source_bucket: str,
    dest_bucket: str,
    prefix: str = '',
    max_workers: int = 10,
    dry_run: bool = False
) -> dict:
    """
    Copy all objects from source to destination bucket while retaining paths.
    
    Args:
        source_bucket: Source bucket name
        dest_bucket: Destination bucket name
        prefix: Optional prefix to filter objects
        max_workers: Number of parallel threads
        dry_run: If True, only list objects without copying
        
    Returns:
        Dictionary with copy statistics
    """
    logger.info(f"Starting copy from {source_bucket} to {dest_bucket}")
    
    # List all objects
    objects = list_all_objects(source_bucket, prefix)
    
    if not objects:
        logger.warning("No objects found to copy")
        return {'total': 0, 'success': 0, 'failed': 0}
    
    if dry_run:
        logger.info(f"DRY RUN: Would copy {len(objects)} objects")
        for obj in objects:
            logger.info(f"  - {obj}")
        return {'total': len(objects), 'success': 0, 'failed': 0, 'dry_run': True}
    
    # Copy objects in parallel
    success_count = 0
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(copy_object, source_bucket, dest_bucket, key): key 
            for key in objects
        }
        
        for future in as_completed(futures):
            try:
                if future.result():
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                failed_count += 1
    
    stats = {
        'total': len(objects),
        'success': success_count,
        'failed': failed_count
    }
    
    logger.info(f"Copy complete: {stats}")
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='Copy all objects from source S3 bucket to destination bucket while retaining prefix paths.'
    )
    
    parser.add_argument(
        'source_bucket',
        help='Source S3 bucket name'
    )
    
    parser.add_argument(
        'destination_bucket',
        help='Destination S3 bucket name'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='List objects that would be copied without actually copying them'
    )
    
    parser.add_argument(
        '--prefix',
        default='',
        help='Only copy objects with this prefix (optional)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=10,
        help='Number of parallel copy threads (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Execute copy
    stats = copy_bucket(
        source_bucket=args.source_bucket,
        dest_bucket=args.destination_bucket,
        prefix=args.prefix,
        max_workers=args.max_workers,
        dry_run=args.dry_run
    )
    
    print(f"\nFinal statistics: {stats}")


if __name__ == '__main__':
    main()