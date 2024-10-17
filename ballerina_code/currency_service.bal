import ballerina/http;
import ballerina/io;

service /currency on new http:Listener(8080) {
    resource function post prediction() returns string|error {
        // Inputs that Ballerina will send to the LLaMA module
        string systemMessage = "You are an AI that predicts currency exchange trends based on economic news.";
        string userMessage = "What is the future trend for USD to EUR?";

        // Call the AI model service to get prediction
        string aiPrediction = check callAIPredictionService(systemMessage, userMessage);
        
        // Print the response from the LLaMA module to the terminal
        io:println("AI Prediction: " + aiPrediction);

        // Return the AI prediction as the HTTP response
        return aiPrediction;
    }
}

function callAIPredictionService(string systemMessage, string userMessage) returns string|error {
    // Create an HTTP client to communicate with the LLaMA Flask API (on port 5001)
    http:Client aiClient = check new("http://localhost:5001");
    
    // Prepare the JSON payload to send to the Python API
    json payload = {
        "system_message": systemMessage,
        "user_message": userMessage
    };
    
    // Send the POST request to the `/predict` endpoint
    http:Response aiResponse = check aiClient->post("/predict", payload);
    
    // Extract the text response from the Python API
    string aiPrediction = check aiResponse.getTextPayload();
    return aiPrediction;
}

public function main() returns error? {
    io:println("Starting Ballerina service on port 8080");
    io:println("Make sure the Python Flask server (llama_api_server.py) is running on port 5001");
}