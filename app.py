from flask import Flask, request, jsonify
from self_upgrade_robot import SelfUpgradeRobot

app = Flask(__name__)
robot = SelfUpgradeRobot()

@app.route("/")
def home():
    return "🤖 Self-Upgrade Robot Ready!"

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    cmd = data.get("command")
    if cmd == "upgrade":
        # only upgrade when you say so
        robot.self_update("https://github.com/your-repo-link.git")
        return jsonify({"message": "✅ Upgraded manually!"})
    return jsonify({"message": "❌ Unknown command."})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)