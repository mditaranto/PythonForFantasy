import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def modificarbbddtest(partido):
    # Google Sheets API authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open your Google Sheet
    spreadsheet = client.open("Prueba")
    sheet = spreadsheet.worksheet(partido)

    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

    # Get a database reference
    db = firestore.client()

        # Batch write to Firestore
    batch = db.batch()

    # Loop through the rows as specified
    for i in range(14, 19):  # Rows 14-18 for the first team
        player_name = sheet.cell(i, 17).value  # Names in column Q (17)
        points = sheet.cell(i, 18).value  # Points in column R (18)

        if player_name and points:  # Check if the name and points are not empty
            # Create a reference to the document
            doc_ref = db.collection(u'jugadores').document(player_name)  # Use player name as document ID
            batch.set(doc_ref, {u'puntos': float(points)}, merge=True)  # Update or create document

    for i in range(14, 19):  # Rows 14-18 for the second team
        player_name = sheet.cell(i, 19).value  # Names in column S (19)
        points = sheet.cell(i, 20).value  # Points in column T (20)

        if player_name and points:  # Check if the name and points are not empty
            # Create a reference to the document
            doc_ref = db.collection(u'jugadores').document(player_name)  # Use player name as document ID
            batch.set(doc_ref, {u'puntos': float(points)}, merge=True)  # Update or create document

    # Commit the batch update to Firestore
    batch.commit()
    print("All player points updated successfully.")
