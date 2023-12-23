from bs4 import BeautifulSoup
from pathlib import Path
import os
import requests
import pandas as pd
import json
import boto3
import streamlit as st
import matplotlib.pyplot as plt

# Directories
DATA_DIR = Path(__file__).resolve().parent.joinpath('', 'data')
if not os.path.exists(DATA_DIR):
   os.makedirs(DATA_DIR)


# Create Boto3 client
boto3_client = boto3.client('comprehend')


def scrape_trustpilot(url:str, review_list:list):
    """Scrape trustpilot reviews"""
    url_reviews = []
    response = requests.get(url)
    if response.status_code == 200:
        web_page = response.text
        soup = BeautifulSoup(web_page, "html.parser")
        reviews_raw = soup.find("script", id = "__NEXT_DATA__").string
        reviews_raw = json.loads(reviews_raw)
        rev = reviews_raw["props"]["pageProps"]["reviews"]
        for i in range(len(rev)):
            instance = rev[i]
            review = instance["text"][:4000].replace("\n"," ") # Amazon Comprehend accepts lines up to 5000 bytes and detects sentiments within the first 500 characters.
            review_list.append(review)
        return True
    else:
        return False


def fetch_reviews(business_domain:str, num_pages:int):
    """Fetch reviews and write to CSV"""
    all_reviews = []
    base_url = f"https://www.trustpilot.com/review/{business_domain}?sort=recency"
    # Scrape the most recent reviews first
    if scrape_trustpilot(base_url, all_reviews):
    # Then scrape the desired number of pages
        if num_pages > 1:
            for i in range(1, num_pages + 1):
                scrape_trustpilot(f"{base_url}&page={i}", all_reviews)
        # Use pandas to write to write to csv
        df = {'Body' : all_reviews }
        rev_df = pd.DataFrame(df)
        rev_df.drop_duplicates(subset=['Body'], keep='first', inplace=True)
        rev_df.to_csv(f'{DATA_DIR}/{business_domain}.csv',index=False,header=False)
        return True
    else:
        return False


def analyze_sentiments(business_domain:str, segment_categories:list):
    """Generate sentiments for trustpilot reviews"""
    analyzed_sentiments = []
    sentiment_results = []
    with open(f'{DATA_DIR}/{business_domain}.csv', "r") as input:
        lines = input.readlines()
    # Use Amazon Comprehend to analyze sentiment for each line
    with open(f'{DATA_DIR}/{business_domain}_sentiments.csv', "w", newline='') as output:
        output.write('Sentiment,Confidence,Text\n')
        for line in lines:
            response = boto3_client.detect_sentiment(Text=line,LanguageCode='en')
            analyzed_sentiments.append(response['Sentiment'])
            output.write(f"{response['Sentiment']},{max(response['SentimentScore'].values())},{line}")
    for s in segment_categories:
        sentiment_results.append(f"{(analyzed_sentiments.count(s) * 100 / len(analyzed_sentiments)):.2f}")
    return len(analyzed_sentiments), sentiment_results


def plot_chart(sentiments_labels:list, sentiments_values:list):
    """Plot sentiment distribution for trustpilot reviews"""
    mycolors = ["green", "red", "orange", "blue"]
    fig1, ax1 = plt.subplots()
    ax1.pie(sentiments_values, labels=sentiments_labels, colors=mycolors)
    ax1.axis('equal')
    st.pyplot(fig1)


def main():
    """Main function for application"""
    st.set_page_config(page_title="Trustpilot Business domain reviews")
    css = '''
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                # padding-left: 5rem;
                # padding-right: 5rem;
            }
        </style>
    '''
    st.write(css, unsafe_allow_html=True)
    st.header("Trustpilot review sentiment analysis")
    st.markdown("This demo application displays a **sentiment analysis** for **Trustpilot reviews** for a business domain. " \
                 "The application uses BeautifulSoup to extract the latest reviews (up to ~ 100) from Trustpilot and then uses **Amazon Comprehend** to perform a sentiment analysis. " )
    col1, col2 = st.columns([0.4,1])
    with col1:
        bd_input = st.text_input("Enter a business domain name (e.g., amazon.com)", key="bd_input_key")
    with col2:
        bd_input_validation = st.empty()
        #bd_output = st.empty()
        if bd_input:
            if len(st.session_state.bd_input_key) < 5:
                with bd_input_validation.container():
                    st.error('Your business domain must contain at least 5 characters.', icon="🚨")
            else:
                segment_categories = ['POSITIVE', 'NEGATIVE', 'MIXED', 'NEUTRAL']
                if fetch_reviews(st.session_state.bd_input_key,5):
                    tp_sentiments = analyze_sentiments(st.session_state.bd_input_key, segment_categories)
                    num_reviews = tp_sentiments[0]
                    tp_sentiments_labels = [f'POSITIVE - {tp_sentiments[1][0]}%', f'NEGATIVE - {tp_sentiments[1][1]}%', f'MIXED - {tp_sentiments[1][2]}%', f'NEUTRAL - {tp_sentiments[1][3]}%']
                    tp_sentiments_values = tp_sentiments[1]
                    plot_chart(tp_sentiments_labels,tp_sentiments_values)
                    with open(f'{DATA_DIR}/{st.session_state.bd_input_key}_sentiments.csv') as f:
                        st.download_button('Download review sentiments (CSV)', f, file_name=f'{st.session_state.bd_input_key}_sentiments.csv')
                else:
                    with bd_input_validation.container():
                        st.error('There was no result returned from Trustpilot. Check if your business domain has reviews on Trustpilot.', icon="🚨")                    


if __name__ == "__main__":
    main()