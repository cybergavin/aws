# @cybergavin - https://github.com/cybergavin
# This program uses Amazon Comprehend (AI/ML solution) to analyze text in a file (each text to be analyzed on one line) for a sentiment.
# The output for each review is a sentiment analysis (POSITIVE/NEGATIVE/MIXED/NEUTRAL sentiment) with a confidence score.
# NOTE: Amazon Comprehend only analyzes the first 500 characters of each review (line) for sentiment and only accepts 5 KB of text per review for analysis.
# Prerequisites:
#   - Shared credential file (~/.aws/credentials) with credentials that have the required IAM policies
#   - The required Python libraries (as per import statements)
# COSTS WILL BE INCURRED FOR USING AMAZON COMPREHEND. Refer https://aws.amazon.com/comprehend/pricing/
#########################################################################################################################################
import sys
import boto3
from pathlib import Path, PurePath

if len(sys.argv) != 2:
    print(f"\nMissing input argument!\nUSAGE: python3 {sys.argv[0]} <file name>\nwhere <file name> is the name of the file containing text to be analyzed (each on a different line) for sentiments.\n")
    exit(1)

script_dir = Path((PurePath(sys.argv[0]).parent)).resolve(strict=True)
input_text = sys.argv[1]
results = script_dir / f'{PurePath(input_text).stem}_sentiments.csv'
defined_sentiments = ['POSITIVE', 'NEGATIVE', 'MIXED', 'NEUTRAL']
analyzed_sentiments = []

# Create Comprehend client
client = boto3.client('comprehend')

# Read input file
with open(input_text, "r") as input:
    lines = input.readlines()

# Use Amazon Comprehend to analyze sentiment for each line
with open(results, "w", newline='') as output:
     output.write('Sentiment,Confidence,Text\n')
     for line in lines:
         response = client.detect_sentiment(Text=line,LanguageCode='en')
         analyzed_sentiments.append(response['Sentiment'])
         output.write(f"{response['Sentiment']},{max(response['SentimentScore'].values())},{line}")

# Summarize Sentiments
print(f"{'-' * 90}\nSentiment Summary for {input_text}. Refer the file {PurePath(input_text).stem}_sentiments.csv for analysis.\n{'-' * 90}\n")
print(f"Number of lines of text analyzed = {len(analyzed_sentiments)}\n")
for s in defined_sentiments:
    print(f"{s} - {(analyzed_sentiments.count(s) * 100 / len(analyzed_sentiments)):.2f}%")
