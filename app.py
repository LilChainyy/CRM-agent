import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from tools.linkedin_tool import init_linkedin
from agent.agent import create_crm_agent

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

print("Loading LinkedIn connections...")
init_linkedin()

# Cache agents per session to avoid re-creating on every message
_agents = {}


def _get_or_create_agent():
    """Get existing agent for this session or create one from session creds."""
    sid = session.get("_id")
    if sid and sid in _agents:
        return _agents[sid], {"configurable": {"thread_id": sid}}

    api_key = session.get("anthropic_api_key", "")
    gmail_address = session.get("gmail_address", "")
    gmail_password = session.get("gmail_password", "")

    if not api_key:
        return None, None

    agent = create_crm_agent(
        api_key=api_key,
        gmail_address=gmail_address,
        gmail_password=gmail_password,
    )

    if not sid:
        sid = os.urandom(16).hex()
        session["_id"] = sid

    _agents[sid] = agent
    return agent, {"configurable": {"thread_id": sid}}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/settings", methods=["POST"])
def save_settings():
    session["anthropic_api_key"] = request.form.get("anthropic_api_key", "").strip()
    session["gmail_address"] = request.form.get("gmail_address", "").strip()
    session["gmail_password"] = request.form.get("gmail_password", "").strip()

    # Clear cached agent so it gets re-created with new creds
    sid = session.get("_id")
    if sid and sid in _agents:
        del _agents[sid]

    return redirect(url_for("index"))


@app.route("/settings/status")
def settings_status():
    configured = bool(session.get("anthropic_api_key"))
    return jsonify({"configured": configured})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please enter a message."}), 400

    agent, thread_config = _get_or_create_agent()
    if agent is None:
        return jsonify({"response": "Please configure your API keys in Settings first."}), 401

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            config=thread_config,
        )
        messages = result["messages"]
        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "ai" and msg.content:
                return jsonify({"response": msg.content})
        return jsonify({"response": "No response from agent."})
    except Exception as e:
        return jsonify({"response": f"Error: {e}"}), 500


if __name__ == "__main__":
    print("CRM Agent ready on http://localhost:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
