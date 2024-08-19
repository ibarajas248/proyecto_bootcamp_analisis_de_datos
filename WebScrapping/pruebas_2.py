import requests
from bs4 import BeautifulSoup

# URL de la página web que deseas analizar
url = 'https://resultados.as.com/resultados/futbol/francia/2023_2024/directo/regular_a_1_443289/estadisticas/'

# Realiza la solicitud GET para obtener el contenido de la página
response = requests.get(url)

# Asegúrate de que la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encuentra los elementos con clase 'stat-val'
    possession_values = soup.find_all('span', class_='stat-val')

    # Extrae el texto de cada elemento
    team1_possession = possession_values[0].text
    team2_possession = possession_values[1].text

    print("Posesión del equipo 1:", team1_possession)
    print("Posesión del equipo 2:", team2_possession)
else:
    print(f"Error al acceder a la página: {response.status_code}")
