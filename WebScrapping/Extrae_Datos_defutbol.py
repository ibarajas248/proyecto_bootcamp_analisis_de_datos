import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import re

def clean_minute_format(gol):
    return gol.split('(')[0]

def extraer_nombre(scorer):
    match = re.match(r"([^\d]+)", scorer)
    if match:
        return match.group(1).strip()
    return scorer.strip()

def insertar_goleadores(cursor, conn, partido_id, scorers, equipo):
    for scorer in scorers:
        partes = scorer.rsplit(', ', 1)
        if len(partes) == 2:
            jugador = extraer_nombre(partes[0])
            minutos_str = partes[1].replace("'", '')

            minutos_list = minutos_str.split(', ')
            for minuto in minutos_list:
                if minuto:
                    cursor.execute(
                        'INSERT INTO goles (partido_id, jugador, equipo, minuto_marcaje) VALUES (%s, %s, %s, %s)',
                        (partido_id, jugador, equipo, int(minuto))
                    )
        else:
            jugador = extraer_nombre(partes[0])
            cursor.execute(
                'INSERT INTO goles (partido_id, jugador, equipo, minuto_marcaje) VALUES (%s, %s, %s, NULL)',
                (partido_id, jugador, equipo)
            )
    conn.commit()

def insertPartidos():
    year = 2024
    id_tabla_partido = 10000

    for numero in range(1, 30):
        url = f'https://colombia.as.com/resultados/futbol/francia/2018_2019/jornada/regular_a_{numero}'
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            partidos = []
            partidosConURL = []
            for partido in soup.find_all('li', class_='list-resultado'):
                local = partido.find('div', class_='equipo-local').find('span', class_='nombre-equipo').text

                try:
                    resultado_str = partido.find('div', class_='cont-resultado').find('a', class_='resultado')
                    if resultado_str:
                        resultado_str = resultado_str.text.strip()
                    else:
                        resultado_str = None

                    if not resultado_str:
                        resultado_str_sin_comenzar = partido.find('div', class_='cont-resultado no-comenzado').find('a', class_='resultado')
                        if resultado_str_sin_comenzar:
                            resultado_str = resultado_str_sin_comenzar.text.strip()
                        else:
                            resultado_str = None

                    if resultado_str:
                        try:
                            goles_local, goles_visitante = resultado_str.split('-')
                            goles_local = int(goles_local.strip())
                            goles_visitante = int(goles_visitante.strip())
                        except:
                            goles_local, goles_visitante = None, None
                    else:
                        goles_local, goles_visitante = None, None

                except AttributeError as e:
                    print(f"Error al obtener el resultado del partido: {e}")
                    resultado_str, partido_url = None, None
                    goles_local, goles_visitante = None, None

                try:
                    partido_url = partido.find('div', class_='cont-resultado').find('a', class_='resultado')['href']
                except:
                    partido_url = None



                #Extraer jornada
                cont_paginador = soup.find('div', class_='cont-paginador cf')

                if cont_paginador:
                    # Extraer todas las jornadas
                    jornadas = cont_paginador.find_all('span', class_='tit-jornada')

                    if jornadas:
                        # Suponiendo que la jornada actual es el primer elemento en la lista
                        jornada_actual = jornadas[0].get_text(strip=True)
                        jornada_numero = (re.search(r'\d+', jornada_actual)).group()


                    else:
                        jornada_numero= None
                else:
                    jornada_numero= None

                try:
                   # liga = soup.find('div', class_='header-seccion').find('h1', class_='tit-seccion').find('a').get_text(strip=True);
                    liga = soup.find('span', class_='tit-subtitle-info').get_text(strip=True);
                except:
                    liga = ("dato no encontrado")




                visitante = partido.find('div', class_='equipo-visitante').find('span', class_='nombre-equipo').text
                fecha_str = partido.find('div', class_='info-evento').find('span', class_='fecha').text.strip()
                match = re.search(r'([A-Z])-(\d{2}/\d{2} \d{2}:\d{2})', fecha_str)
                if match:
                    dia_semana = match.group(1)
                    fecha_hora = match.group(2)
                    fecha_str_con_año = f'{year} {fecha_hora}'
                    try:
                        fecha = datetime.strptime(fecha_str_con_año, '%Y %d/%m %H:%M')
                    except ValueError as e:
                        print(f'Error al convertir fecha {fecha_str_con_año}: {e}')
                        continue
                else:
                    print(f'Formato de fecha no reconocido para {fecha_str}')
                    continue

                partidos.append((id_tabla_partido, local, goles_local, goles_visitante, visitante, fecha, jornada_numero, liga))

                if partido_url:
                    partidosConURL.append(
                        (id_tabla_partido, local, goles_local, goles_visitante, visitante, fecha, partido_url))
                    print(f'Partido: {local} {goles_local} - {goles_visitante} {visitante} {fecha} {partido_url}')

                id_tabla_partido += 1

            conn = mysql.connector.connect(
                host='localhost',
                port=3310,
                user='root',
                password='',
                database='futbol'
            )
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS partidos (
                id INT primary key,
                local VARCHAR(255),
                goles_local INT,
                goles_visitante INT,
                visitante VARCHAR(255),
                fecha DATETIME,
                jornada VARCHAR(50) null,
                liga VARCHAR(100) null
            
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS goles (
                id INT AUTO_INCREMENT primary key,
                partido_id INT,
                jugador VARCHAR(255),
                equipo VARCHAR(255),
                minuto_marcaje INT,
                FOREIGN KEY (partido_id) REFERENCES partidos(id) ON DELETE CASCADE
            )
            ''')

            if numero == 1:
                cursor.execute('DELETE FROM goles')
                cursor.execute('DELETE FROM partidos')

            cursor.executemany(
                'INSERT INTO partidos (id, local, goles_local, goles_visitante, visitante, fecha, jornada,liga) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                partidos)
            try:
                procesar_goles(cursor, conn, partidosConURL)
            except Exception as e:
                print(f"No hay información de goles: {e}")

            conn.commit()
            conn.close()
            print('Partidos insertados exitosamente en la base de datos.')


def scraping_stadisticas(cursor, conn, estadistica):
    # URL de la página a scrapear
    url = 'estadistica'  # Reemplaza con la URL real

    # Realiza la solicitud HTTP
    response = requests.get(url)
    response.raise_for_status()  # Lanza una excepción si la solicitud falla

    # Analiza el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extrae las estadísticas
    stats = {}

    # Extrae posesión
    posesion_div = soup.find('div', class_='stat-posesion')  # Ajusta el selector
    if posesion_div:
        stats['posesion'] = posesion_div.find('span', class_='stat-val').text.strip()

    # Extrae intervenciones del portero
    intervenciones_div = soup.find('div', class_='stat-intervenciones')  # Ajusta el selector
    if intervenciones_div:
        stats['intervenciones'] = intervenciones_div.find('span', class_='stat-val').text.strip()

    # Extrae tarjetas amarillas
    tarjetas_amarillas_div = soup.find('div', class_='stat-tarjetas-amarillas')  # Ajusta el selector
    if tarjetas_amarillas_div:
        stats['tarjetas_amarillas'] = tarjetas_amarillas_div.find('span', class_='stat-val').text.strip()

    # Extrae tarjetas rojas
    tarjetas_rojas_div = soup.find('div', class_='stat-tarjetas-rojas')  # Ajusta el selector
    if tarjetas_rojas_div:
        stats['tarjetas_rojas'] = tarjetas_rojas_div.find('span', class_='stat-val').text.strip()

    # Extrae faltas recibidas
    faltas_recibidas_div = soup.find('div', class_='stat-faltas-recibidas')  # Ajusta el selector
    if faltas_recibidas_div:
        stats['faltas_recibidas'] = faltas_recibidas_div.find('span', class_='stat-val').text.strip()

    # Extrae faltas cometidas
    faltas_cometidas_div = soup.find('div', class_='stat-faltas-cometidas')  # Ajusta el selector
    if faltas_cometidas_div:
        stats['faltas_cometidas'] = faltas_cometidas_div.find('span', class_='stat-val').text.strip()

    # Extrae balones perdidos
    balones_perdidos_div = soup.find('div', class_='stat-balones-perdidos')  # Ajusta el selector
    if balones_perdidos_div:
        stats['balones_perdidos'] = balones_perdidos_div.find('span', class_='stat-val').text.strip()

    # Extrae balones recuperados
    balones_recuperados_div = soup.find('div', class_='stat-balones-recuperados')  # Ajusta el selector
    if balones_recuperados_div:
        stats['balones_recuperados'] = balones_recuperados_div.find('span', class_='stat-val').text.strip()

    # Extrae fueras de juego en contra
    fueras_de_juego_div = soup.find('div', class_='stat-fueras-de-juego')  # Ajusta el selector
    if fueras_de_juego_div:
        stats['fueras_de_juego'] = fueras_de_juego_div.find('span', class_='stat-val').text.strip()

    # Imprime los datos obtenidos
    print("Datos obtenidos:")
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Aquí puedes hacer la lógica para guardar los datos en la base de datos
    # cursor.execute('INSERT INTO estadisticas ...', (stats['posesion'], ...))
    # conn.commit()

    return stats


def procesar_goles(cursor, conn, partidosConURL):
    for partido_data in partidosConURL:
        partido_id = partido_data[0]
        partido_url = partido_data[6]
        response_partido = requests.get(partido_url)

        if response_partido.status_code == 200:
            soup_partido = BeautifulSoup(response_partido.content, 'html.parser')

            try:
                local_scorers_tag = soup_partido.find('div', class_='scr-hdr__team is-local').find('div', class_='scr-hdr__scorers')
                if local_scorers_tag:
                    local_scorers = [scorer.text.strip() for scorer in local_scorers_tag.find_all('span')]
                else:
                    local_scorers = []
                if not local_scorers:
                    teams = soup_partido.find_all('div', class_='team team-a')
                    for team in teams:
                        scorers_div = team.find('div', class_='scorers')
                        if scorers_div:
                            local_scorers = [scorer.text.strip() for scorer in scorers_div.find_all('span')]
                            break

                if local_scorers:
                    insertar_goleadores(cursor, conn, partido_id, local_scorers, partido_data[1])
                else:
                    print(f"No se encontraron goleadores locales en {partido_url}")

            except AttributeError:
                print(f"Error al extraer goleadores locales en {partido_url}")

            try:
                visitante_scorers_tag = soup_partido.find('div', class_='scr-hdr__team is-visitor')
                if visitante_scorers_tag:
                    scorers_div = visitante_scorers_tag.find('div', class_='scr-hdr__scorers')
                    if scorers_div:
                        visitante_scorers = [scorer.text.strip() for scorer in scorers_div.find_all('span')]
                    else:
                        visitante_scorers = []
                else:
                    visitante_scorers = []

                if not visitante_scorers:
                    teams = soup_partido.find_all('div', class_='team team-b')
                    for team in teams:
                        scorers_div = team.find('div', class_='scorers')
                        if scorers_div:
                            visitante_scorers = [scorer.text.strip() for scorer in scorers_div.find_all('span')]
                            break

                if visitante_scorers:
                    insertar_goleadores(cursor, conn, partido_id, visitante_scorers, partido_data[4])
                    print(f'Goleadores registrados para el partido ID {partido_id} ' + f'{partido_url}')
                else:
                    print(f"No se encontraron goleadores visitantes en {partido_url}")

            except AttributeError:
                print(f"Error al extraer goleadores visitantes en {partido_url}")

            try:
                nav = soup_partido.find('nav', class_='nav-hor-wr sh')
                if nav:
                    # Encontrar todos los elementos <a> dentro del nav
                    links = nav.find_all('a')

                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        if text=="ESTADÍSTICAS":
                            estadistica="https://colombia.as.com/"+href;
                            print(f"Texto: {text}, Enlace: {estadistica}")
                            scraping_stadisticas(cursor, conn,estadistica)

                            #print(f"Texto: {text}, Enlace: {href}")



            except:
                print("no se encuentran estadisticas")


        else:
            print(f'Error al realizar la solicitud para {partido_url}: {response_partido.status_code}')

insertPartidos()
