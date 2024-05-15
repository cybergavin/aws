#!/bin/bash
# Create a dev container for a streamlit app usthat uses AWS services. The app's repo must contain a requirements.txt in its parent folder.
#
if [ $# -ne 1 ]; then
	echo -e "Missing argument.\nUsage: python ${0} <Git repo URL>"
	exit 1
fi
PYTHON_VERSION="3.9"
REPO_URL="$1"
LISTEN_PORT=8501
REPO_DIR=$(echo $(basename $REPO_URL) | sed -e "s/.git//g")

http_check=$(curl -o /dev/null -s -m 2 -w "%{http_code}\n" ${REPO_URL})
if [ $http_check -ne 200 ]; then
	echo "Github repo for $REPO_DIR does not exist. Exiting"
	exit 2
fi
if [ -d $REPO_DIR ] ; then
	rm -rf $REPO_DIR
fi
git clone ${REPO_URL}
if [ ! -f ${REPO_DIR}/requirements.txt ]; then
	echo "Python app repo $REPO_DIR does not have a requirements.txt in parent folder. Exiting"
	exit 3
fi
docker build \
        -t ${REPO_DIR} --build-arg pyver=${PYTHON_VERSION} \
       	--build-arg listen_port=${LISTEN_PORT} \
       	--build-arg git_repo=${REPO_DIR} \
       	--no-cache .
if [ ! -f ${PWD}/aws-config ]; then
	echo "Missing aws-config file. Aborting container execution due to missing credentials for AWS."
	exit 4
fi
docker run \
       	-it \
       	-p ${LISTEN_PORT}:${LISTEN_PORT} \
	-v ${PWD}/aws-config:/root/.aws/config \
	-v ${PWD}/${REPO_DIR}:/app/ ${REPO_DIR}