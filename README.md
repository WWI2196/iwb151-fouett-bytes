# Currency Exchange Prediction Microservice with AI Integration
A sophisticated microservice that leverages AI to forecast currency exchange rates by analyzing financial news. The system integrates Meta-LLaMA (LLaMA-3.2-1B-Instruct) for AI predictions and NewsAPI for real-time financial news data.

## 🚀 Features
- **Real-time Currency Conversion**: Fetch and convert exchange rates between multiple currencies
- **AI-Powered Forecasting**: Utilize Meta-LLaMA model for exchange rate predictions
- **Automated News Analysis**: Real-time financial news retrieval and processing with relevancy scoring
- **Secure API Management**: Protected storage for API credentials
- **Ballerina Architecture**: Robust microservice structure with error handling and logging
- **Historical Data Storage**: Systematic storage of AI forecasts and news articles

## 🏗️ Architecture
```
.
├── ai_module/
│   ├── hf_token.txt              # Hugging Face API credentials
│   └── llama_api_server.py       # AI prediction service
├── ballerina_code/
│   ├── currency_service.bal      # Main Ballerina service
│   └── collected_ai_forecasts/   # Forecast storage
├── news_api/
│   ├── news_token.txt           # NewsAPI credentials
│   └── news_api_server.py       # News fetching service
└── collected_news/              # News article storage
```

## 📋 Prerequisites
### Required Accounts
- **Hugging Face Account**
  - Create account at [Hugging Face](https://huggingface.co)
  - Request special access for Meta-LLaMA models
  - Generate API token
- **NewsAPI Account**
  - Register at [NewsAPI](https://newsapi.org)
  - Obtain API key
- **Ballerina Installation**
  - Follow official [Ballerina installation guide](https://ballerina.io/learn/install-ballerina/)
  - Required version: 2023R1 or higher

## 🛠️ Installation
1. **Clone Repository**
   ```bash
   git clone https://github.com/WWI2196/iwb151-fouett-bytes.git
   cd currency-exchange-prediction
   ```

2. **Install Python Dependencies**
   ```bash
   pip install torch transformers flask huggingface-hub newsapi-python python-dateutil requests logging
   ```

## 🚦 Usage
1. **Launch AI Service**
   ```bash
   python ai_module/llama_api_server.py
   ```
   Runs on port 5001

2. **Start News Service**
   ```bash
   python news_api/news_api_server.py
   ```
   Runs on port 5002

3. **Run Ballerina Service**
   ```bash
   bal run ballerina_code/currency_service.bal
   ```
> **Important**: Once both Python and Ballerina services are running, AI predictions will be automatically saved to the `collected_ai_forecasts` folder in the main directory.

## ⚙️ Configuration
### API Configuration
1. Place your Hugging Face token in `ai_module/hf_token.txt`
2. Store NewsAPI key in `news_api/news_token.txt`

### Model Customization
- Modify the model ID in `llama_api_server.py` to use alternative models
- Current model: "meta-llama/Llama-3.2-1B-Instruct"
- Configuration: torch.bfloat16, CPU inference, max_tokens=4000

### News API Settings
- Articles fetched from last 7 days
- Relevancy scoring based on categories:
  - Monetary Policy
  - Economic Indicators
  - Currency-Specific News
  - Market Sentiment
  - Geopolitical Events
  - Technical Analysis

## 📊 Data Flow
1. NewsAPI service fetches latest financial news
2. News data is processed and stored in `collected_news`
3. AI service analyzes news using Meta-LLaMA
4. Predictions are stored in `collected_ai_forecasts`
5. Ballerina service orchestrates the entire workflow

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License
Distributed under the MIT License. See `LICENSE` for more information.
