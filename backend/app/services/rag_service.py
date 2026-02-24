import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast
import re

class RAGService:
    """
    Service for retrieving relevant content examples from the RAG dataset
    """

    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / 'data' / 'rag_ready_social_media_dataset.csv'
        self.df = None
        self.load_data()

    def load_data(self):
        """Load RAG dataset into memory"""
        try:
            self.df = pd.read_csv(self.data_path)
            # Convert string representation of lists to actual lists
            self.df['tags'] = self.df['tags'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
            print(f"✅ Loaded {len(self.df)} content examples from RAG dataset")
        except Exception as e:
            print(f"⚠️ Warning: Could not load RAG dataset: {e}")
            self.df = pd.DataFrame()
    
    def extract_intent(self, user_message: str) -> Dict[str, Any]:
        """Extract platform, keywords, and sentiment from user message"""
        platforms = {
            'facebook': ['facebook', 'fb'],
            'instagram': ['instagram', 'ig', 'insta'],
            'twitter': ['twitter', 'x', 'tweet'],
            'youtube': ['youtube', 'yt'],
            'reddit': ['reddit']
        }
        
        message_lower = user_message.lower()
        
        # Detect platform
        detected_platform = None
        for platform, keywords in platforms.items():
            if any(kw in message_lower for kw in keywords):
                detected_platform = platform.capitalize()
                break
        
        # Extract potential keywords (words longer than 3 chars, excluding common words)
        stop_words = {'post', 'write', 'create', 'generate', 'make', 'content', 'social', 'media', 'for', 'the', 'and', 'with'}
        words = re.findall(r'\b\w+\b', message_lower)
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Detect sentiment intent (default to positive for promotional content)
        sentiment = 'positive'
        if any(word in message_lower for word in ['discount', 'sale', 'offer', 'deal', 'promo']):
            sentiment = 'positive'
        elif any(word in message_lower for word in ['issue', 'problem', 'concern', 'complaint']):
            sentiment = 'negative'
        
        # Check if this is a content generation request
        is_content_request = any(phrase in message_lower for phrase in [
            'write', 'create', 'generate', 'post', 'content', 'caption', 'draft'
        ])
        
        return {
            'platform': detected_platform,
            'keywords': keywords[:5],  # Top 5 keywords
            'sentiment': sentiment,
            'is_content_request': is_content_request
        }
    
    def get_examples(
        self, 
        platform: Optional[str] = None, 
        sentiment: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Filter and retrieve relevant examples"""
        if self.df.empty:
            return []
        
        filtered_df = self.df.copy()
        
        # Filter by platform
        if platform:
            filtered_df = filtered_df[filtered_df['platform'].str.lower() == platform.lower()]
        
        # Filter by sentiment
        if sentiment:
            filtered_df = filtered_df[filtered_df['sentiment'].str.lower() == sentiment.lower()]
        
        # Filter by keywords (check in tags, hook, body)
        if keywords and len(keywords) > 0:
            mask = filtered_df.apply(
                lambda row: any(
                    keyword.lower() in str(row['tags']).lower() or
                    keyword.lower() in str(row['hook']).lower() or
                    keyword.lower() in str(row['body']).lower()
                    for keyword in keywords
                ),
                axis=1
            )
            filtered_df = filtered_df[mask]
        
        # If no results, relax filters
        if len(filtered_df) == 0 and platform:
            filtered_df = self.df[self.df['platform'].str.lower() == platform.lower()]
        
        if len(filtered_df) == 0:
            # Return top examples from entire dataset
            filtered_df = self.df.copy()
        
        # Sort by engagement score
        filtered_df = filtered_df.sort_values('engagement_score', ascending=False)
        
        # Return top K examples
        return filtered_df.head(top_k).to_dict('records')
    
    def get_best_posting_time(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """Analyze best posting times based on engagement"""
        if self.df.empty:
            return {
                'best_time': 'afternoon',
                'avg_engagement': 0.0,
                'sample_size': 0
            }
        
        filtered_df = self.df.copy()
        
        if platform:
            filtered_df = filtered_df[filtered_df['platform'].str.lower() == platform.lower()]
        
        # Group by time_of_day and calculate average engagement
        time_analysis = filtered_df.groupby('time_of_day')['engagement_score'].agg(['mean', 'count']).reset_index()
        time_analysis = time_analysis.sort_values('mean', ascending=False)
        
        if len(time_analysis) == 0:
            return {
                'best_time': 'afternoon',
                'avg_engagement': 0.0,
                'sample_size': 0
            }
        
        best_time = time_analysis.iloc[0]
        return {
            'best_time': best_time['time_of_day'],
            'avg_engagement': float(best_time['mean']),
            'sample_size': int(best_time['count'])
        }
    
    def format_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples into a readable string for LLM context"""
        if not examples:
            return "No similar examples found."
        
        formatted = "Here are some high-performing examples from similar campaigns:\n\n"
        
        for i, ex in enumerate(examples, 1):
            formatted += f"**Example {i}** (Engagement: {ex['engagement_score']:.2f}):\n"
            formatted += f"- Hook: {ex['hook']}\n"
            if pd.notna(ex['body']) and ex['body']:
                formatted += f"- Body: {ex['body']}\n"
            if pd.notna(ex['cta']) and ex['cta']:
                formatted += f"- CTA: {ex['cta']}\n"
            formatted += f"- Posted at: {ex['time_of_day']}\n\n"
        
        print (formatted) # Debug
        return formatted


rag_service = RAGService()
    