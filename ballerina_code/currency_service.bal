import ballerina/http;
import ballerina/io;
import ballerina/log;

configurable int timeoutInSeconds = 300;

public function main() returns error? {
    log:printInfo("Starting Ballerina ML API test");
    
    string dummyNews = "This is a test news article about currency exchange rates.";
    json|error result = callAIPredictionService(dummyNews);
    
    if (result is json) {
        io:println("ML API Response:");
        io:println(result.toJsonString());
    } else {
        io:println("Error occurred: ", result.message());
    }
}

function callAIPredictionService(string newsDetails) returns json|error {
    http:Client aiClient = check new("http://localhost:5001", timeout = <decimal>timeoutInSeconds);
    
    json payload = {
        "system_message": "You are an AI that predicts currency exchange trends based on economic news.",
        "user_message": newsDetails
    };
    
    log:printInfo("Payload being sent to AI API: " + payload.toJsonString());
    
    log:printInfo("Sending request to AI API...");
    http:Response aiResponse = check aiClient->post("/predict", payload);
    
    log:printInfo("Received response from AI API. Status: " + aiResponse.statusCode.toString());
    
    if (aiResponse.statusCode != 200) {
        string|error responseBody = aiResponse.getTextPayload();
        if (responseBody is string) {
            log:printError("Error response body: " + responseBody);
        }
        return error("AI API returned a non-200 status code: " + aiResponse.statusCode.toString());
    }
    
    json aiPredictionJson = check aiResponse.getJsonPayload();
    return aiPredictionJson;
}