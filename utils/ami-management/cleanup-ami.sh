#!/bin/bash
# Deletes a specific AMI and its associated snapshots.
# Usage: ./cleanup-ami.sh --ami-id <ami-xxxxxxxxxxxxxxxxx>
# Ensure you have the AWS CLI configured with appropriate permissions.
###############################################################################################
# Usage Function
function usage() {
  echo "Usage: $0 --ami-id <ami-xxxxxxxxxxxxxxxxx>"
  echo ""
  echo "  --ami-id   The ID of the AMI to delete and clean up its snapshots"
  exit 1
}

# Parse Arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ami-id)
      AMI_ID="$2"
      shift 2
      ;;
    -*|--*)
      echo "❌ Unknown option: $1"
      usage
      ;;
    *)
      break
      ;;
  esac
done

# Validate AMI ID
if [[ -z "$AMI_ID" ]]; then
  echo "❌ Error: --ami-id is required."
  usage
fi

# Check if AMI exists
AMI_CHECK=$(aws ec2 describe-images --image-ids "$AMI_ID" --query 'Images[0].ImageId' --output text 2>/dev/null)

if [[ "$AMI_CHECK" != "$AMI_ID" ]]; then
  echo "❌ Error: AMI $AMI_ID not found or you don't have permission."
  exit 1
fi

# Get associated snapshot IDs
echo "🔍 Looking up snapshots for AMI $AMI_ID..."
SNAPSHOTS=$(aws ec2 describe-images --image-ids "$AMI_ID" \
  --query 'Images[].BlockDeviceMappings[].Ebs.SnapshotId' --output text)

# Deregister the AMI
echo "🗑️  Deregistering AMI: $AMI_ID"
aws ec2 deregister-image --image-id "$AMI_ID"

# Delete each snapshot
for SNAP_ID in $SNAPSHOTS; do
  echo "🔻 Deleting snapshot: $SNAP_ID"
  aws ec2 delete-snapshot --snapshot-id "$SNAP_ID"
done

echo "✅ Cleanup complete for AMI: $AMI_ID"
