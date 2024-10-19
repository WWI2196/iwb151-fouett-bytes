import freecurrencyapi
import requests
from requests.structures import CaseInsensitiveDict

def load_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            api_key = file.read().strip()
            return api_key
    except FileNotFoundError:
        raise ValueError(f"API key file not found at {file_path}. Please provide a valid file.")


api_key_file_path = 'currency_api\\currency_token.txt' 

api_key = load_api_key(api_key_file_path)

# FreeCurrencyAPI URL
url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}"

resp = requests.get(url)

# Print the response status code
print(resp.status_code)

# Initialize the FreeCurrencyAPI client with the loaded API key
client = freecurrencyapi.Client(api_key)

# Get status
print(client.status())

# Retrieve currencies
result = client.currencies(currencies=['EUR', 'CAD'])
print(result)

# Retrieve latest exchange rates
result = client.latest()
print(result)

# Retrieve historical exchange rates
result = client.historical('2022-02-02')
print(result)
