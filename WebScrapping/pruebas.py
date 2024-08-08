import requests
from bs4 import BeautifulSoup

# URL de la página web
url = 'https://colombia.as.com//resultados/futbol/francia/2018_2019/directo/regular_a_3_241635/estadisticas/'

# Hacer una solicitud HTTP GET a la URL
response = requests.get(url)

# Asegúrate de que la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML de la respuesta
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraer el nombre de los equipos y las estadísticas
    teams = soup.select('.team-banner')


    # Procesar y mostrar los nombres de los equipos y sus logos
    for team in teams:
        team_name = team.select_one('.team-name').get_text(strip=True)
        team_logo = team.select_one('.team-logo img')['src']
        print(f'Team Name: {team_name}')
        print(f'Team Logo URL: {team_logo}')

    stats = soup.select('.stat-wr')

    # Procesar y mostrar las estadísticas
    for stat in stats:
        stat_title = stat.select_one('.stat-tl').get_text(strip=True)
        values = stat.select('.stat-val')
        percentages = stat.select('.svg-progress')

        print(f'Statistic: {stat_title}')
        for value, percentage in zip(values, percentages):
            print(f'Value: {value.get_text(strip=True)}, Width: {percentage["width"]}')
        print('---')
else:
    print(f'Failed to retrieve the page. Status code: {response.status_code}')
