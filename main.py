import requests
import time
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datosequipo import datosequipo
from datosjugador import datosjugador
from modificarbbdd import modificarbbdd

if __name__ == "__main__":

    idpartido = 62755
    # URL de la página que contiene la tabla
    url = f'https://gol.gg/game/stats/{idpartido}/page-game/'  # Cambia esto por la URL real
    
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

    # Comprobamos si existen 2 o 3 partidos
    all_li = soup.find_all('li', class_='nav-item game-menu-button')
    game2 = False
    game3 = False
    game4 = False
    game5 = False

    if len(all_li) >= 3:
        game2 = True
    if len(all_li) >= 4:
        game3 = True
    if len(all_li) >= 5:
        game4 = True
    if len(all_li) >= 6:
        game5 = True

    # Cogemos el equipo en el lado azul
    team_blue_status = soup.find('div', class_='blue-line-header')
    team_blue = team_blue_status.find('a').text.strip()
  

    # Google Sheets API authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open your Google Sheet
    spreadsheet = client.open("Pts Fantasy Automatized")  # Replace with your spreadsheet name

    # Step 1: Copy a template sheet (e.g., "Plantilla")
    template_sheet = spreadsheet.worksheet("Plantilla")
    partido = soup.find('h1').text.strip()
    new_sheet = template_sheet.duplicate(new_sheet_name=partido)
    sheet = spreadsheet.worksheet(partido)

    datosjugador(idpartido, partido, team_blue)
    sheet.update_cell(12, 18, "1")
    if game2:
        datosjugador(idpartido + 1, partido, team_blue)
        sheet.update_cell(12, 18, "2")
        if game3:
            datosjugador(idpartido + 2, partido, team_blue)
            sheet.update_cell(12, 18, "3")
            if game4:
                datosjugador(idpartido + 3, partido, team_blue)
                sheet.update_cell(12, 18, "4")
                if game5:
                    datosjugador(idpartido + 4, partido, team_blue)
                    sheet.update_cell(12, 18, "5")
                
    modificarbbdd(partido)
           
       