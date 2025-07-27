# import tweepy
# import os
# from dotenv import load_dotenv

# load_dotenv()

# bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# client = tweepy.Client(bearer_token=bearer_token)

# username = "AmitShah"
# user = client.get_user(username=username)

# tweets = client.get_users_tweets(id=user.data.id, max_results=5)

# for tweet in tweets.data:
#     print(tweet.text)



# Replace with your actual SerpApi key


import requests
from textblob import TextBlob

SERPER_API_KEY = "6ae48b97d7470ff32779f6aaa6f0a2bab46e9ec6"

def google_reddit_sentiment(query):
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "q": f"{query} site:reddit.com"
    }

    response = requests.post("https://google.serper.dev/search", headers=headers, json=data)
    results = response.json()

    for item in results.get("organic", []):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        full_text = title + " " + snippet
        sentiment = TextBlob(full_text).sentiment.polarity
        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
        print(f"\nTitle: {title}\nSnippet: {snippet}\nSentiment: {sentiment_label}")

# Run it
google_reddit_sentiment("openai gpt-4 opinions")
