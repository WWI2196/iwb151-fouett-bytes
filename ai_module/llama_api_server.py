import os
import torch
from transformers import pipeline
import warnings
from flask import Flask, request, jsonify
from huggingface_hub import login

warnings.filterwarnings('ignore')

# Load the Hugging Face token from a file
def load_hf_token(file_path):
    try:
        with open(file_path, 'r') as file:
            hf_token = file.read().strip()
            return hf_token
    except FileNotFoundError:
        raise ValueError(f"Token file not found at {file_path}. Please provide a valid file.")

# Path to the file containing your Hugging Face token
token_file_path = 'C:\\Users\\Wansajee\\OneDrive\\Desktop\\Currency Conversion Microservice with AI Integration\\ai_module\\hf_token.txt'
print(f"Looking for the token file at: {token_file_path}")
hf_token = load_hf_token(token_file_path)


# Get the Hugging Face token
hf_token = load_hf_token(token_file_path)

# Login to Hugging Face
if hf_token and hf_token != "TOKEN_ENTER":
    login(token=hf_token)
else:
    raise ValueError("Hugging Face token is invalid or missing.")

# Initialize the LLaMA pipeline for text generation
model_id = "meta-llama/Llama-3.2-1B-Instruct"  # Change model ID if needed
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

def generate_response(system_message, user_message):
    """Generate AI response based on system prompt and user input."""
    prompt = f"{system_message}\n\nHuman: {user_message}\n\nAssistant:"
    
    # Generate the response using the LLaMA model
    outputs = pipe(prompt, max_new_tokens=1000, do_sample=True, temperature=0.7)
    assistant_response = outputs[0]['generated_text'].split("Assistant:")[-1].strip()
    
    return assistant_response

# Initialize Flask app to expose the API
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    """Flask route to handle predictions."""
    data = request.get_json()
    
    # Retrieve system message and user message from JSON payload
    system_message = data.get('system_message', "You are an assistant AI.")
    user_message = data.get('user_message', "")
    
    if not user_message:
        return jsonify({"error": "No user message provided."}), 400
    
    try:
        # Call the generate_response function to get AI prediction
        response = generate_response(system_message, user_message)
        return response, 200  # Return only the assistant's response as plain text
    except Exception as e:
        return str(e), 500  # Return error message as plain text

if __name__ == '__main__':
    # Running Flask app on port 5001
    app.run(port=5001, debug=True)