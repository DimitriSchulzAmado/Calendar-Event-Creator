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
    def _get_credentials():
        """Obtém e gerencia as credenciais do Google Calendar"""
        creds = None
        credentials_json = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        token_json = os.getenv("GOOGLE_TOKEN")

        if not creds and token_json:
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(token_json), SCOPES
                )
                print("Token carregado da variável de ambiente")
            except Exception as e:
                print(f"Erro ao carregar token da variável de ambiente: {e}")
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    GoogleCalendar._save_token(creds)
                    print("Token renovado com sucesso")
                except Exception as e:
                    print(f"Erro ao renovar token: {e}")
                    creds = None

            if not creds or not creds.valid:
                if credentials_json:
                    try:
                        creds_info = json.loads(credentials_json)
                        flow = InstalledAppFlow.from_client_config(creds_info, SCOPES)
                        creds = flow.run_local_server(port=0)

                        GoogleCalendar._save_token(creds)
                        print("Nova autenticação realizada com sucesso")
                    except Exception as e:
                        raise Exception(f"Erro na autenticação: {e}")
                else:
                    raise Exception(
                        "Credenciais do Google Calendar não encontradas nas variáveis de ambiente."
                    )

        return creds

    @staticmethod
    def _save_token(creds):
        """Salva o token em arquivo para persistência"""
        try:
            token_data = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            }

            os.environ["GOOGLE_TOKEN"] = json.dumps(token_data)
            print("Token atualizado na variável de ambiente GOOGLE_TOKEN")
        except Exception as e:
            print(f"Erro ao salvar token: {e}")

    @staticmethod
    def create_event(
        summary: str,
        location: str,
        description: str,
        start_time: str,
        end_time: str,
        remind: int = 5,
        type: str = "Common Tasks",
    ):
        # Validação de dados obrigatórios
        if not summary:
            raise ValueError("O campo 'summary' é obrigatório")
        if not start_time:
            raise ValueError("O campo 'start_time' é obrigatório")
        if not end_time:
            raise ValueError("O campo 'end_time' é obrigatório")

        try:
            creds = GoogleCalendar._get_credentials()
        except Exception as e:
            raise Exception(f"Erro na autenticação: {e}")

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

            # Determina o calendário a ser usado
            calendar_id = GoogleCalendar._get_calendar_id(service, type)

            # Cria o evento
            created_event = (
                service.events().insert(calendarId=calendar_id, body=event).execute()
            )

            print(f"Evento criado com sucesso: {created_event.get('htmlLink')}")
            return created_event

        except HttpError as error:
            error_details = GoogleCalendar._parse_http_error(error)
            print(f"Erro HTTP: {error_details}")

            if error_details.get("code") == 401:
                # Token inválido, tenta nova autenticação
                print("Token inválido, tentando nova autenticação...")
                try:
                    creds = GoogleCalendar._get_credentials()
                    service = build("calendar", "v3", credentials=creds)
                    created_event = (
                        service.events()
                        .insert(calendarId="primary", body=event)
                        .execute()
                    )
                    print(
                        f"Evento criado após nova autenticação: {created_event.get('htmlLink')}"
                    )
                    return created_event
                except Exception as retry_error:
                    raise Exception(
                        f"Falha na nova tentativa de autenticação: {retry_error}"
                    )
            else:
                raise Exception(
                    f"Erro ao criar evento: {error_details.get('message', str(error))}"
                )

        except Exception as error:
            print(f"Erro geral: {error}")
            raise Exception(f"Erro ao criar evento: {str(error)}")

    @staticmethod
    def _get_calendar_id(service, calendar_type):
        """Determina o ID do calendário baseado no tipo"""
        if not calendar_type:
            return "primary"

        try:
            calendars = service.calendarList().list().execute()

            for calendar in calendars.get("items", []):
                summary = calendar.get("summary", "") or ""
                if calendar_type.lower() in summary.lower():
                    calendar_id = calendar.get("id")
                    return calendar_id

            return "primary"

        except Exception as e:
            print(f"Erro ao buscar calendários: {e}. Usando calendário principal.")
            return "primary"

    @staticmethod
    def _parse_http_error(error):
        """Analisa erros HTTP e retorna informações estruturadas"""
        try:
            error_data = json.loads(error.content.decode())
            return {
                "code": error.resp.status,
                "message": error_data.get("error", {}).get("message", str(error)),
                "details": error_data,
            }
        except Exception:
            return {
                "code": getattr(error.resp, "status", 500),
                "message": str(error),
                "details": {},
            }
