import os
import torch
from transformers import pipeline
from flask import Flask, request, jsonify
from huggingface_hub import login
from datetime import datetime

# Load the Hugging Face token from a file
def load_hf_token(file_path):
    try:
        with open(file_path, 'r') as file:
            hf_token = file.read().strip()
            return hf_token
    except FileNotFoundError:
        raise ValueError(f"Token file not found at {file_path}. Please provide a valid file.")

# Create the output directory if it doesn't exist
output_directory = 'collected_ai_forecasts'
os.makedirs(output_directory, exist_ok=True)

token_file_path = 'ai_module\\hf_token.txt'
print(f"Looking for the token file at: {token_file_path}")
hf_token = load_hf_token(token_file_path)

# Login to Hugging Face
if hf_token and hf_token != "TOKEN_ENTER":
    login(token=hf_token)
else:
    raise ValueError("Hugging Face token is invalid or missing.")

model_id = "meta-llama/Llama-3.2-1B-Instruct"
pipe = pipeline(
    "text-generation",
    model=model_id,
    torch_dtype=torch.bfloat16,
    device_map="cpu"
)

def generate_response(system_message, user_message):
    prompt = f"{system_message}\n\nHuman: {user_message}\n\nAssistant:"
    
    # Generate the response using the LLaMA model
    outputs = pipe(prompt, max_new_tokens=4000, do_sample=True, temperature=0.7)
    assistant_response = outputs[0]['generated_text'].split("Assistant:")[-1].strip()

    return assistant_response

def save_forecast(response, user_message):
    # Generate timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"forecast_{timestamp}.txt"
    filepath = os.path.join(output_directory, filename)
    
    # Save the response with context
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Query: {user_message}\n")
        file.write(f"Response:\n{response}\n")
        file.write("-" * 80 + "\n")
    
    # Also update the latest forecast file
    with open('ai_output.txt', 'w', encoding='utf-8') as file:
        file.write(response)
    
    return filepath

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    
    system_message = data.get('system_message', "You are an AI that predicts currency exchange trends based on economic news.")
    user_message = data.get('user_message', "")
    
    if not user_message:
        return jsonify({"error": "No user message provided."}), 400
    
    try:
        response = generate_response(system_message, user_message)
        
        # Save the forecast to a new file
        saved_filepath = save_forecast(response, user_message)
        print(f"Forecast saved to: {saved_filepath}")
        
        return response, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)