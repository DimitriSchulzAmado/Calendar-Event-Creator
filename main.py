import requests
from google_calendar.google_calendar_service import GoogleCalendar
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/notion-webhook/", methods=["POST"])
def receive_notion_webhook():
    if request.method == "POST":
        data = request.get_json()
        print("Received data:", data)
        # GoogleCalendar.create_event(
        #     "teste",
        #     "Localização",
        #     "Descrição",
        #     datetime.datetime(2025, 8, 1, 10, 0),
        #     datetime.datetime(2025, 8, 1, 11, 0),
        # )
        return jsonify({"status": "success", "message": "Webhook received"})
    else:
        return jsonify({"status": "error", "message": "Invalid request method"}), 405


if __name__ == "__main__":
    app.run()
