import json
import requests
import os

def load_tasks(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_BASE_URL")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def large_model_judgment(prediction: str, ground_truth: str, model="gpt-4", temperature=0.4, max_tokens=512):
    messages = [
        {"role": "system", "content": "You are an expert in evaluating line balancing problems."},
        {"role": "user", "content": f"""
        We have a line balancing problem. Below is the model's prediction and the ground truth:

        Prediction: {prediction}
        Ground Truth: {ground_truth}

        Please judge if the prediction is correct based on the following criteria:
        - Number of workstations <= 6

        If the prediction meets this criterion, answer "yes", otherwise answer "no".
        """}
    ]
    
    url = f"{API_BASE}/chat/completions"
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        text = result['choices'][0]['message']['content'].strip().lower()
        return text == "yes"
    
    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return False

def is_correct(prediction: str, ground_truth: str) -> bool:
    return large_model_judgment(prediction, ground_truth)