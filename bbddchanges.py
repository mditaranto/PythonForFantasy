import gspread
from oauth2client.service_account import ServiceAccountCredentials
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import requests
from bs4 import BeautifulSoup
import gspread
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


cred = credentials.Certificate("fantasyServiceAccount.json")
firebase_admin.initialize_app(cred)

# Get a database reference
db = firestore.client()

jugadoresRef = db.collection(u'jugadores')



def puntosa0():
    # Loop through the players and change puntos to a list with 0
    for jugador in jugadoresRef.stream():
        doc_ref = db.collection(u'jugadores').document(jugador.id)
        doc_ref.set({u'puntos': [0]}, merge=True)  # Update or create document

# Función para eliminar el primer valor 0 de la lista de puntos
def eliminar_puntos_cero():
    jugadores_ref = db.collection(u'jugadores')  # Referencia a la colección 'jugadores'
    
    # Obtener todos los documentos de la colección 'jugadores'
    jugadores_docs = jugadores_ref.get()

    for jugador_doc in jugadores_docs:
        jugador_data = jugador_doc.to_dict()  # Obtener los datos del documento como un diccionario
        entienda = jugador_data.get('puntos', None)  # Obtener la lista de puntos, o una lista vacía si no existe

        # Verificar si el ultimo valor y eliminarlo
        if len(entienda) > 4:
            # Eliminar el ultimo valor de la lista
            entienda.pop()
            # Actualizar el documento con la nueva lista de puntos
            jugadores_ref.document(jugador_doc.id).update({
                'puntos': entienda,
            })
            print(f"Puntos actualizados para el jugador {jugador_doc.id}")

def actualizar_puntos_equipo(equipo_objetivo, multiplicador=1.4):
    """
    Modifica la base de datos para multiplicar las últimas 2 entradas de puntos de los jugadores
    de un equipo específico por un multiplicador (por defecto 1.4).
    
    :param equipo_objetivo: El nombre del equipo al que pertenecen los jugadores que se modificarán.
    :param multiplicador: El valor por el que se multiplicarán las últimas 2 entradas de puntos.
    """
    jugadores_ref = db.collection(u'jugadores')
    
    # Obtener todos los jugadores del equipo específico
    jugadores_query = jugadores_ref.where(u'equipo', u'==', equipo_objetivo).stream()

    for jugador in jugadores_query:
        jugador_data = jugador.to_dict()
        puntos = jugador_data.get('puntos', [])

        if len(puntos) >= 2:
            # Modificar las últimas dos entradas de la lista
            puntos[-2:] = [p * multiplicador for p in puntos[-2:]]

            # Actualizar en la base de datos
            jugadores_ref.document(jugador.id).update({u'puntos': puntos})
            print(f"Puntos actualizados para {jugador_data['nombre']} - Últimos dos puntos multiplicados por {multiplicador}")
        else:
            print(f"El jugador {jugador_data['nombre']} no tiene suficientes puntos para modificar")


def actualizar_ofertado():
    jugadores_ref = db.collection(u'jugadores')
    
    # Obtener todos los documentos de la colección 'jugadores'
    jugadores_docs = jugadores_ref.get()

    for jugador_doc in jugadores_docs:
        jugador_data = jugador_doc.to_dict()  # Obtener los datos del documento como un diccionario
        userId = jugador_data.get('userId', None)  # Obtener el userId, o None si no existe
        equipo = jugador_data.get('equipo', None)  # Obtener el equipo del jugador

        if userId or equipo == 'VKE' or equipo =='100T' or equipo == 'R7' or equipo == 'SHG':
            # Actualizar el documento con un nuevo userId
            jugadores_ref.document(jugador_doc.id).update({
                'ofertado': True
            })
            print(f"UserId actualizado para el jugador {jugador_doc.id}")
        else :
            jugadores_ref.document(jugador_doc.id).update({
                'ofertado': False
            })

def añadir_cero_jugadores():
    jugadores_ref = db.collection(u'jugadores')
    
    # Obtener todos los documentos de la colección 'jugadores'
    jugadores_docs = jugadores_ref.get()

    for jugador_doc in jugadores_docs:
        jugador_data = jugador_doc.to_dict()  # Obtener los datos del documento como un diccionario
        puntos = jugador_data.get('puntos', [])  # Obtener la lista de puntos, o una lista vacía si no existe

        # Si la longitud de puntos es mayor que 4, eliminar el último valor (el quinto)
        if len(puntos) > 4:
            puntos.pop()  # Eliminar el último elemento de la lista

        if len(puntos) < 4:
            # Añadir un 0 al principio de la lista de puntos
            updated_puntos_list = puntos + [0]

            # Actualizar el documento con la nueva lista de puntos
            jugadores_ref.document(jugador_doc.id).update({
                'puntos': updated_puntos_list
            })
            print(f"Puntos actualizados para el jugador {jugador_doc.id}")


def actualizar_jugador(nombre, equipo, valor, posicion):
   # Referencia al documento del jugador usando su nombre como ID
    jugador_ref = db.collection('jugadores').document(nombre)
    
    # Verificar si el jugador ya existe (comprobando si tiene datos)
    jugador_existente = jugador_ref.get()

    if jugador_existente.exists:
        # Si el jugador ya existe, actualizamos solo el valor
        jugador_ref.update({'precio': valor})
        print(f'Jugador {nombre} actualizado con nuevo valor: {valor}')
    else:
        # Si no existe, agregar un nuevo documento con todos los datos
        nuevo_jugador = {
            'nombre': nombre,
            'equipo': equipo,
            'precio': valor,
            'posicion': posicion,
            'puntos': [0],  # Inicializar la lista de puntos,
            'entienda': False,
            'pujas': 0,
            'ofertado': False,
            'foto': 'https://psicoaroha.es/wp-content/uploads/2021/12/perfil-empty.png'
        }
        jugador_ref.set(nuevo_jugador)
        print(f'Jugador {nombre} agregado con valor: {valor}')

