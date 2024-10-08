import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


partido = "Dplus KIA vs LNG Esports"
# Google Sheets API authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet
spreadsheet = client.open("Pts Fantasy Automatized")
sheet = spreadsheet.worksheet(partido)

cred = credentials.Certificate("fantasyServiceAccount.json")
firebase_admin.initialize_app(cred)

# Get a database reference
db = firestore.client()

# Batch write to Firestore
batch = db.batch()

for i in range(14, 19):  # Rows 14-18 for the first team
    player_name = sheet.cell(i, 17).value  # Names in column Q (17)
    points = sheet.cell(i, 18).value  # Points in column R (18)

    if player_name and points:  # Check if the name and points are not empty
        doc_ref = db.collection(u'jugadores').document(player_name)  # Use player name as document ID

        # Get the current points list
        current_data = doc_ref.get()
        current_points_list = current_data.to_dict().get('puntos', [])  # Default to empty list if not found

        # Add the new points to the end of the list
        current_points_list.append(float(points))

        # Update the document with the new points list
        batch.set(doc_ref, {u'puntos': current_points_list}, merge=True)


for i in range(14, 19):  # Rows 14-18 for the second team
    player_name = sheet.cell(i, 19).value  # Names in column S (19)
    points = sheet.cell(i, 20).value  # Points in column T (20)

    if player_name and points:  # Check if the name and points are not empty
        doc_ref = db.collection(u'jugadores').document(player_name)  # Use player name as document ID

        # Get the current points list
        current_data = doc_ref.get()
        current_points_list = current_data.to_dict().get('puntos', [])  # Default to empty list if not found

        # Add the new points to the end of the list
        current_points_list.append(float(points))

        # Update the document with the new points list
        batch.set(doc_ref, {u'puntos': current_points_list}, merge=True)

# Commit the batch update to Firestore
batch.commit()
print("All player points updated successfully.")
