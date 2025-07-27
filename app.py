import streamlit as st
import pickle
import re
import os
import certifi
import ssl
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import nltk
from dotenv import load_dotenv
from textblob import TextBlob

# Force SSL to use unverified context globally
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables for certificate verification
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Load environment variables
load_dotenv()

# Download stopwords once, using Streamlit's caching
@st.cache_resource
def load_stopwords():
    nltk.download('stopwords')
    return stopwords.words('english')

# Load model and vectorizer once
@st.cache_resource
def load_model_and_vectorizer():
    try:
        with open('model.pkl', 'rb') as model_file:
            model = pickle.load(model_file)
        with open('vectorizer.pkl', 'rb') as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
        return model, vectorizer
    except FileNotFoundError as e:
        st.error(f"Error loading model or vectorizer: {e}")
        return None, None

# Sentiment analysis for text input
def predict_sentiment(text, model, vectorizer, stop_words):
    # Preprocess text
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    text = text.split()
    text = [word for word in text if word not in stop_words]
    text = ' '.join(text)
    
    # Handle empty text after preprocessing
    if not text.strip():
        return "Neutral"
        
    text = [text]
    text = vectorizer.transform(text)
    
    # Predict sentiment
    sentiment = model.predict(text)
    return "Negative" if sentiment == 0 else "Positive"

# Serper API integration to fetch Reddit posts and analyze sentiment
def fetch_reddit_posts(query, limit=5, serpapi_key=None):
    headers = {
        "X-API-KEY": serpapi_key,
        "Content-Type": "application/json"
    }
    
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

# Function to create a colored card for displaying results
def create_card(post_text, sentiment):
    color = "green" if sentiment == "Positive" else "red" if sentiment == "Negative" else "gray"
    card_html = f"""
    <div style="background-color: {color}; padding: 10px; border-radius: 5px; margin: 10px 0;">
        <h5 style="color: white;">{sentiment} Sentiment</h5>
        <p style="color: white;">{post_text}</p>
    </div>
    """
    return card_html

# Main app logic
def main():
    st.title("Sentiment Analysis")

    # Load stopwords, model, vectorizer
    stop_words = load_stopwords()
    model, vectorizer = load_model_and_vectorizer()
    
    if model is None or vectorizer is None:
        st.error("Failed to load model or vectorizer. Please check that the files exist.")
        return
    
    # Load the SerpAPI key from the environment variables
    serpapi_key = os.getenv("SERPAPI_KEY")
    if not serpapi_key:
        st.error("SerpAPI key is missing. Please provide it in the .env file.")
        return
    
    # User input for search query
    option = st.selectbox("Choose an option", ["Input text", "Get Reddit posts"])

    if option == "Input text":
        text_input = st.text_area("Enter text to analyze sentiment")
        if st.button("Analyze"):
            if text_input.strip():
                sentiment = predict_sentiment(text_input, model, vectorizer, stop_words)
                st.write(f"Sentiment: {sentiment}")
                
                # Display color-coded result
                card_html = create_card(text_input, sentiment)
                st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.warning("Please enter some text to analyze.")
    
    elif option == "Get Reddit posts":
        query = st.text_input("Enter a search query (e.g., 'AI sentiment analysis')")

        if st.button("Analyze Sentiment"):
            if query.strip():
                # Fetch Reddit posts and analyze sentiment
                sentiment_results = fetch_reddit_posts(query, serpapi_key=serpapi_key)

                if sentiment_results:
                    st.subheader("Sentiment Results:")
                    for result in sentiment_results:
                        st.write(f"**Title:** {result['title']}")
                        st.write(f"**Snippet:** {result['snippet']}")
                        st.write(f"**Sentiment:** {result['sentiment']}")
                        st.write("---")

                        # Create and display the colored card
                        card_html = create_card(result['snippet'], result['sentiment'])
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning("No results found for the given query.")
            else:
                st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()
