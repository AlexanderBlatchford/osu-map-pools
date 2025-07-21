import os.path

import csv
import time
import emoji
import re

from enum import Enum
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1Pm1ihvelNLk5hyAxDir5o8UgPuqE9CEsJ00jBv3OLs4"
RANGE = "!B7:F40"

# Escape single quotes and double quotes
def escape_str(string):
  string.replace("'", "\\'")
  string.replace('"', '\\"')
  return string

class blacklist_words(Enum):
  NOMOD = "nomod"
  HIDDEN = "hidden"
  HARDROCK = "hard rock"
  HALFTIME = "half time"
  DOUBLETIME = "double time" 
  FREEMOD = "free mod"
  TIEBREAKER = "tiebreaker"

def sanitise_text(text):
    text = emoji.replace_emoji(text, replace='')
    text = re.sub('[^a-zA-Z0-9\n\. ]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = text.replace("\\u2605", '')
    ''.join(e for e in text if e.isalnum())


def extract_pool(spreadsheet_id, range_name):
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow complete  s for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  # =========================== End Credentials ==============================

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
    sheet_names = [sheet['properties']['title'] for sheet in sheet_metadata['sheets']]

    result = (
        sheet
        .get(spreadsheetId=spreadsheet_id, ranges=[range_name], fields="sheets(data(rowData(values(formattedValue,hyperlink))))")
        .execute()
    )

    csv_string = ""
    metadata_num = 0
    blacklist_values = set(word.value for word in blacklist_words)

    for sheet in result["sheets"]:
      for data in sheet["data"]:
        for rowData in data["rowData"]:
          if (len(rowData) == 0):
            continue
          for value in rowData["values"]:
            if (value["formattedValue"] in blacklist_values):
              continue

            if (metadata_num == 6):
              metadata_num = 0
              csv_string += "\n"

            metadata_num += 1
            csv_string += escape_str(str(value["formattedValue"]))

            if (metadata_num == 6):
                continue
            csv_string += ","

            if (value.get("hyperlink")) == None:
              continue
            else:
              metadata_num += 1
              csv_string += escape_str(value["hyperlink"])
              csv_string += ","

    print(csv_string)
    return csv_string
    
  except HttpError as err:
    print(err)


# Returns a list of sheet ids
def extract_sheets(spreadsheet_id):
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow complete  s for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  # =========================== End Credentials ==============================

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    sheet_metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
    sheet_names = [sheet['properties']['title'] for sheet in sheet_metadata['sheets']]

    return sheet_names

  except HttpError as err:
    print(err)


def write_to_csv(sheet_title, pool_data):
  with open(rf".\mappools\{sheet_title}.csv", 'w', newline='') as csvfile:

      csv_writer = csv.writer(csvfile)

      lines = pool_data.split('\n')
      for line in lines:
          fields = line.split(',')
          csv_writer.writerow(fields)



def main():
  sheets = extract_sheets(SPREADSHEET_ID)
  print(sheets)
  for sheet in sheets:
    if (sheet == "pool index" or sheet == "Format"):
      continue
    print(f"Sheet: {sheet}")
    sheet_title_range = sheet
    sheet_title_range += RANGE # Sheet title + Range
    pool = extract_pool(SPREADSHEET_ID, sheet_title_range)
    sheet += "Pool"
    sanitise_text(sheet)

    # if "??" in sheet: #TODO: fix this laters
    #   print("DID THIS EVEN HAPPEN?")
    #   continue

    print(f"Pool {pool}")

    try:
      write_to_csv(sheet, pool)
    except OSError as e:
      print(f"An OS file structure occurred: {e}")
      continue
    except UnicodeEncodeError as e:
      print(f"A Unicode Error occurred: {e}")
      continue

    time.sleep(1)

    # TODO: Add beatmap id stuff



if __name__ == "__main__":
  main()