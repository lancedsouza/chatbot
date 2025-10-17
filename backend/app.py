from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

# LangChain agent and tools
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

# Your logic
from google_calendar import create_event
from pdf_qa_bot import rag_answer, llm  # reusing your PDF RAG logic and LLM

app = Flask(__name__)
CORS(app)

# 📅 Google Calendar Tool with safer handler
def calendar_tool_handler(input_str):
    try:
        data = json.loads(input_str)
        return create_event(
            name=data.get("name", ""),
            date_str=data.get("date", ""),
            time_str=data.get("time", ""),
            purpose=data.get("purpose", "")
        )
    except Exception as e:
        return f"❌ Failed to parse or create event: {str(e)}"

calendar_tool = Tool(
    name="Google Calendar Tool",
    func=calendar_tool_handler,
    description="Use this to create calendar events. Input must be JSON with keys: name, date, time, purpose."
)

# 📄 PDF Q&A Tool
pdf_qa_tool = Tool(
    name="PDF Question Answering Tool",
    func=rag_answer,
    description="Use this to answer questions based on uploaded PDF documents."
)

# 🧠 LangChain Agent
agent = initialize_agent(
    tools=[calendar_tool, pdf_qa_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

@app.route("/")
def home():
    return jsonify({"message": "Backend is running!"})

@app.route("/agent", methods=["POST"])
def run_agent():
    data = request.get_json()
    message = data.get("message", "").strip()
    print(f"Received message: {message}")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = agent.invoke(message)
        print(f"Agent response: {response}")

        # Cleanly extract output
        if isinstance(response, dict):
            answer_text = response.get("output") or response.get("result") or str(response)
        elif hasattr(response, "output"):
            answer_text = response.output
        else:
            answer_text = str(response)

        return jsonify({"answer": answer_text})
    except Exception as e:
        print(f"Agent error: {str(e)}")
        return jsonify({"error": f"Agent failed: {str(e)}"}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, ''), 'favicon.ico')

@app.route("/book_appointment", methods=["POST"])
def book_appointment():
    data = request.get_json()
    name = data.get("name")
    date = data.get("date")
    time = data.get("time")
    purpose = data.get("purpose")

    if not all([name, date, time, purpose]):
        return jsonify({"error": "Missing one or more required fields."}), 400

    try:
        calendar_link = create_event(name, date, time, purpose)
        return jsonify({
            "message": f"✅ Appointment booked for {name} on {date} at {time} for {purpose}.",
            "calendar_link": calendar_link
        })
    except Exception as e:
        print("Error in create_event:", e)
        return jsonify({"error": f"create_event failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
