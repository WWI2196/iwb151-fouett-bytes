import ballerina/http;
import ballerina/io;
import ballerina/log;
import ballerina/file;

final http:Client newsClient = check new ("http://localhost:5002",
    timeout = 30
);
final http:Client llamaClient = check new ("http://localhost:5001",
    timeout = 1000 
);

public function main() returns error? {
    json|error combinedResponse = predict();

    if combinedResponse is json {
        io:println("Prediction process completed successfully.");
        io:println("Forecast has been saved in the 'collected_ai_forecasts' folder.");
    } else {
        log:printError("Error in prediction process", 'error = combinedResponse);
        io:println("Error details: ", combinedResponse.message());
    }
}

// Function to perform prediction
function predict() returns json|error {
    log:printInfo("Starting prediction process...");

    // Fetch news from News API
    log:printInfo("Sending request to local News API...");
    json newsResponse = check fetchLocalNews();

    // Get the formatted news content from the response
    string formattedNews = check newsResponse.formatted_news;
    
    // Clean the news content
    string cleanedNews = cleanUtf8(formattedNews);
    
    // Send the cleaned news to LLaMA API for analysis
    log:printInfo("Sending news data to local LLaMA API for analysis...");
    json aiResponse = check analyzeWithLocalLLaMA(cleanedNews);

    // Combine responses
    json combinedResponse = {
        "news_data": newsResponse,
        "ai_analysis": aiResponse
    };

    // Save the combined response to a text file
    string fileName = "general_currency_forecast.txt";
    check saveToFile(combinedResponse.toJsonString(), fileName);

    return combinedResponse;
}

// Function to get news from the News API
function fetchLocalNews() returns json|error {
    log:printInfo("Attempting to fetch news data...");
    http:Response|error response = newsClient->/news;

    if response is error {
        log:printError("Error fetching news data", 'error = response);
        return error("Failed to fetch news data: " + response.message());
    }

    log:printInfo("Received response from News API with status code: " + response.statusCode.toString());

    if response.statusCode == 200 {
        json|error payload = response.getJsonPayload();
        if payload is error {
            log:printError("Error parsing news data", 'error = payload);
            return error("Failed to parse news data: " + payload.message());
        }
        log:printInfo("Successfully parsed News API response");
        return payload;
    }
    return error("Failed to fetch news data: HTTP " + response.statusCode.toString());
}

// Function to analyze with LLaMA
function analyzeWithLocalLLaMA(string newsContent) returns json|error {
    json requestBody = {
        "system_message": "You are an AI currency analyst expert. Your task is to: 1. Analyze the provided financial news data. 2. Identify key currencies and factors impacting their movement. 3. Predict currency trends for the upcoming week. 4. Provide specific insights on major currency pairs and key events driving the market. Format your response with sections for Analysis, Key Factors, and Predictions.",
        "user_message": newsContent
    };

    // Send the request to LLaMA
    log:printInfo("Sending request to LLaMA API...");
    http:Response|error response = llamaClient->/predict.post(requestBody);

    if response is error {
        log:printError("Error sending request to LLaMA", 'error = response);
        return error("Failed to send request to LLaMA: " + response.message());
    }

    log:printInfo("Received response from LLaMA API with status code: " + response.statusCode.toString());

    if response.statusCode == 200 {
        json|error payload = response.getJsonPayload();
        if payload is error {
            log:printError("Error parsing LLaMA response", 'error = payload);
            return error("Failed to parse LLaMA response: " + payload.message());
        }
        log:printInfo("Successfully parsed LLaMA response");
        return payload;
    }
    string|error errorPayload = response.getTextPayload();
    log:printError("LLaMA API error", errorPayload = check errorPayload);
    return error("Failed to analyze with LLaMA: HTTP " + response.statusCode.toString());
}

// Function to clean the input text and remove non ASCII characters
function cleanUtf8(string input) returns string {
    string[] result = [];
    foreach int i in 0 ..< input.length() {
        int codePoint = input.getCodePoint(i);
        if (codePoint <= 127) {
            result.push(input.substring(i, i + 1));
        }
    }
    return string:'join("", ...result);
}

function saveToFile(string content, string fileName) returns error? {
    string folderPath = "./collected_ai_forecasts";

    check file:createDir(folderPath, file:RECURSIVE);

    string filePath = folderPath + "/" + fileName;

    log:printInfo(string `Saving prediction to: ${filePath}`);
    check io:fileWriteString(filePath, content);
}