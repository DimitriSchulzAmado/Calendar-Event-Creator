import os
from google_calendar.google_calendar_service import GoogleCalendar
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/notion-webhook/", methods=["POST"])
def receive_notion_webhook():
    if request.method == "POST":
        response = request.get_json()
        print(response)
        properties = response["data"]["properties"]

        GoogleCalendar.create_event(
            summary=properties["Name"]["title"][0]["text"]["content"],
            location=properties["Place"]["rich_text"][0]["text"]["content"],
            description=properties["Description"]["rich_text"][0]["text"]["content"],
            start_time=properties["Date"]["date"]["start"],
            end_time=properties["Date"]["date"]["end"],
            remind=properties["Remind"]["number"],
            type=properties["Type"]["select"]["name"],
        )

        return jsonify({"status": "success", "message": "Webhook received"})
    else:
        return jsonify({"status": "error", "message": "Invalid request method"}), 405


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
