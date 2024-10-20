import ballerina/http;
import ballerina/io;
import ballerina/log;
import ballerina/file;

// Define HTTP clients as module-level variables with increased timeout
final http:Client newsClient = check new ("http://localhost:5002",
    timeout = 30
);
final http:Client llamaClient = check new ("http://localhost:5001",
    timeout = 300  // 5 minutes timeout
);

// Define the main function
public function main() returns error? {
    // Start the prediction process
    json|error combinedResponse = predict();

    if combinedResponse is json {
        // Print the combined response to the terminal
        io:println("Combined Response: ", combinedResponse.toJsonString());
    } else {
        log:printError("Error in prediction process", 'error = combinedResponse);
        io:println("Error details: ", combinedResponse.message());
    }
}

// Function to perform prediction
function predict() returns json|error {
    log:printInfo("Starting prediction process...");

    // Step 1: Fetch news data from local News API
    log:printInfo("Sending request to local News API...");
    json newsResponse = check fetchLocalNews();

    // Extract the formatted news content from the response
    string _ = check newsResponse.formatted_news;
    
    // Step 2: Send a simplified request to LLaMA API for analysis
    log:printInfo("Sending simplified request to local LLaMA API...");
    json aiResponse = check analyzeWithLocalLLaMA("Hello, world!");

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

// Function to analyze with LLaMA (simplified version)
function analyzeWithLocalLLaMA(string simpleMessage) returns json|error {
    // Create a simplified request body
    json requestBody = {
        "system_message": "You are a helpful assistant.",
        "user_message": simpleMessage
    };

    // Log the request body
    log:printInfo("Request body for LLaMA API: " + requestBody.toJsonString());

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
    return error("Failed to analyze with LLaMA: HTTP " + response.statusCode.toString());
}

// Function to clean the input text and remove non-ASCII characters
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

// Save the response to a file inside the "collected_ai_forecasts" folder
function saveToFile(string content, string fileName) returns error? {
    string folderPath = "./collected_ai_forecasts";

    // Create the folder if it doesn't exist
    check file:createDir(folderPath, file:RECURSIVE);

    // Create the complete file path
    string filePath = folderPath + "/" + fileName;

    // Write the content to the file
    log:printInfo(string `Saving prediction to: ${filePath}`);
    check io:fileWriteString(filePath, content);
}