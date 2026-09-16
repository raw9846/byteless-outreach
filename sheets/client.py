from typing import Any, List

from googleapiclient.discovery import build

from .auth import get_credentials


def _service():
    return build("sheets", "v4", credentials=get_credentials())


def get_values(spreadsheet_id: str, range_: str) -> List[List[Any]]:
    service = _service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_
    ).execute()
    return result.get("values", [])


def update_values(spreadsheet_id: str, range_: str, values: List[List[Any]],
                   value_input_option: str = "USER_ENTERED") -> dict:
    service = _service()
    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption=value_input_option,
        body={"values": values},
    ).execute()


def clear_values(spreadsheet_id: str, range_: str) -> dict:
    service = _service()
    return service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id, range=range_, body={}
    ).execute()


def batch_update(spreadsheet_id: str, requests: List[dict]) -> dict:
    service = _service()
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests},
    ).execute()


def get_spreadsheet(spreadsheet_id: str) -> dict:
    service = _service()
    return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
