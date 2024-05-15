## Overview

[Trustpilot](https://www.trustpilot.com/) is a popular platform for consumer reviews of businesses. Trustpilot provides a star rating for reviews. The star rating does not always match the sentiment of the review. This demo application uses **Amazon Comprehend** to perform a **sentiment analysis** of the latest Trustpilot reviews (up to around 100) for a business and displays the sentiment distribution of the reviews. You must provide the business' domain (e.g., amazon.com for Amazon) as input.

Watch the video below for the demo in action.

[Trustpilot_review_sentiments.webm](https://github.com/cybergavin/aws/assets/39437216/982eaf17-69a7-4e8f-8cf0-25becebfa9c5)


## Prerequisites

The following prerequisites must be met to run the demo application on your local workstation.

- AWS account (sandbox account recommended)
- IAM user or role with Administrator access or the [required permissions](https://docs.aws.amazon.com/comprehend/latest/dg/security_iam_id-based-policy-examples.html) to access Amazon Comprehend. Configure this principal's credentials in your environment's [default AWS profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) (AWS_PROFILE).
- Python 3.9+
- Internet access

### Usage
Implement the following steps to start using the demo application:

**STEP 1:** Create a Python virtual environment (Optional)

```
python -m venv demo
cd demo
source bin/activate
```

**STEP 2:** Clone the git repository

```
git clone https://github.com/cybergavin/aws.git
```

Alternatively, download the code and extract the aws directory.

**STEP 3:** Install the required python modules 

```
cd aws/trustpilot_review_sentiments
pip install -r requirements.txt
```

**STEP 4:** Launch the Streamlit application and access the displayed URL

```
streamlit run tp_review_sentiments.py
```
