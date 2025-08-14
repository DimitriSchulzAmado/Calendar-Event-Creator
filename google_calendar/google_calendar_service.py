import os.path
import json

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendar:
    def __init__(self):
        pass

    @staticmethod
    def create_event(
        summary: str,
        location: str,
        description: str,
        start_time: str,
        end_time: str,
        remind: int,
        type: str,
    ):
        creds = None
        credentials_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        token_json = os.getenv("GOOGLE_TOKEN")

        if token_json:
            creds = Credentials.from_authorized_user_info(
                json.loads(token_json), SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Atualiza o token na variável de ambiente, se necessário
            else:
                if credentials_json:
                    creds_info = json.loads(credentials_json)
                    flow = InstalledAppFlow.from_client_config(creds_info, SCOPES)
                    creds = flow.run_local_server(port=0)
                    # Após autenticação, salve o token manualmente no .env para uso futuro
                else:
                    raise Exception(
                        "Credenciais do Google Calendar não encontradas nas variáveis de ambiente."
                    )

        try:
            service = build("calendar", "v3", credentials=creds)

            event = {
                "summary": summary,
                "location": location,
                "description": description,
                "start": {
                    "dateTime": start_time,
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": "America/Sao_Paulo",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": remind},
                    ],
                },
            }

            calendars = service.calendarList().list().execute()
            for calendar in calendars["items"]:
                print(calendar["id"], calendar["summary"])
            event = service.events().insert(calendarId="primary", body=event).execute()
            # print(f"Event created: {event.get('htmlLink')}")

        except HttpError as error:
            print("An error occurred:", error)
            creds = None
