from textblob import TextBlob
from cleaner import clean_review

def analyze_sentiment(review):
    cleaned_review = clean_review(review)
    polarity = TextBlob(cleaned_review).sentiment.polarity

    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "original_review": review,
        "cleaned_review": cleaned_review,
        "polarity": polarity,
        "sentiment": sentiment
    }


if __name__ == "__main__":
    sample_reviews = [
        "This phone is amazing!",
        "Battery is okay.",
        "Worst product ever!"
    ]

    for review in sample_reviews:
        result = analyze_sentiment(review)
        print(result)