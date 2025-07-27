import streamlit as st
import requests
from textblob import TextBlob
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Replace with your SerpApi key
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def google_reddit_sentiment(query):
    headers = {
        "X-API-KEY": SERPAPI_KEY,
        "Content-Type": "application/json"
    }
    
    # Query Reddit posts related to the search term
    data = {
        "q": f"{query} site:reddit.com"
    }
    
    try:
        response = requests.post("https://google.serper.dev/search", headers=headers, json=data)
        results = response.json()

        if 'organic' not in results:
            st.error("No search results found!")
            return []

        sentiment_results = []
        for item in results.get("organic", []):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            full_text = title + " " + snippet

            # Get sentiment of the text
            sentiment = TextBlob(full_text).sentiment.polarity
            sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"
            sentiment_results.append({"title": title, "snippet": snippet, "sentiment": sentiment_label})
        
        return sentiment_results
    
    except Exception as e:
        st.error(f"Error fetching results: {e}")
        return []

def main():
    st.title("Reddit Sentiment Analysis")

    # Input for search query
    query = st.text_input("Enter a search query (e.g., 'AI sentiment analysis')")

    if query.strip() and st.button("Analyze Sentiment"):
        # Call Serper API to get sentiment of Reddit posts related to the query
        sentiment_results = google_reddit_sentiment(query)

        if sentiment_results:
            st.subheader("Sentiment Results:")
            for result in sentiment_results:
                st.write(f"**Title:** {result['title']}")
                st.write(f"**Snippet:** {result['snippet']}")
                st.write(f"**Sentiment:** {result['sentiment']}")
                st.write("---")

if __name__ == "__main__":
    main()
