import ballerina/http;
import ballerina/io;
import ballerina/log;
import ballerina/lang.runtime;

configurable int timeoutInSeconds = 300;

service /currency on new http:Listener(8080) {
    resource function post prediction() returns string|error {
        log:printInfo("Received prediction request");

        // Fetch news details
        string newsDetails = check getNewsDetailsFromPythonAPI();
        log:printInfo("Fetched News Details for prediction: " + newsDetails);

        // Call AI Prediction Service
        string aiPrediction = check callAIPredictionService(newsDetails);
        log:printInfo("AI Prediction Result: " + aiPrediction);

        // Output only the currency predictions
        return aiPrediction;
    }

    // New endpoint for testing news API
    resource function get testNews() returns string|error {
        return getNewsDetailsFromPythonAPI();
    }

    // New endpoint for testing AI API
    resource function get testAI() returns string|error {
        string dummyNews = "This is a test news article about currency exchange rates.";
        return callAIPredictionService(dummyNews);
    }
}

function getNewsDetailsFromPythonAPI() returns string|error {
    http:Client newsClient = check new("http://localhost:5002", timeout = <decimal>timeoutInSeconds);
    
    log:printInfo("Sending request to News API...");
    http:Response|error newsResponse = newsClient->get("/news");
    
    if (newsResponse is error) {
        log:printError("Error calling News API: " + newsResponse.message());
        return error("Failed to fetch news");
    }
    
    log:printInfo("Received response from News API. Status: " + newsResponse.statusCode.toString());
    
    json|error newsJson = newsResponse.getJsonPayload();
    if (newsJson is error) {
        log:printError("Error parsing News API response: " + newsJson.message());
        return error("Failed to parse news response");
    }
    
    json|error formattedNews = newsJson.formatted_news;
    if (formattedNews is error) {
        log:printError("Error extracting formatted news: " + formattedNews.message());
        return error("Failed to extract formatted news");
    }
    
    return formattedNews.toString();
}

function callAIPredictionService(string newsDetails) returns string|error {
    http:Client aiClient = check new("http://localhost:5001", timeout = <decimal>timeoutInSeconds);
    
    json payload = {
        "user_message": newsDetails
    };
    
    log:printInfo("Payload being sent to AI API: " + payload.toJsonString());
    
    log:printInfo("Sending request to AI API...");
    http:Response|error aiResponse = aiClient->post("/predict", payload);
    
    if (aiResponse is error) {
        log:printError("Error calling AI API: " + aiResponse.message());
        return error("Failed to call AI prediction service");
    }
    
    log:printInfo("Received response from AI API. Status: " + aiResponse.statusCode.toString());
    
    json|error aiPredictionJson = aiResponse.getJsonPayload();
    if (aiPredictionJson is error) {
        log:printError("Error parsing AI API response: " + aiPredictionJson.message());
        return error("Failed to parse AI prediction response");
    }
    
    json|error currencyPredictions = aiPredictionJson.currency_predictions;
    if (currencyPredictions is error) {
        log:printError("Error extracting currency predictions: " + currencyPredictions.message());
        return error("Failed to extract currency predictions");
    }
    
    return currencyPredictions.toString();
}

public function main() returns error? {
    log:printInfo("Starting Ballerina service on port 8080");
    log:printInfo("Ensure both Python Flask servers are running: news collection (port 5002) and AI prediction (port 5001)");
    log:printInfo("Test endpoints: ");
    log:printInfo("  - News API: http://localhost:8080/currency/testNews");
    log:printInfo("  - AI API: http://localhost:8080/currency/testAI");
    log:printInfo("  - Full prediction: Send a POST request to http://localhost:8080/currency/prediction");

    // Keeping the service alive
    while true {
        io:println("\nService is running. Press Ctrl+C to stop.");
        runtime:sleep(60);
    }
}