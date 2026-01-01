# 🛠️ AWS Utils

A collection of Python utility scripts to support operational tasks, automation, and configuration management across AWS environments.
All scripts use [`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) and require AWS credentials configured via environment variables, AWS CLI, or IAM role. Refer Dependencies below.

This repository complements our Ansible-based infrastructure workflows. It includes lightweight scripts to support quick, targeted operations where full Ansible playbooks may be excessive or impractical.

---

## 📦 What's Inside

This repository contains modular folders, each focused on a specific area of AWS resource management.

| Folder | Purpose |
|--------|---------|
| `ami-management/` | Scripts to create, clean up, and manage EC2 AMIs and EBS snapshots |
| `ebs/` | Scripts to administer and report on EBS volumes |
| `s3/` | Scripts to administer and report on S3 buckets |
| `ec2/` | Scripts to administer and report on EC2 instances |
| `iam/` | Scripts to administer and report on IAM Policies, Roles and Identity Providers |
| `...` | More folders coming soon as utilities are added |

---

## 🧰 Dependencies

- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Bash (tested on Bash 4+)
- IAM credentials with appropriate permissions

You can configure credentials via environment variables, `~/.aws/config`, or a named profile. Using [`saml2aws`](https://usc-its-jira-cloud.atlassian.net/wiki/spaces/testcsetea/pages/2197717039/HOW-TO+Use+AWS+CLI+SSO+with+Shibboleth) is strongly recommended.

---
