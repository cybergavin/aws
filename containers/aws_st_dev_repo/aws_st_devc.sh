#!/bin/bash
# Create a dev container for a streamlit + python application that uses AWS services. The application's repo must contain a requirements.txt in its parent folder.
#
if [ $# -ne 1 ]; then
	echo -e "Missing argument.\nUsage: bash ${0} <Git repo URL>\nExample: bash ${0} https://github.com/cybergavin/amazon-bedrock-intro-demo.git"
	exit 1
fi
PYTHON_VERSION="3.9"
REPO_URL="$1"
REPO_URL_HTTP=$(echo $REPO_URL | sed -e "s/.git$//g")
LISTEN_PORT=8501
REPO_DIR=$(echo $(basename $REPO_URL) | sed -e "s/.git$//g")
#
# Check if the Git repo is accessible
#
http_check=$(curl -o /dev/null -s -m 2 -w "%{http_code}\n" ${REPO_URL_HTTP})
if [ $http_check -ne 200 ]; then
	echo "Github repo for $REPO_DIR does not exist. Exiting"
	exit 2
fi
if [ -d $REPO_DIR ] ; then
	rm -rf $REPO_DIR
fi
#
# Check AWS config and test authentication
#
if ! command -v aws &> /dev/null || [[ $(aws --version 2>&1) != aws-cli/2* ]]; then
	echo "Missing AWS CLI or AWS CLI is not version 2. Aborting container execution due to missing credentials for AWS."
	exit 4
fi
if [ ! -f ${PWD}/aws-config ]; then
	echo "Missing aws-config file. Aborting container execution due to missing credentials for AWS."
	exit 5
fi
if ! aws sts get-caller-identity &> /dev/null; then
	echo "AWS CLI v2 is installed but not working correctly. Please check your AWS configuration. Aborting container execution due to incorrect AWS configuration."
	exit 6
fi
#
# Clone the Git repo and check for requirements.txt
#
git clone ${REPO_URL}
if [ ! -f ${REPO_DIR}/requirements.txt ]; then
	echo "Python app repo $REPO_DIR does not have a requirements.txt in parent folder. Exiting"
	exit 7
fi
#
# Build a docker container for the DEV environment
#
docker build \
        -t ${REPO_DIR} --build-arg pyver=${PYTHON_VERSION} \
       	--build-arg listen_port=${LISTEN_PORT} \
       	--build-arg git_repo=${REPO_DIR} \
       	--no-cache .
#
# Run the docker container. You may connect to it using DEV containers extension in Visual Studio Code or via other mechanisms.
#
docker run \
       	-it \
       	-p ${LISTEN_PORT}:${LISTEN_PORT} \
	-v ${PWD}/aws-config:/root/.aws/config \
	-v ${PWD}/${REPO_DIR}:/app/ ${REPO_DIR}