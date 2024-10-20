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

# Create the output directory
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

    try:
        outputs = pipe(prompt, max_new_tokens=4000, do_sample=True, temperature=0.7)
        assistant_response = outputs[0]['generated_text'].split("Assistant:")[-1].strip()
        return assistant_response
    except Exception as e:
        print(f"Error generating response with LLaMA: {e}")
        raise

def save_forecast(response, user_message):
    # Create a new file with the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"forecast_{timestamp}.txt"
    filepath = os.path.join(output_directory, filename)
    
    # Save the response with context
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Query: {user_message}\n")
        file.write(f"Response:\n{response}\n")
        file.write("-" * 80 + "\n")

    return filepath

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        print(f"Request Body: {data}")  
        print(f"Request Headers: {request.headers}") 
        
        system_message = data.get('system_message', 
            "You are an AI currency analyst expert. Your task is to: "
            "1. Analyze the provided financial news data."
            "2. Identify key currencies and factors impacting their movement."
            "3. Predict currency trends for the upcoming week."
            "4. Provide specific insights on major currency pairs and key events driving the market."
            " Format your response with sections for Analysis, Key Factors, and Predictions.")
        
        user_message = data.get('user_message', "")
        
        if not user_message:
            return jsonify({"error": "No user message provided."}), 400
        
        response = generate_response(system_message, user_message)
        
        # Save the forecast to a new file
        saved_filepath = save_forecast(response, user_message)
        print(f"Forecast saved to: {saved_filepath}")
        
        return jsonify({
            "ai_response": response,
            "saved_filepath": saved_filepath
        }), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
