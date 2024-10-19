import ballerina/http;
import ballerina/io;

// Increase the timeout to 5 minutes (300000 milliseconds)
configurable int timeoutInSeconds = 300;

// Service that handles currency exchange predictions
service /currency on new http:Listener(8080) {
    resource function post prediction() returns string|error {
        // Collect news details from Python NewsCollector
        string systemMessage = "You are an AI that predicts currency exchange trends based on economic news.";
        
        // Fetch the latest economic news to predict based on the current trends
        string newsDetails = check getNewsDetailsFromPythonAPI();
        io:println("Fetched News Details for AI Prediction: \n" + newsDetails);

        // Send the collected news details to the AI model for prediction
        string aiPrediction = check callAIPredictionService(systemMessage, newsDetails);
        
        // Print the response from the LLaMA module to the terminal
        io:println("AI Prediction based on news: " + aiPrediction);

        // Return the AI prediction as the HTTP response
        return aiPrediction;
    }
}

// Function to call Python NewsCollector API and get formatted news details
function getNewsDetailsFromPythonAPI() returns string|error {
    // Create an HTTP client to communicate with the Python API (on port 5002)
    http:Client newsClient = check new("http://localhost:5002",
        timeout = <decimal>timeoutInSeconds
    );
    
    // Send a GET request to the `/collect-news` endpoint of the Python service
    http:Response newsResponse = check newsClient->get("/collect-news");
    io:println("Received response from Python News API.");
    
    // Extract the formatted news details
    string newsDetails = check newsResponse.getTextPayload();
    
    return newsDetails;
}

// Function to send the news to the LLaMA model for currency prediction
function callAIPredictionService(string systemMessage, string newsDetails) returns string|error {
    // Create an HTTP client to communicate with the LLaMA Flask API (on port 5001)
    http:Client aiClient = check new("http://localhost:5001",
        timeout = <decimal>timeoutInSeconds
    );
    
    // Prepare the JSON payload to send to the Python API
    json payload = {
        "system_message": systemMessage,
        "user_message": newsDetails
    };
    
    io:println("Sending request to Python AI API...");
    // Send the POST request to the `/predict` endpoint
    http:Response aiResponse = check aiClient->post("/predict", payload);
    io:println("Received response from Python AI API.");
    
    // Extract the AI prediction text response
    string aiPrediction = check aiResponse.getTextPayload();

    // Return the prediction made by the AI
    return aiPrediction;
}

public function main() returns error? {
    io:println("Starting Ballerina service on port 8080");
    io:println("Ensure both Python Flask servers are running: one for news collection (port 5002) and one for AI prediction (port 5001)");

    while true {
        io:println("\nSend a POST request to `/currency/prediction` to predict currency trends based on economic news.");
        io:println("Enter 'exit' to stop the service.");

        string userInput = io:readln();
        if (userInput.toLowerAscii() == "exit") {
            break;
        }
    }

    io:println("Exiting the Currency Prediction Service.");
}
