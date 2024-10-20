import ballerina/http;
import ballerina/io;


// Define the main function
public function main() returns error? {
    // Start the prediction process
    json combinedResponse = check predict();

    // Print the combined response to the terminal
    io:println("Combined Response: ", combinedResponse);
}

// Function to perform prediction
function predict() returns json|error {
    io:println("Starting prediction process...");

    // Step 1: Fetch news data from local News API
    io:println("Sending request to local News API...");
    json newsResponse = check fetchLocalNews();

    // Extract the formatted news content from the response
    string formattedNews = check newsResponse.formatted_news;
    
    // Step 2: Send the news data to LLaMA API for analysis
    io:println("Sending request to local LLaMA API...");
    json aiResponse = check analyzeWithLocalLLaMA(formattedNews);

    // Step 3: Combine responses
    json combinedResponse = {
        "news_data": newsResponse,
        "ai_analysis": aiResponse
    };

    // Save the combined response to a text file
    string fileName = "general_currency_forecast.txt";
    check saveToFile(combinedResponse.toJsonString(), fileName);

    return combinedResponse;
}

// Function to fetch news from the local API
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

// Function to analyze news data with LLaMA
function analyzeWithLocalLLaMA(string newsData) returns json|error {
    http:Client llamaClient = check new("http://localhost:5001");

    string systemMessage = string `You are an AI currency analyst expert. Your task is to:
        1. Analyze the provided financial news data.
        2. Identify key currencies and factors impacting their movement.
        3. Predict currency trends for the upcoming week.
        4. Provide specific insights on major currency pairs and key events driving the market.
        Format your response with sections for Analysis, Key Factors, and Predictions.`;

    string userMessage = string `Analyze the following financial news data and predict potential currency trends 
        for the next week based on the key events mentioned:

        ${newsData}

        Please provide:
        1. Currency pairs likely to show significant movement.
        2. Expected trends (bullish/bearish) for each currency pair.
        3. Key factors and risks to monitor.`;

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
function saveToFile(string content, string fileName) returns error? {
    string folderPath = "./collected_ai_forecasts";


    // Create the complete file path
    string filePath = folderPath + "/" + fileName;

    // Write the content to the file
    io:println("Saving prediction to: ", filePath);
    checkpanic io:fileWriteString(filePath, content);
}
