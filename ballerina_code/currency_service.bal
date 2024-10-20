import ballerina/http;
import ballerina/io;

// Service definition
service / on new http:Listener(8080) {
    resource function get predict/[string baseCurrency]/[string targetCurrency]() returns json|error {
        io:println("Starting prediction process...");

        // Step 1: Fetch news data from local News API
        io:println("Sending request to local News API...");
        json newsResponse = check fetchLocalNews();

        // Extract the formatted news content from the response
        string formattedNews = check newsResponse.formatted_news;
        
        // Step 2: Send to local LLaMA API for analysis
        io:println("Sending request to local LLaMA API...");
        json aiResponse = check analyzeWithLocalLLaMA(formattedNews, baseCurrency, targetCurrency);

        // Step 3: Combine responses
        json combinedResponse = {
            "news_data": newsResponse,
            "ai_analysis": aiResponse
        };

        // Print the combined response to the terminal
        io:println("Combined Response: ", combinedResponse);

        // Save the combined response to a text file
        string fileName = string `${baseCurrency}_${targetCurrency}_forecast.txt`;
        saveToFile(combinedResponse.toJsonString(), fileName);

        return combinedResponse;
    }
}

function fetchLocalNews() returns json|error {
    http:Client newsClient = check new("http://localhost:5002");

    // Make request to local news API
    http:Response response = check newsClient->get("/news");

    if response.statusCode == 200 {
        json payload = check response.getJsonPayload();
        return payload;
    }
    return error("Failed to fetch news data: " + response.statusCode.toString());
}

function analyzeWithLocalLLaMA(string newsData, string baseCurrency, string targetCurrency) returns json|error {
    http:Client llamaClient = check new("http://localhost:5001");

    string systemMessage = string `You are an AI currency analyst expert. Your task is to:
        1. Analyze the provided financial news data
        2. Identify key factors affecting the currencies
        3. Provide a detailed prediction for the currency pair's movement
        4. Support your analysis with specific news events
        5. Quantify the predicted movement if possible
        Format your response in a clear, structured way with sections for Analysis, Key Factors, and Prediction.`;

    string userMessage = string `Based on this financial news data, analyze and predict the movement 
        of ${baseCurrency} against ${targetCurrency} in the next week:

        ${newsData}

        Please provide:
        1. Your overall prediction (bullish/bearish)
        2. Expected price movement range
        3. Key factors supporting your prediction
        4. Risk factors to watch`;

    json requestBody = {
        "system_message": systemMessage,
        "user_message": userMessage
    };

    http:Response response = check llamaClient->post("/predict", requestBody);

    if response.statusCode == 200 {
        json payload = check response.getJsonPayload();
        return payload;
    }
    return error("Failed to analyze with LLaMA: " + response.statusCode.toString());
}

// Save the response to a file inside the "collected_ai_forecasts" folder
function saveToFile(string content, string fileName) {
    string folderPath = "./collected_ai_forecasts";

    // Create the complete file path
    string filePath = folderPath + "/" + fileName;

    // Write the content to the file
    io:println("Saving prediction to: ", filePath);
    checkpanic io:fileWriteString(filePath, content);
}
