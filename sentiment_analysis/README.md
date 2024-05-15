## Overview
This program uses **[Amazon Comprehend](https://aws.amazon.com/comprehend/)** (AI/ML solution) for the *sentiment* analysis of text in a file (each text to be analyzed on one line).
The output for each line of text is a sentiment analysis (POSITIVE/NEGATIVE/MIXED/NEUTRAL sentiment) with a confidence score.
**NOTE:** Amazon Comprehend only analyzes the **first 500** characters of each review (line) for sentiment and only accepts **5 KB** (5000 caharacters) of text per line for sentiment analysis.

## Prerequisites:
- Shared credential file (~/.aws/credentials) with credentials that have the required IAM policies
- The required Python libraries (as per import statements)

## Demo:
[![asciicast](https://asciinema.org/a/570227.png)](https://asciinema.org/a/570227?speed=2)

**NOTE:** COSTS WILL BE INCURRED FOR USING AMAZON COMPREHEND. Refer https://aws.amazon.com/comprehend/pricing/
