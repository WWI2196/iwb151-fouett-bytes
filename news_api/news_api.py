import os
from newsapi import NewsApiClient
from datetime import datetime, timedelta


def load_api_key(file_path):
    """Load API key from a text file."""
    print(f"Attempting to load API key from: {file_path}")
    try:
        with open(file_path, 'r') as file:
            api_key = file.read().strip()
        print("API key loaded successfully")
        return api_key
    except FileNotFoundError:
        print(f"Error: API key file not found at {file_path}. Please provide a valid file.")
        return None
    except Exception as e:
        print(f"Error loading API key: {str(e)}")
        return None


def get_news(newsapi, keyword='currency exchange', country_code='us', category='business', days=7):
    """Fetch news articles based on given parameters."""
    print(f"Fetching news for keyword: {keyword}, country: {country_code}, category: {category}, last {days} days")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        articles = newsapi.get_everything(
            q=keyword,
            language='en',
            from_param=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d'),
            sort_by='relevancy'
        )

        print(f"API Response Status: {articles['status']}")
        print(f"Total Results: {articles['totalResults']}")

        if articles['status'] == 'ok':
            return articles['articles']
        else:
            return f"Error fetching news: {articles.get('message', 'Unknown error')}"

    except Exception as e:
        return f"An error occurred while fetching news: {str(e)}"


def main():
    try:
        print("Starting the news fetching script...")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        api_key_file_path = os.path.join(script_dir, 'news_token.txt')
        print(f"Looking for API key file at: {api_key_file_path}")

        api_key = load_api_key(api_key_file_path)
        if api_key is None:
            print("Failed to load API key. Exiting script.")
            return

        print("Initializing NewsApiClient...")
        newsapi = NewsApiClient(api_key=api_key)

        print("Fetching news articles...")
        news_articles = get_news(newsapi, keyword='finance OR economy OR "currency exchange"', days=30)

        if isinstance(news_articles, list):
            print(f"Found {len(news_articles)} articles:")
            for article in news_articles[:5]:  # Print only the first 5 articles
                print(f"Title: {article['title']}")
                print(f"Description: {article['description']}")
                print(f"URL: {article['url']}")
                print(f"Published at: {article['publishedAt']}")
                print("=" * 40)
        else:
            print("Error:", news_articles)

    except Exception as e:
        print(f"An unexpected error occurred in main: {str(e)}")

    finally:
        print("Script execution completed.")


if __name__ == "__main__":
    main()