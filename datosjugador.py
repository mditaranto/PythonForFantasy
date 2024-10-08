import requests
import time
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datosequipo import datosequipo

def datosjugador(idpartido, partido, equipoizq):
    # URL del partido
    url = f'https://gol.gg/game/stats/{idpartido}/page-fullstats/'
    urlfk = f'https://gol.gg/game/stats/{idpartido}/page-timeline/'

    # Headers para simular un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # Realizamos la solicitud con los headers
    response = requests.get(url, headers=headers)
    responsefk = requests.get(urlfk, headers=headers)

    if responsefk.status_code == 200:
        soupfk = BeautifulSoup(responsefk.text, 'html.parser')
    else:
        print(f"Error {responsefk.status_code}: No se pudo acceder a la página.")

    # Comprobamos si la solicitud fue exitosa
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Error {response.status_code}: No se pudo acceder a la página.")

    # Initialize empty lists for player statistics
    players_data = []

    # Comprobamos si el equipo sigue en el lado azul
    team_blue_status = soupfk.find('div', class_='blue-line-header')
    team_blue = team_blue_status.find('a').text.strip()
    if equipoizq == team_blue:
        ladoazul = True
    else:
        ladoazul = False

    # Obtiene el numero del game
    game_number = soup.find('li', class_='nav-item game-menu-button-active').text.strip()

    # Obtiene el nombre del jugador first kill
    table = soupfk.find('table', class_='nostyle timeline trhover')
    all_tr = table.find_all('tr')

    player_name = None
    for tr in all_tr:
        tds = tr.find_all('td')
        # Revisa si este 'tr' contiene un 'img' con el 'kill-icon'
        if any(td.find('img', {'src': '../_img/kill-icon.png'}) for td in tds):
            # Si el 'tr' tiene suficientes 'td' y hay un nombre de jugador en el tercer 'td'
            if len(tds) > 2 and tds[2].text.strip():
                player_name = tds[2].text.strip()  # Obtiene el nombre del jugador
                break

    # Extract the rows from the table body
    rows = soup.select('tr')

    # Variables to hold different sections of the stats
    player_names = []
    player_roles = []
    player_kills = []
    player_deaths = []
    player_assists = []
    player_csm = []

    # Extract data from each row of interest
    for i, row in enumerate(rows):
        columns = row.find_all('td')
        
        if i == 1:  # Player names
            player_names = [col.find('b').text.strip() for col in columns if col.find('b')]
            
        elif i == 2:  # Player roles
            player_roles = [col.text.strip() for col in columns[1:]]  # Skip first TD
            
        elif i == 4:  # Kills
            player_kills = [col.text.strip() for col in columns[1:]]  # Skip first TD
            
        elif i == 5:  # Deaths
            player_deaths = [col.text.strip() for col in columns[1:]]  # Skip first TD
            
        elif i == 6:  # Assists
            player_assists = [col.text.strip() for col in columns[1:]]  # Skip first TD
            
        elif i == 11:  # CSM
            player_csm = [col.text.strip() for col in columns[1:]]  # Skip first TD

    # Combine data into player stats
    for idx in range(len(player_names)):
        player = {
            'Nombre': player_names[idx],
            'Posición': player_roles[idx],
            'Kills': player_kills[idx],
            'Deaths': player_deaths[idx],
            'Assists': player_assists[idx],
            'CSM': player_csm[idx]
        }
        players_data.append(player)



    # Google Sheets API authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet = client.open("Pts Fantasy Automatized")  # Replace with your spreadsheet name
    # Step 3: Access the newly created sheet
    spreadsheet_id = spreadsheet.id
    sheet = spreadsheet.worksheet(partido)  # The newly renamed sheet

    batch_data = [] 
    batch_data2 = []

    # Update the sheet with the scraped data
    for i, player in enumerate(players_data):
        if (game_number == 'Game 1' and i < 5):
            if ladoazul:
                row = i + 4
            else:
                row = i + 36
        elif (game_number == 'Game 2' and i < 5):
            if ladoazul:
                row = i + 10
            else:
                row = i + 42
        elif (game_number == 'Game 3' and i < 5):
            if ladoazul:
                row = i + 16
            else:
                row = i + 48
        elif (game_number == 'Game 4' and i < 5):
            if ladoazul:
                row = i + 22
            else:
                row = i + 54
        elif (game_number == 'Game 5' and i < 5):
            if ladoazul:
                row = i + 28
            else:
                row = i + 60
        elif (game_number == 'Game 1' and i >= 5):
            if ladoazul:
                row = i + 31
            else:
                row = i - 1
        elif (game_number == 'Game 2' and i >= 5):  
            if ladoazul:
                row = i + 37
            else:
                row = i + 5
        elif (game_number == 'Game 3' and i >= 5):
            if ladoazul:
                row = i + 43
            else:
                row = i + 11
        elif (game_number == 'Game 4' and i >= 5):
            if ladoazul:
                row = i + 49
            else:
                row = i + 17
        elif (game_number == 'Game 5' and i >= 5):
            if ladoazul:
                row = i + 55
            else:
                row = i + 23

        if player['Nombre'] == player_name:
            fk = 1
        else:
            fk = 0

        # Create row data
        row_data = [
            player['Nombre'], 
            player['Posición'], 
            0, 
            0, 
            fk, 
            player['Kills'], 
            player['Deaths'], 
            player['Assists'], 
            player['CSM']
        ]

        # Append data to batch request
        batch_data.append({
            'range': f'{partido}!B{row}:J{row}',  # Define the range to update
            'values': [row_data]  # List of values
        })

        if (i < 5 and ladoazul) or (i >= 5 and not ladoazul):
            batch_data2.append({
                'range': f'{partido}!Q{14+i}',  # Define the range to update
                'values': [[player['Nombre']]]  # List of values
            })
        elif (i < 5 and not ladoazul) or (i >= 5 and ladoazul):
            batch_data2.append({
                'range': f'{partido}!S{9+i}',  # Define the range to update
                'values': [[player['Nombre']]]  # List of values
            })


    # Prepare the batch update request body
    batch_update_data = {
        'valueInputOption': 'RAW',  # Specify how the input data should be interpreted
        'data': batch_data
    }

    batch_update_data2 = {
        'valueInputOption': 'RAW',  # Specify how the input data should be interpreted
        'data': batch_data2
    }

    request = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, 
        body=batch_update_data
    ).execute()

    request2 = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id, 
        body=batch_update_data2
    ).execute()
            
    datosequipo(idpartido, game_number, partido, ladoazul)