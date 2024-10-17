import ballerina/http;
import ballerina/log;

service /currency on new http:Listener(8080) {

    resource function post prediction() returns json|error {
        // Inputs that Ballerina will send to the LLaMA module
        string systemMessage = "You are an AI that predicts currency exchange trends based on economic news.";
        string userMessage = "What is the future trend for USD to EUR?";

        // Call the AI model service (llma_module.py Flask API) to get prediction
        json aiPrediction = check callAIPredictionService(systemMessage, userMessage);
        
        // Print the response from the LLaMA module to the terminal
        log:printInfo("AI Prediction: " + aiPrediction.toString());

        // Return the AI prediction as the HTTP response
        return aiPrediction;
    }
}

// Function to call the Flask-based AI prediction service (llma_module.py)
function callAIPredictionService(string systemMessage, string userMessage) returns json|error {
    // Create an HTTP client to communicate with the LLaMA Flask API (on port 5001)
    http:Client aiClient = check new("http://localhost:5001");  // LLaMA module is running on port 5001
    
    // Prepare the JSON payload to send to the Python API
    json payload = {
        "system_message": systemMessage,
        "user_message": userMessage
    };
    
    // Send the POST request to the `/predict` endpoint
    http:Response aiResponse = check aiClient->post("/predict", payload);
    
    // Extract the JSON response from the Python API
    json aiPrediction = check aiResponse.getJsonPayload();
    return aiPrediction;
}
