import os
import json
from flask import Flask, jsonify, request
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import html
import re
import logging

app = Flask(__name__)

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

    def get_news(self, keyword: str = 'currency exchange OR forex OR "foreign exchange"') -> List[Dict]:
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

        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', '', text)
        text = ' '.join(text.split())
        text = re.sub(r'[^\w\s.,!?-]', '', text)

        return text.strip()

    def get_full_description(self, article: Dict) -> str:
        """Combine and clean all available text content from the article."""
        content_parts = []
        if article.get('description'):
            content_parts.append(self.clean_text(article['description']))

        if article.get('content'):
            content = re.sub(r'\[\+\d+ chars\]', '', article['content'])
            content = self.clean_text(content)
            if content and content not in content_parts:
                content_parts.append(content)

        if article.get('title'):
            title_context = self.clean_text(article['title'])
            if not any(title_context in part for part in content_parts):
                content_parts.insert(0, title_context)

        full_description = ' '.join(content_parts)

        return full_description if full_description else "No detailed description available."

    def categorize_article(self, article: Dict) -> List[str]:
        """Categorize article based on content and return all matching categories."""
        text = self.get_full_description(article).lower()
        matching_categories = [category for category, keywords in self.categories.items() if any(keyword in text for keyword in keywords)]
        return matching_categories if matching_categories else None

    def format_articles_for_ml(self, articles: List[Dict]) -> str:
        """Format articles with enhanced description and categories."""
        formatted_output = ""
        for article in articles:
            categories = self.categorize_article(article)
            if not categories:
                continue

            try:
                date_obj = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_date = article['publishedAt']

            full_description = self.get_full_description(article)
            formatted_output += "\n"
            formatted_output += f"Title: {article['title']}\n"
            formatted_output += f"Date: {formatted_date}\n"
            formatted_output += f"Description: {full_description}\n"
            formatted_output += f"Categories: {', '.join(categories)}\n"

        return formatted_output

    def save_articles(self, articles: List[Dict]) -> Tuple[List[Dict], str]:
        """Save articles in both ML format and raw JSON."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        ml_filename = self.output_dir / f'ml_format_news_{timestamp}.txt'
        formatted_content = self.format_articles_for_ml(articles)
        with open(ml_filename, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

        json_filename = self.output_dir / f'raw_news_{timestamp}.json'
        enriched_articles = []
        for article in articles:
            categories = self.categorize_article(article)
            if not categories:
                continue

            article_copy = article.copy()
            article_copy['categories'] = categories
            article_copy['full_description'] = self.get_full_description(article)
            enriched_articles.append(article_copy)

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(enriched_articles, f, ensure_ascii=False, indent=2)

        return enriched_articles, formatted_content

@app.route('/news', methods=['GET'])
def get_news_for_ballerina():
    """Fetch news and return formatted data for Ballerina."""
    api_key = NewsCollector.load_api_key(Path('news_api/news_token.txt'))
    if api_key is None:
        return jsonify({"error": "API key not found"}), 500

    keyword = request.args.get('keyword', default='currency exchange OR forex OR "foreign exchange"')
    collector = NewsCollector(api_key)
    news_articles = collector.get_news(keyword)

    # Debugging print statements to check the fetched articles
    print(f"Number of Articles Fetched: {len(news_articles)}")
    for article in news_articles:
        print(f"Title: {article.get('title', 'No title')}")

    if not news_articles:
        return jsonify({"error": "No news articles found"}), 404

    enriched_articles, formatted_content = collector.save_articles(news_articles)

    # Print formatted content to console for debugging
    print("Formatted Content:")
    print(formatted_content)

    return jsonify({
        "raw_news": enriched_articles,
        "formatted_news": formatted_content
    })

if __name__ == '__main__':
    app.run(port=5002, debug=True)