import os
import torch
from transformers import pipeline
import warnings
from flask import Flask, request, jsonify
from huggingface_hub import login

warnings.filterwarnings('ignore')

# Get the Hugging Face token (replace 'TOKEN_ENTER' with your actual token or use env variable)
hf_token = os.getenv('HUGGINGFACE_TOKEN', 'TOKEN_ENTER')

# Login to Hugging Face
if hf_token and hf_token != "TOKEN_ENTER":
    login(token=hf_token)
else:
    raise ValueError("HUGGINGFACE_TOKEN not found or invalid. Please set it correctly.")

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
        return jsonify({"assistant_response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Running Flask app on port 5001
    app.run(port=5001, debug=True)
