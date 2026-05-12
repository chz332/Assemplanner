import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template, render_template_string, send_file
from flask_cors import CORS
import uuid
import json
import docx
import pdfplumber
import asyncio

from React.agent import run_react_agent
from graph_visual_with_html import generate_graph_html
from sence_graph_visual_with_html import generate_interactive_map

app = Flask(__name__)
CORS(app)

CHAT_FILE = "chat_store.json"

# Load chat history
if os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        chat_store = json.loads(content) if content else {}
else:
    chat_store = {}

def save_chat_store():
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_store, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    try:
        question = request.form.get("question", "").strip()
        chat_id = request.form.get("chat_id")
        if not question:
            return jsonify({"answer": "Please enter a question", "chat_id": chat_id})

        file = request.files.get("file")
        file_text = ""
        if file:
            ext = os.path.splitext(file.filename)[-1].lower()
            if ext == ".pdf":
                with pdfplumber.open(file) as pdf:
                    file_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            elif ext == ".docx":
                doc = docx.Document(file)
                file_text = "\n".join(p.text for p in doc.paragraphs)
            else:
                return jsonify({"answer": f"File type not supported: {ext}", "chat_id": chat_id})

        if not chat_id or chat_id not in chat_store:
            chat_id = str(uuid.uuid4())
            chat_store[chat_id] = []

        if file_text:
            question += f"\n\n[Attached Document Content]\n{file_text[:3000]}"

        chat_store[chat_id].append({"role": "user", "content": question})

        # Call ReAct agent
        result = asyncio.run(run_react_agent(question))
        answer = result.get("final_answer", "Failed to get valid answer")
        rag_info = result.get("rag_output", "")
        linebalance_result = result.get("line_balance_result", "")

        if not answer:
            answer = "Failed to get valid answer."

        chat_store[chat_id].append({"role": "assistant", "content": answer})
        save_chat_store()

        # Return linebalance_result as well
        return jsonify({
            "answer": answer,
            "chat_id": chat_id,
            "rag_info": rag_info,
            "linebalance_result": linebalance_result
        })

    except Exception as e:
        return jsonify({
            "answer": f"Server error: {str(e)}",
            "chat_id": request.form.get("chat_id")
        })

@app.route("/chats", methods=["GET"])
def get_chats():
    chat_list = []
    for chat_id, messages in chat_store.items():
        title = next((m["content"] for m in messages if m["role"] == "user"), "Untitled")
        chat_list.append({"id": chat_id, "title": title[:20]})
    return jsonify(chat_list)

@app.route("/chats/<chat_id>", methods=["GET"])
def get_chat(chat_id):
    return jsonify(chat_store.get(chat_id, []))

@app.route("/chats/<chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    if chat_id in chat_store:
        del chat_store[chat_id]
        save_chat_store()
        return jsonify({"status": "ok"})
    return jsonify({"status": "not found"}), 404

@app.route("/graph")
def serve_graph():
    try:
        html = generate_graph_html()
        return render_template_string(html)
    except Exception as e:
        return f"Graph loading failed: {e}", 500
    
@app.route("/scene_graph")
def scene_graph():
    json_path = request.args.get("json", "React/scene_graph.json")
    html_path = generate_interactive_map(json_path)
    return send_file(html_path)

if __name__ == "__main__":
    # For Windows asyncio event loop issues:
    # import asyncio
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app.run(debug=True)