# DEV container for an AWS streamlit app hosted in a git repository

This application may be used to create a disposable, working DEV container for a streamlit application in a Git repository. The streamlit application must have a `requirements.txt` in its root folder for the required python modules to be installed into the container image.

## Usage

You have a streamlit application that uses AWS services hosted in a git repository. You want a working, disposable "DEV" environment to work on the application. The steps below outline how you may create and use such a DEV environment using containers.

### STEP 1: Clone this application's repository

```
git clone https://github.com/cybergavin/aws.git
cd aws/containers/aws_st_dev_repo
```

### STEP 2: Update the AWS config

Update `aws-config` to reflect your AWS credentials (SSO or access key). SSO with IAM Identity Center is recommended.

### STEP 3: Launch DEV container for your streamlit application

```
bash aws_st_devc.sh <git repo URL>
```

NOTE: The Git repo URL must include the suffix `.git`

Upon execution of the above script, a container image will be built and launched for your streamlit app and you will be logged into the container as the root user. 

### STEP 4: Work in your new DEV container environment

You may now work in your new DEV container environment via the shell or interact with it using MS Visual Studio Code ([Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers#review-details)). 
You may run the streamlit application on port 8501 and access it at http://localhost:8501