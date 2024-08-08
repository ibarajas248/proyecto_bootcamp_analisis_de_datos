import requests
from bs4 import BeautifulSoup

# URL de la página a scrape
url = "https://colombia.as.com/resultados/futbol/francia/2018_2019/directo/regular_a_20_241806/estadisticas/"

# Realizar la petición a la página
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Función para extraer datos de estadísticas
def extract_stats(soup):

    # Equipos
    teams = soup.find_all('a', class_='team-banner')
    team_names = [team.find('span', class_='team-name').text for team in teams]
    stats['teams'] = team_names

    # Posesión
    possession = soup.find('div', class_='stat-bar-xl')
    possession_values = [span.text for span in possession.find_all('span', class_='stat-val')]
    stats['possession'] = possession_values

    # Intervenciones del portero
    goalkeeper_interventions = soup.find_all('div', class_='stat-wr')[1]
    goalkeeper_values = [span.text for span in goalkeeper_interventions.find_all('span', class_='stat-val')]
    stats['goalkeeper_interventions'] = goalkeeper_values


    # Tarjetas amarillas
    yellow_cards = soup.find_all('div', class_='stat-wr')[2]
    yellow_card_values = [span.text for span in yellow_cards.find_all('span', class_='stat-val')]
    stats['yellow_cards'] = yellow_card_values

    # Tarjetas rojas
    red_cards = soup.find_all('div', class_='stat-wr')[3]
    red_card_values = [span.text for span in red_cards.find_all('span', class_='stat-val')]
    stats['red_cards'] = red_card_values

    # Faltas recibidas
    fouls_received = soup.find_all('div', class_='stat-wr')[4]
    fouls_received_values = [span.text for span in fouls_received.find_all('span', class_='stat-val')]
    stats['fouls_received'] = fouls_received_values

    # Faltas cometidas
    fouls_committed = soup.find_all('div', class_='stat-wr')[5]
    fouls_committed_values = [span.text for span in fouls_committed.find_all('span', class_='stat-val')]
    stats['fouls_committed'] = fouls_committed_values

    # Balones perdidos
    lost_balls = soup.find_all('div', class_='stat-wr')[6]
    lost_balls_values = [span.text for span in lost_balls.find_all('span', class_='stat-val')]
    stats['lost_balls'] = lost_balls_values

    # Balones recuperados
    recovered_balls = soup.find_all('div', class_='stat-wr')[7]
    recovered_balls_values = [span.text for span in recovered_balls.find_all('span', class_='stat-val')]
    stats['recovered_balls'] = recovered_balls_values

    # Fueras de juego en contra
    offsides_against = soup.find_all('div', class_='stat-wr')[8]
    offsides_values = [span.text for span in offsides_against.find_all('span', class_='stat-val')]
    stats['offsides_against'] = offsides_values

    return stats

# Extraer las estadísticas
stats = extract_stats(soup)
print(stats)
