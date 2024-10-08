import requests
from bs4 import BeautifulSoup
import gspread
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

def datosequipo(idpartido, game_number, partido, ladoazul):
    # Simulación de cargar el HTML directamente
    url = f'https://gol.gg/game/stats/{idpartido}/page-game/'  # Reemplaza con el HTML de la página
    # Headers para simular un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    # Realizamos la solicitud con los headers
    response = requests.get(url, headers=headers)

    # Comprobamos si la solicitud fue exitosa
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Error {response.status_code}: No se pudo acceder a la página.")

    # Extraer el Game Time
    game_time = soup.find('div', class_='col-6 text-center').find('h1').text.strip()

    # Verificar qué equipo ganó (Movistar R7 es azul, 100 Thieves es rojo)
    team_blue_status = soup.find('div', class_='blue-line-header').text.strip()
    team_red_status = soup.find('div', class_='red-line-header').text.strip()

    # Determinar si ganó el equipo azul o el rojo
    if 'WIN' in team_blue_status:
        winner = 'Azul'
    elif 'WIN' in team_red_status:
        winner = 'Rojo'

    # Extraer los grubs de cada equipo
    alldivs = soup.find_all('div', class_='row pb-3')[1]
    cols = alldivs.find_all('div', class_='col-4 text-center')
    blue_grubs = cols[1].text.strip()
    red_grubs = cols[2].text.strip()

    # Extraer las Torres, Dragones y Nashors para cada equipo
    blue_stats = soup.find_all('span', class_='score-box blue_line')
    red_stats = soup.find_all('span', class_='score-box red_line')

    # Extraer Torres
    blue_towers = blue_stats[1].text.split()[-1]
    red_towers = red_stats[1].text.split()[-1]

    # Extraer Dragones
    blue_dragons = blue_stats[2].text.split()[-1]
    red_dragons = red_stats[2].text.split()[-1]

    # Extraer Nashors
    blue_nashors = blue_stats[3].text.split()[-1]
    red_nashors = red_stats[3].text.split()[-1]

    # Convertir el string de la hora en un entero
    game_time = int(game_time.split(':')[0])

    if (game_time > 30):
        vic30 = 0
    else:
        vic30 = 1

    # Google Sheets API authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    service = build('sheets', 'v4', credentials=creds)

    batch_data = []
    # Open your Google Sheet
    spreadsheet = client.open("Pts Fantasy Automatized")  # Replace with your sheet name
    spreadsheet_id = spreadsheet.id
    team_data = [
    {'range_col': 'K', 'nashors': blue_nashors, 'dragons': blue_dragons, 'grubs': blue_grubs, 'towers': blue_towers},  # Azul
    {'range_col': 'K', 'nashors': red_nashors, 'dragons': red_dragons, 'grubs': red_grubs, 'towers': red_towers}  # Rojo
]
    sheet = spreadsheet.worksheet(partido)  # The newly renamed sheet

    # Update the sheet with the scraped data
    for i in range (10):
        # Update the sheet with the scraped data
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
    
        victory = 1 if (winner == 'Azul' and i < 5) or (winner == 'Rojo' and i >= 5) else 0
        vic_value = vic30 if victory else 0

        # Actualizar victoria y vic30
        batch_data.extend([
            {'range': f'{partido}!D{row}', 'values': [[victory]]},  # Columna 4 (victoria)
            {'range': f'{partido}!E{row}', 'values': [[vic_value]]},  # Columna 5 (vic30)
        ])
        
        team_idx = 0 if i < 5 else 1
        batch_data.extend([
            {'range': f'{partido}!{team_data[team_idx]["range_col"]}{row}', 'values': [[team_data[team_idx]['nashors']]]},  # Col 11
            {'range': f'{partido}!L{row}', 'values': [[team_data[team_idx]['dragons']]]},  # Col 12
            {'range': f'{partido}!M{row}', 'values': [[team_data[team_idx]['grubs']]]},  # Col 13
            {'range': f'{partido}!N{row}', 'values': [[team_data[team_idx]['towers']]]},  # Col 14
        ])

    # Actualizar la hoja de cálculo con los datos extraídos
    batch_update_data = {'valueInputOption': 'RAW', 'data': batch_data}
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=batch_update_data
    ).execute()
        