# Obtener datos de Google Sheets
def leer_jugadores():

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet = client.open("Pts Fantasy Automatized") 

    sheet = spreadsheet.worksheet("Jugadores")  # Obtener la primera hoja del documento
    # Empezamos a leer desde la fila 6 (donde está el primer jugador)
    fila_inicial = 21
    for fila in range(fila_inicial, sheet.row_count + 1):

       
        # Obtener datos de la fila actual
        nombre = sheet.cell(fila, 16).value  # Columna D para el nombre del jugador
        if not nombre:  # Si no hay nombre, asumimos que es el final de la lista
            break

        posicion = sheet.cell(fila, 15).value  # Columna C para la posición
        valor = sheet.cell(fila, 17).value  # Columna E para el valor
        equipo = sheet.cell(fila_inicial-2, 16).value  # La fila 5 contiene los nombres de los equipos

        # Asegurarse de que todos los campos estén completos
        if nombre and valor and equipo:
            # Convertir valor a número si es necesario
            valor = int(valor)*1000

            # Llamar a la función para actualizar o insertar jugador en Firestore
            actualizar_jugador(nombre, equipo, valor, posicion)

# Función para agregar el campo 'valorventa' a todos los jugadores
def agregar_valorventa_a_todos():
    # Referencia a la colección de jugadores
    jugadores_ref = db.collection('jugadores')
    
    # Obtener todos los documentos de la colección
    jugadores = jugadores_ref.stream()

    for jugador in jugadores:
        jugador_data = jugador.to_dict()

        # Verificar si ya tiene el campo 'valorventa'
        if 'valorventa' not in jugador_data:
            precio_actual = jugador_data.get('precio', 0)  # Obtener el valor de 'precio'
            
            # Actualizar el documento agregando el campo 'valorventa'
            jugadores_ref.document(jugador.id).update({
                'precioventa': precio_actual
            })
            print(f'Se ha añadido el campo "valorventa" para el jugador {jugador.id} con valor {precio_actual}')
        else:
            print(f'El jugador {jugador.id} ya tiene el campo "valorventa"')



def añadir_userId_jugadores(jugadores, userId):
    jugadores_ref = db.collection(u'jugadores')
    
    # Obtener todos los documentos de la colección 'jugadores'
    jugadores_docs = jugadores_ref.get()

    for jugador_doc in jugadores_docs:
        jugador_data = jugador_doc.to_dict()  # Obtener los datos del documento como un diccionario
        nombre = jugador_data.get('nombre', '')  # Obtener el nombre del jugador

        if nombre in jugadores:
            # Actualizar el documento con el userId
            jugadores_ref.document(jugador_doc.id).update({
                'userId': userId
            })
            print(f"UserId actualizado para el jugador {jugador_doc.id}")

def añadir_jugador(nombre, precio, equipo, posicion):
    jugador_ref = db.collection(u'jugadores').document(nombre)
    
    # Verificar si el jugador ya existe
    jugador_existente = jugador_ref.get()

    if jugador_existente.exists:
        print(f"El jugador {nombre} ya existe en la base de datos.")
    else:
        nuevo_jugador = {
            'nombre': nombre,
            'precio': precio,
            'equipo': equipo,
            'posicion': posicion,
            'puntos': [0,0,0,0],
            'entienda': False,
            'pujas': 0,
            'ofertado': False,
            'precioventa' : precio,
            'foto': 'https://psicoaroha.es/wp-content/uploads/2021/12/perfil-empty.png'
        }
        jugador_ref.set(nuevo_jugador)
        print(f"Jugador {nombre} agregado con éxito a la base de datos.")

def actualizar_puntos_usuarios_por_todas_las_jornadas():
    puntos_ref = db.collection("puntos")

    try:
        # Obtener todos los documentos de "puntos"
        puntos_snapshot = puntos_ref.get()

        puntos_consolidados = {}

        # Filtrar los documentos que tienen "puntosdados" en true y acumular los puntos por usuario
        for doc in puntos_snapshot:
            doc_data = doc.to_dict()
            puntos_dados = doc_data.get("puntosdados", False)
            user_id = doc_data.get("userId")
            puntos = doc_data.get("puntos", 0.0)

            if puntos_dados and user_id:
                # Acumulamos los puntos por usuario
                if user_id in puntos_consolidados:
                    puntos_consolidados[user_id] += puntos
                else:
                    puntos_consolidados[user_id] = puntos

        # Ahora actualizamos los puntos de cada usuario en la colección "users"
        for user_id, total_puntos in puntos_consolidados.items():
            user_ref = db.collection("users").document(user_id)
            user_ref.update({
                'puntos': total_puntos  # Incrementar los puntos en la base de datos
            })
            print(f"Puntos del usuario {user_id} actualizados correctamente.")

    except Exception as e:
        print(f"Error al actualizar los puntos de los usuarios: {e}")

actualizar_ofertado()