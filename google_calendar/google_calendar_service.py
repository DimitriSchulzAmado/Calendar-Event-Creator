import os
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
            # Procura calendarId cujo summary contém o valor de `type` (case-insensitive)
            calendar_id = None
            for calendar in calendars.get("items", []):
                summary = calendar.get("summary", "") or ""
                if type and type.lower() in summary.lower():
                    calendar_id = calendar.get("id")
                    break

            if not calendar_id:
                print(
                    f"Calendar '{type}' not found in calendar list. Falling back to 'primary'."
                )
                calendar_id = "primary"

            try:
                service.calendarList().get(calendarId=calendar_id).execute()
            except HttpError as e:
                try:
                    err = json.loads(e.content.decode())
                except Exception:
                    err = {"error": {"message": str(e)}}
                print("Unable to access chosen calendar:", err)
                if calendar_id != "primary":
                    print("Falling back to primary calendar and retrying insert.")
                    calendar_id = "primary"

            try:
                event = (
                    service.events()
                    .insert(calendarId=calendar_id, body=event)
                    .execute()
                )
            except HttpError as e:
                try:
                    err_json = json.loads(e.content.decode())
                except Exception:
                    err_json = {"error": {"message": str(e)}}
                print(
                    "Failed to create event. API response:",
                    json.dumps(err_json, ensure_ascii=False),
                )

                if err_json.get("error", {}).get("code") == 403:
                    print(
                        "Permission denied. Possible causes:\n"
                        " - The OAuth client is not authorized for this calendar.\n"
                        " - The calendar belongs to another user and wasn't shared with the authenticated account.\n"
                        " - You might be using an API key instead of OAuth credentials. Make sure you're authenticating with OAuth and the token has the correct scopes."
                    )
                raise

        except HttpError as error:
            print("An error occurred:", error)
            creds = None
