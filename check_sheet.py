import os
import sys
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Replace with your service account file path
SERVICE_ACCOUNT_FILE = "C:\\Users\\Leader\\PycharmProjects\\ai\\wallet\\service-account-key.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheet_data(spreadsheet_id, sheet_name, range_name):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    
    # First, get the list of sheets to verify the exact name
    spreadsheet = sheet.get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get('sheets', [])
    print("Available sheets:")
    for s in sheets:
        title = s['properties']['title']
        print(f"- {title}")
        if 'PROMT Temp: UX' in title:
            print(f"  ^^^ Found matching sheet: {title}")
    
    # Try to get data from the specified range
    try:
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'!{range_name}"
        ).execute()
        values = result.get('values', [])
        
        if not values:
            print('No data found in the specified range.')
        else:
            print(f"\nData from {sheet_name}!{range_name}:")
            for row in values:
                print(row)
    except Exception as e:
        print(f"Error accessing sheet data: {e}")

if __name__ == '__main__':
    # The ID and range of the spreadsheet
    SPREADSHEET_ID = '10Ro4U_7M0w3bEw_5nunNcy6hTB64oba4q5MAwjNNJPM'
    # Try to find the sheet with 'PROMT Temp: UX' in the name
    SHEET_NAME = 'PROMT Temp: UX Researсher'  # Will be updated if found
    RANGE_NAME = 'A1:Z100'  # Wide range to capture all potential data
    
    # First, list all sheets to find the exact name
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    spreadsheet = sheet.get(spreadsheetId=SPREADSHEET_ID).execute()
    
    # Update SHEET_NAME if we find a matching sheet
    for s in spreadsheet.get('sheets', []):
        title = s['properties']['title']
        if 'PROMT Temp: UX' in title:
            SHEET_NAME = title
            print(f"\nFound matching sheet: {SHEET_NAME}")
            break
    else:
        print("\nWarning: Could not find sheet with 'PROMT Temp: UX' in the name. Using default name.")
    
    try:
        get_sheet_data(SPREADSHEET_ID, SHEET_NAME, RANGE_NAME)
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying with a different sheet name variation...")
        # Try with a different variation of the sheet name
        SHEET_NAME = 'PROMT Temp: UX Researcher'  # Without the Cyrillic 'с'
        get_sheet_data(SPREADSHEET_ID, SHEET_NAME, RANGE_NAME)
