import os
import tweepy


def _client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_SECRET"),
    )


def post_tweet(text: str) -> dict:
    """Post a tweet and return a dict with the tweet id and URL."""
    missing = [
        k for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")
        if not os.getenv(k)
    ]
    if missing:
        raise ValueError(f"Missing X API credentials: {', '.join(missing)}")

    response = _client().create_tweet(text=text)
    tweet_id = response.data["id"]
    return {
        "id": tweet_id,
        "url": f"https://x.com/CristianVGB9/status/{tweet_id}",
    }
