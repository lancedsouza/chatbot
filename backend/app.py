from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# LangChain agent and tools
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

# Your logic
from google_calendar import create_event
from pdf_qa_bot import rag_answer, llm  # reusing your PDF RAG logic and LLM

app = Flask(__name__)
CORS(app)

# 📅 Google Calendar Tool
calendar_tool = Tool(
    name="Google Calendar Tool",
    func=lambda x: create_event(**json.loads(x)),
    description="Use this to create calendar events. Input should be JSON with keys: name, date, time, purpose."
)

# 📄 PDF Q&A Tool
pdf_qa_tool = Tool(
    name="PDF Question Answering Tool",
    func=rag_answer,
    description="Use this to answer questions based on uploaded PDF documents."
)

# 🧠 LangChain Agent with both tools
agent = initialize_agent(
    tools=[calendar_tool, pdf_qa_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

@app.route("/")
def home():
    return jsonify({"message": "Backend is running!"})


# ✅ Homepage route
@app.route("/agent", methods=["POST"])
def run_agent():
    data = request.get_json()
    message = data.get("message", "")
    print(f"Received message: {message}")  # debug log

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = agent.invoke(message)
        print(f"Agent response: {response}")  # debug log

        # Extract string output from response
        answer_text = ""
        if isinstance(response, dict) and "output" in response:
            answer_text = response["output"]
        elif hasattr(response, "output"):
            answer_text = response.output
        else:
            answer_text = str(response)

        return jsonify({"answer": answer_text})
    except Exception as e:
        print(f"Agent error: {str(e)}")  # debug log
        return jsonify({"error": str(e)}), 500

# (Optional) 🔧 Manual fallback route (still uses create_event)
@app.route("/book_appointment", methods=["POST"])
def book_appointment():
    data = request.get_json()
    name = data.get("name")
    date = data.get("date")
    time = data.get("time")
    purpose = data.get("purpose")

    if not all([name, date, time, purpose]):
        return jsonify({"error": "Missing information"}), 400

    try:
        calendar_link = create_event(name, date, time, purpose)
        return jsonify({
            "message": f"Appointment booked for {name} on {date} at {time} for {purpose}.",
            "calendar_link": calendar_link
        })
    except Exception as e:
        # 🔥 Print error for debugging
        print("Error in create_event:", e)
        return jsonify({"error": f"create_event failed: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
