import freecurrencyapi
import requests
from requests.structures import CaseInsensitiveDict

url = "https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_cyksGQMCokod6Bn1SbxbwMSbmmg33vu2HafxmJ8u"

resp = requests.get(url)

print(resp.status_code)


# Replace 'API_KEY' with your actual API key
client = freecurrencyapi.Client('fca_live_cyksGQMCokod6Bn1SbxbwMSbmmg33vu2HafxmJ8u')

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
