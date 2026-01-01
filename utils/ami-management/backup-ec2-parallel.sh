#!/bin/bash
# Backup EC2 instances in parallel, creating AMIs with a specified prefix.
# Usage: ./backup-ec2-parallel.sh [--prefix <ami_prefix>] [--file <instances_file>] [--batch <max_parallel_jobs>]
# Ensure you have the AWS CLI configured with appropriate permissions.
###############################################################################################
# Defaults
AMI_PREFIX="cps"
INSTANCE_NAME_FILE="instances.txt"
MAX_PARALLEL=4
DATE=$(date +%Y%m%d-%H%M%S)

# Usage Function
function usage() {
  echo "Usage: $0 [--prefix <ami_prefix>] [--file <instances_file>] [--batch <max_parallel_jobs>]"
  echo ""
  echo "  --prefix   AMI name prefix (default: cps)"
  echo "  --file     File with EC2 instance names (default: instances.txt)"
  echo "  --batch    Max parallel backups (default: 4)"
  exit 1
}

# Parse Arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --prefix)
      AMI_PREFIX="$2"
      shift 2
      ;;
    --file)
      INSTANCE_NAME_FILE="$2"
      shift 2
      ;;
    --batch)
      MAX_PARALLEL="$2"
      shift 2
      ;;
    -*|--*)
      echo "❌ Unknown option $1"
      usage
      ;;
    *)
      break
      ;;
  esac
done

# Validate instance name file
if [[ ! -f "$INSTANCE_NAME_FILE" ]]; then
  echo "❌ Error: Instance name file '$INSTANCE_NAME_FILE' not found."
  exit 1
fi

# Semaphore control function to limit parallel jobs
function wait_for_jobs {
  while (( $(jobs -r | wc -l) >= MAX_PARALLEL )); do
    sleep 1
  done
}

# Per-instance backup logic
function backup_instance {
  INSTANCE_NAME="$1"
  echo "🔍 Processing instance: $INSTANCE_NAME"

  INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=$INSTANCE_NAME" \
    --query "Reservations[].Instances[].InstanceId" --output text)

  if [[ -z "$INSTANCE_ID" ]]; then
    echo "❌ Instance not found: $INSTANCE_NAME"
    return
  fi

  STATE=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
    --query "Reservations[0].Instances[0].State.Name" --output text)

  echo "ℹ️  $INSTANCE_NAME ($INSTANCE_ID) is in state: $STATE"

  if [[ "$STATE" == "running" ]]; then
    echo "🛑 Stopping $INSTANCE_NAME..."
    aws ec2 stop-instances --instance-ids "$INSTANCE_ID" >/dev/null
    aws ec2 wait instance-stopped --instance-ids "$INSTANCE_ID"
  fi

  AMI_NAME="${AMI_PREFIX}-${INSTANCE_NAME}-${DATE}"
  echo "📸 Creating AMI for $INSTANCE_NAME: $AMI_NAME"

  AMI_ID=$(aws ec2 create-image \
    --instance-id "$INSTANCE_ID" \
    --name "$AMI_NAME" \
    --no-reboot \
    --query 'ImageId' --output text)

  if [[ -z "$AMI_ID" ]]; then
    echo "❌ Failed to create AMI for $INSTANCE_NAME"
    return
  fi

  echo "⏳ Waiting for AMI $AMI_ID to become available..."
  aws ec2 wait image-available --image-ids "$AMI_ID"

  echo "✅ AMI $AMI_ID is available for $INSTANCE_NAME"

  echo "🚀 Restarting $INSTANCE_NAME..."
  aws ec2 start-instances --instance-ids "$INSTANCE_ID" >/dev/null
  echo "✅ $INSTANCE_NAME backup complete"
}

# Main loop: parallel execution
while IFS= read -r INSTANCE_NAME || [[ -n "$INSTANCE_NAME" ]]; do
  [[ -z "$INSTANCE_NAME" ]] && continue
  wait_for_jobs
  backup_instance "$INSTANCE_NAME" &
done < "$INSTANCE_NAME_FILE"

wait  # Wait for all background jobs to complete

echo "🎉 All instance backups completed."
