#!/bin/bash
# This script uses the AWS CLI to report unattached EBS volumes
output=$(aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query "Volumes[].{VolumeId:VolumeId,Size_GB:Size,AZ:AvailabilityZone,CreateTime:CreateTime,LastInstance:Attachments[-1].InstanceId}" \
  --output table)

if [[ -n "$output" && "$output" != "None" && "$output" != "[]" ]]; then
  echo "$output"
  echo -e "\nNOTE: LastInstance = None → the volume has never been attached.\n"
else
  echo "No unattached volumes found."
fi