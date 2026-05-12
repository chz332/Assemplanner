import requests
import os

API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE = os.getenv("OPENAI_BASE_URL")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def chat_completion(messages, model="gpt-4o", temperature=0.4, max_tokens=512):
    url = f"{API_BASE}/chat/completions"
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

class LineBalancingAgent:
    def __init__(self, model="gpt-4"):
        self.answer = ""
        self.model = model

    def solve(self, question: str, memory=None) -> str:
        prompt = "You are an expert in industrial engineering and line balancing.\n\n"
        if memory:
            prompt += "Here are your past reflection records:\n"
            for i, (q, a) in enumerate(memory):
                prompt += f"[Previous Question {i+1}] {q}\n[Previous Answer {i+1}] {a}\n\n"
        prompt += f"""Now, please solve the following task:\n{question}
        \nOutput the workstation process allocation scheme. You can decide the number of workstations.
        ***Important Notes***
        - Processes have strict precedence relationships that must be followed
        - Cycle time is the maximum working time across all workstations
        - Consider multiple approaches instead of repeating previous solutions
        - Provide evaluation metrics and explain your criteria
        - Keep output concise and include calculation results for each allocation
        """

        messages = [
            {"role": "system", "content": "You are an expert in line balancing"},
            {"role": "user", "content": prompt}
        ]

        resp_json = chat_completion(messages, model=self.model)
        self.answer = resp_json["choices"][0]["message"]["content"].strip()
        return self.answer