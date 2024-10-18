import ballerina/http;
import ballerina/io;

// Increase the timeout to 5 minutes (300000 milliseconds)
configurable int timeoutInSeconds = 300;

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
    http:Client aiClient = check new("http://localhost:5001",
        timeout = <decimal>timeoutInSeconds
    );
    
    // Prepare the JSON payload to send to the Python API
    json payload = {
        "system_message": systemMessage,
        "user_message": userMessage
    };
    
    io:println("Sending request to Python API...");
    // Send the POST request to the `/predict` endpoint
    http:Response aiResponse = check aiClient->post("/predict", payload);
    io:println("Received response from Python API.");
    
    // Extract the text response from the Python API
    string aiPrediction = check aiResponse.getTextPayload();

    // Read the full content from the file saved by the Python API
    string filePath = "C:\\Users\\Wansajee\\OneDrive\\Desktop\\Currency Conversion Microservice with AI Integration\\ai_output.txt";
    string fileContent = check io:fileReadString(filePath);

    // If the file content is not empty, use it instead of the direct API response
    if (fileContent != "") {
        aiPrediction = fileContent;
    }

    return aiPrediction;
}

public function main() returns error? {
    io:println("Starting Ballerina service on port 8080");
    io:println("Make sure the Python Flask server (llama_api_server.py) is running on port 5001");

    while true {
        io:println("\nEnter your question about currency exchange trends (or type 'exit' to quit):");
        string userInput = io:readln();

        if (userInput.toLowerAscii() == "exit") {
            break;
        }

        if (userInput == "") {
            io:println("Please enter a valid question.");
            continue;
        }

        string systemMessage = "You are an AI that predicts currency exchange trends based on economic news.";
        
        io:println("Sending request to AI service...");
        string aiPrediction = check callAIPredictionService(systemMessage, userInput);
        
        io:println("AI Prediction:\n" + aiPrediction);
    }

    io:println("Exiting the program. Thank you for using the Currency Prediction Service!");
}