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
logging.basicConfig(level=logging.INFO)

class NewsCollector:
    def __init__(self, api_key: str, max_articles: int = 10):
        """Initialize NewsCollector with API key and maximum articles limit."""
        self.newsapi = NewsApiClient(api_key=api_key)
        self.output_dir = Path('collected_news')
        self.output_dir.mkdir(exist_ok=True)
        self.max_articles = max_articles  # Maximum number of articles to return
        
        # Categories and their keywords remain the same as before
        self.relevancy_keywords = {
            'monetary_policy': {
                'weight': 3.0,
                'terms': [
                    'interest rate', 'central bank', 'federal reserve', 'ecb', 
                    'bank of japan', 'monetary policy', 'rate decision', 'fed', 
                    'boe', 'bank of england', 'rate hike', 'rate cut'
                ]
            },
            'economic_indicators': {
                'weight': 2.5,
                'terms': [
                    'gdp', 'inflation', 'cpi', 'ppi', 'employment', 'nfp',
                    'trade balance', 'retail sales', 'industrial production',
                    'pmi', 'manufacturing', 'economic growth', 'recession'
                ]
            },
            'currency_specific': {
                'weight': 3.0,
                'terms': [
                    'forex', 'currency', 'exchange rate', 'usd', 'eur', 'gbp',
                    'jpy', 'dollar', 'euro', 'pound', 'yen', 'yuan', 'renminbi',
                    'forex trading', 'currency pair', 'forex market', 
                    'EUR/USD', 'GBP/USD', 'USD/JPY', 'currency market'
                ]
            },
            'market_sentiment': {
                'weight': 2.0,
                'terms': [
                    'bull', 'bear', 'hawkish', 'dovish', 'volatility', 'risk',
                    'sentiment', 'momentum', 'outlook', 'forecast', 'market mood',
                    'risk appetite', 'risk aversion', 'market confidence'
                ]
            },
            'geopolitical': {
                'weight': 2.0,
                'terms': [
                    'war', 'conflict', 'sanctions', 'trade war', 'election',
                    'political', 'agreement', 'deal', 'summit', 'regulation',
                    'policy change', 'diplomatic', 'international relations'
                ]
            },
            'technical_analysis': {
                'weight': 1.5,
                'terms': [
                    'technical analysis', 'support level', 'resistance level',
                    'price action', 'trend analysis', 'market trend',
                    'trading volume', 'market volatility', 'breakout',
                    'technical indicator', 'moving average'
                ]
            }
        }

        self.exclusion_keywords = [
            'cryptocurrency', 'crypto', 'bitcoin', 'ethereum',
            'nft', 'metaverse', 'meme stock', 'reddit',
            'unrelated', 'non-financial'
        ]

    def calculate_relevance_score(self, text: str) -> Tuple[float, Dict[str, int]]:
        """Calculate a relevance score and category matches for the article text."""
        text = text.lower()
        score = 0.0
        category_matches = {category: 0 for category in self.relevancy_keywords.keys()}
        
        # Check for keywords in each category
        for category, data in self.relevancy_keywords.items():
            matches = 0
            for keyword in data['terms']:
                if keyword.lower() in text:
                    matches += 1
                    score += data['weight']
            category_matches[category] = matches
                
        # Apply penalties for exclusion keywords
        for keyword in self.exclusion_keywords:
            if keyword.lower() in text:
                score -= 2.5
                
        return max(score, 0.0), category_matches

    def is_relevant_article(self, article: Dict, min_score: float = 4.0) -> Tuple[bool, float, Dict[str, int]]:
        """Determine if an article is relevant based on its content."""
        full_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
        relevance_score, category_matches = self.calculate_relevance_score(full_text)
        
        # Article must have at least one category with matches to be considered relevant
        has_categories = any(matches > 0 for matches in category_matches.values())
        
        return (relevance_score >= min_score and has_categories), relevance_score, category_matches

    def get_news(self, keyword: str = None) -> List[Dict]:
        """Fetch news articles with comprehensive relevancy filtering."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            if keyword is None:
                keyword = ('(forex OR "foreign exchange" OR "currency trading") AND '
                         '(central bank OR interest rate OR inflation OR currency OR trading)')

            articles = self.newsapi.get_everything(
                q=keyword,
                language='en',
                from_param=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d'),
                sort_by='relevancy',
                page_size=100
            )

            if articles['status'] != 'ok':
                logging.warning(f"API returned status: {articles['status']}")
                return []

            # Filter and enrich articles
            relevant_articles = []
            for article in articles['articles']:
                is_relevant, score, categories = self.is_relevant_article(article)
                if is_relevant:
                    # Only include articles that have at least one matching category
                    matching_categories = [
                        category for category, matches in categories.items() 
                        if matches > 0
                    ]
                    if matching_categories:  # Skip if no categories match
                        article['relevance_score'] = score
                        article['category_matches'] = categories
                        article['primary_categories'] = matching_categories
                        relevant_articles.append(article)

            # Sort by relevance score and limit to max_articles
            relevant_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            relevant_articles = relevant_articles[:self.max_articles]
            
            logging.info(f"Retrieved {len(articles['articles'])} articles, filtered to {len(relevant_articles)} most relevant articles")
            
            return relevant_articles

        except Exception as e:
            logging.error(f"An error occurred while fetching news: {str(e)}")
            return []

    def format_articles_for_ml(self, articles: List[Dict]) -> str:
        """Format articles with enhanced description, relevance score, and categories."""
        formatted_output = f"Top {self.max_articles} Most Relevant Financial News Articles:\n"
        formatted_output += "=" * 80 + "\n"
        
        for i, article in enumerate(articles, 1):
            try:
                date_obj = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                formatted_date = article['publishedAt']

            formatted_output += f"\n{i}. Title: {article['title']}\n"
            formatted_output += f"Date: {formatted_date}\n"
            formatted_output += f"Description: {self.get_full_description(article)}\n"
            formatted_output += f"Relevance Score: {article.get('relevance_score', 0):.2f}\n"
            formatted_output += f"Categories: {', '.join(article.get('primary_categories', []))}\n"
            formatted_output += f"URL: {article['url']}\n"
            formatted_output += "-" * 80 + "\n"

        return formatted_output.strip()

    # ... [rest of the methods remain the same] ...

@app.route('/news', methods=['GET'])
def get_news_for_ballerina():
    """Fetch news and return formatted data with comprehensive filtering."""
    api_key = NewsCollector.load_api_key(Path('news_api/news_token.txt'))
    if api_key is None:
        return jsonify({"error": "API key not found"}), 500

    # Get max_articles from query parameters, default to 10
    max_articles = int(request.args.get('max_articles', 10))
    collector = NewsCollector(api_key, max_articles=max_articles)
    
    keyword = request.args.get('keyword', default=None)
    news_articles = collector.get_news(keyword)

    if not news_articles:
        return jsonify({"error": "No relevant news articles found"}), 404

    enriched_articles, formatted_content = collector.save_articles(news_articles)

    response = jsonify({
        "raw_news": enriched_articles,
        "formatted_news": formatted_content,
        "total_articles": len(news_articles),
        "categories_found": list(set(
            cat for article in enriched_articles 
            for cat in article.get('primary_categories', [])
        ))
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(port=5002, debug=True)