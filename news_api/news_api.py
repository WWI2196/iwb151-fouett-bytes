import os
import json
import logging
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union
import html
import re


class NewsCollector:
    def __init__(self, api_key: str):
        """Initialize NewsCollector with API key."""
        self.newsapi = NewsApiClient(api_key=api_key)
        self.output_dir = Path('collected_news')
        self.output_dir.mkdir(exist_ok=True)

        self.categories = {
            'Monetary Policy': [
                'interest rate', 'central bank', 'federal reserve', 'ecb', 'bank of japan',
                'monetary policy', 'rate decision', 'fed', 'boe', 'bank of england'
            ],
            'Economic Indicators': [
                'gdp', 'inflation', 'cpi', 'ppi', 'employment', 'nfp', 'trade balance',
                'retail sales', 'industrial production', 'pmi', 'manufacturing'
            ],
            'Currency Specific': [
                'forex', 'currency', 'exchange rate', 'usd', 'eur', 'gbp', 'jpy',
                'dollar', 'euro', 'pound', 'yen', 'yuan', 'renminbi'
            ],
            'Market Sentiment': [
                'bull', 'bear', 'hawkish', 'dovish', 'volatility', 'risk',
                'sentiment', 'momentum', 'outlook', 'forecast'
            ],
            'Geopolitical': [
                'war', 'conflict', 'sanctions', 'trade war', 'election', 'political',
                'agreement', 'deal', 'summit', 'regulation'
            ]
        }

    @staticmethod
    def load_api_key(file_path: Union[str, Path]) -> Optional[str]:
        """Load API key from a text file."""
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"API key file not found at {file_path}")
            return None
        except Exception as e:
            print(f"Error loading API key: {str(e)}")
            return None

    def get_news(self,
                 keyword: str = 'currency exchange OR forex OR "foreign exchange"') -> List[Dict]:
        """Fetch news articles based on given parameters."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)  # Capture yesterday and today

            articles = self.newsapi.get_everything(
                q=keyword,
                language='en',
                from_param=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d'),
                sort_by='relevancy'
            )

            if articles['status'] == 'ok':
                return articles['articles']
            return []

        except Exception as e:
            print(f"An error occurred while fetching news: {str(e)}")
            return []

    def clean_text(self, text: str) -> str:
        """Clean and format text content."""
        if not text:
            return ""

        # Decode HTML entities
        text = html.unescape(text)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove extra whitespace and newlines
        text = ' '.join(text.split())

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        return text.strip()

    def get_full_description(self, article: Dict) -> str:
        """Combine and clean all available text content from the article."""
        content_parts = []

        # Add description if available
        if article.get('description'):
            content_parts.append(self.clean_text(article['description']))

        # Add content if available
        if article.get('content'):
            # Remove the "[+chars]" suffix that sometimes appears in content
            content = re.sub(r'\[\+\d+ chars\]', '', article['content'])
            content = self.clean_text(content)
            if content and content not in content_parts:  # Avoid duplication
                content_parts.append(content)

        # Add title context if needed
        if article.get('title'):
            title_context = self.clean_text(article['title'])
            if not any(title_context in part for part in content_parts):
                content_parts.insert(0, title_context)

        # Combine all parts
        full_description = ' '.join(content_parts)

        # If still empty, use a placeholder
        if not full_description:
            return "No detailed description available."

        return full_description

    def categorize_article(self, article: Dict) -> List[str]:
        """Categorize article based on content and return all matching categories."""
        text = self.get_full_description(article).lower()

        matching_categories = []
        for category, keywords in self.categories.items():
            if any(keyword in text for keyword in keywords):
                matching_categories.append(category)

        return matching_categories if matching_categories else ['Uncategorized']

    def format_articles_for_ml(self, articles: List[Dict]) -> str:
        """Format articles with enhanced description and categories."""
        formatted_output = ""
        for article in articles:
            # Format date
            try:
                date_obj = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_date = article['publishedAt']

            # Get full description
            full_description = self.get_full_description(article)

            # Get categories
            categories = self.categorize_article(article)

            # Add formatted article with clear section separation
            formatted_output += "\n"  # Section separator
            formatted_output += f"Title: {article['title']}\n"
            formatted_output += f"Date: {formatted_date}\n"
            formatted_output += f"Description: {full_description}\n"
            formatted_output += f"Categories: {', '.join(categories)}\n"


        return formatted_output

    def save_articles(self, articles: List[Dict]):
        """Save articles in both ML format and raw JSON."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save ML format
        ml_filename = self.output_dir / f'ml_format_news_{timestamp}.txt'
        formatted_content = self.format_articles_for_ml(articles)
        with open(ml_filename, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        # Save raw JSON with categories and full descriptions
        json_filename = self.output_dir / f'raw_news_{timestamp}.json'
        enriched_articles = []
        for article in articles:
            article_copy = article.copy()
            article_copy['categories'] = self.categorize_article(article)
            article_copy['full_description'] = self.get_full_description(article)
            enriched_articles.append(article_copy)

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(enriched_articles, f, ensure_ascii=False, indent=2)


def main():
    try:
        # Setup
        script_dir = Path(__file__).parent
        api_key_file_path = script_dir / 'news_token.txt'

        # Load API key
        api_key = NewsCollector.load_api_key(api_key_file_path)
        if api_key is None:
            print("Failed to load API key. Exiting script.")
            return

        # Initialize collector and fetch news
        collector = NewsCollector(api_key)
        news_articles = collector.get_news()

        if news_articles:
            print(collector.format_articles_for_ml(news_articles))
            collector.save_articles(news_articles)
        else:
            print("No articles were retrieved")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()