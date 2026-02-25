import pandas as pd
import numpy as np
import re
import nltk
from pathlib import Path

# Sentence tokenization
nltk.download('punkt_tab')

# Get the data directory path relative to this script
script_dir = Path(__file__).parent
data_dir = script_dir.parent / 'data'

# Load dataset
df = pd.read_csv(data_dir / 'Social Media Engagement Dataset.csv')

# Clean and prepare data
master_df = df.rename(columns={
    'text_content': 'text',
    'timestamp': 'timestamp',
    'likes_count': 'likes',
    'shares_count': 'shares',
    'hashtags': 'hashtags',
    'sentiment_label': 'sentiment'
})
master_df = master_df[['text', 'timestamp', 'platform', 'likes', 'shares', 'hashtags', 'sentiment']].copy()
master_df['timestamp'] = pd.to_datetime(master_df['timestamp'], errors='coerce')

# Convert sentiment to lowercase
master_df['sentiment'] = master_df['sentiment'].str.lower()

def extract_hashtags(text):
    """Extract hashtags from text."""
    return [tag.lower() for tag in re.findall(r"#\w+", str(text))]

master_df['tags'] = master_df.apply(
    lambda r: r['hashtags'].split(',') if pd.notnull(r['hashtags']) else extract_hashtags(r['text']),
    axis=1
)

def time_of_day(ts):
    if pd.isnull(ts):
        return "unknown"
    hour = ts.hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"

master_df['time_of_day'] = master_df['timestamp'].apply(time_of_day)

master_df['engagement_score'] = master_df['likes'] * 0.6 + master_df['shares'] * 1.4
# Normalize 0–1
min_score = master_df['engagement_score'].min()
max_score = master_df['engagement_score'].max()
master_df['engagement_score'] = (master_df['engagement_score'] - min_score) / (max_score - min_score)

def split_post(text):
    """Split post into hook, body, CTA."""
    sentences = nltk.sent_tokenize(text)
    hook = sentences[0] if sentences else ""
    body = ""
    cta = ""
    for s in sentences[1:]:
        if '?' in s or any(word in s.lower() for word in ['buy', 'check', 'click', 'learn', 'try']):
            cta = s
        else:
            body += " " + s
    body = body.strip()
    return hook, body, cta

master_df[['hook', 'body', 'cta']] = master_df['text'].apply(lambda x: pd.Series(split_post(x)))

rag_df = master_df[['platform', 'hook', 'body', 'cta', 'tags', 'sentiment', 'engagement_score', 'time_of_day']]

output_path = data_dir / 'rag_ready_social_media_dataset.csv'
rag_df.to_csv(output_path, index=False)
print(f"Saved to: {output_path}")

print(rag_df.head())
print(rag_df.shape)