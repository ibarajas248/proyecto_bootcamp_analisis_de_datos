import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime
import re

def clean_minute_format(gol):
    return gol.split('(')[0]
#dd

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
    year = 2023
    id_tabla_partido = 15000
    cambio_mes = False


    for numero in range(1, 39):
        url = f'https://colombia.as.com/resultados/futbol/francia/2023_2024/jornada/regular_a_{numero}'
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


                        if fecha.month == 1 and cambio_mes==False :  # January of the following year
                            year += 1  # Increment the year to 2025
                            fecha = fecha.replace(year=year)  # Update the date with the new year
                            cambio_mes= True

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

            #conexion localhost
            """
            conn = mysql.connector.connect(
                host='localhost',
                port=3310,
                user='root',
                password='',
                database='futbol'
            )
            
            """

            #conexión clever cloud

            conn = mysql.connector.connect(
                host='bnlrjjogqqtrux5dkhx3-mysql.services.clever-cloud.com',
                port=3306,
                user='ug9k8pdx4fu2lc9p',
                password='MiyaArHakCa5tGKIRcec',
                database='bnlrjjogqqtrux5dkhx3'
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

            #if numero == 1:
                #cursor.execute('DELETE FROM goles')
                #cursor.execute('DELETE FROM partidos')


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


def scraping_stadisticas(cursor, conn, estadistica, partido_id):
    print("Iniciando scraping de estadísticas...")

    # URL de la página a scrapear
    url = estadistica

    try:
        # Realiza la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla

        # Analiza el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Crear la tabla si no existe
        create_table_query = """
            CREATE TABLE IF NOT EXISTS estadisticas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_partido INT NULL,
                equipo VARCHAR(70) NULL,
                intervenciones_portero INT,
                tarjetas_amarillas INT NULL,
                tarjeta_roja INT NULL,
                faltas_recibidas INT NULL,
                faltas_cometidas INT NULL,
                balones_perdidos INT NULL, 
                balones_recuperados INT NULL,
                fuera_de_juego_en_contra INT NULL,
                FOREIGN KEY (id_partido) REFERENCES partidos(id) ON DELETE CASCADE
            )
        """
        cursor.execute(create_table_query)

        # Extraer los nombres de los equipos
        teams = soup.find_all('a', class_='team-banner')
        team_names = [team.find('span', class_='team-name').text.strip() for team in teams]

        # Extraer las estadísticas
        stats = {}
        stats['intervenciones_portero'] = [int(span.text) for span in
                                           soup.find_all('div', class_='stat-wr')[1].find_all('span',
                                                                                              class_='stat-val')]
        stats['tarjetas_amarillas'] = [int(span.text) for span in
                                       soup.find_all('div', class_='stat-wr')[2].find_all('span', class_='stat-val')]
        stats['tarjetas_rojas'] = [int(span.text) for span in
                                   soup.find_all('div', class_='stat-wr')[3].find_all('span', class_='stat-val')]

        stats['faltas_recibidas'] = [int(span.text) for span in
                                     soup.find_all('div', class_='stat-wr')[5].find_all('span', class_='stat-val')]

        stats['faltas_cometidas'] = [int(span.text) for span in
                                     soup.find_all('div', class_='stat-wr')[5].find_all('span', class_='stat-val')]
        stats['balones_perdidos'] = [int(span.text) for span in
                                     soup.find_all('div', class_='stat-wr')[6].find_all('span', class_='stat-val')]
        stats['balones_recuperados'] = [int(span.text) for span in
                                        soup.find_all('div', class_='stat-wr')[7].find_all('span', class_='stat-val')]
        stats['fueras_de_juego_en_contra'] = [int(span.text) for span in
                                              soup.find_all('div', class_='stat-wr')[8].find_all('span',
                                                                                                 class_='stat-val')]

        # Insertar las estadísticas en la base de datos
        for i in range(2):  # Asumiendo que siempre hay dos equipos
            equipo = team_names[i]
            intervenciones_portero = stats['intervenciones_portero'][i]
            tarjetas_amarillas = stats['tarjetas_amarillas'][i]
            tarjetas_rojas = stats['tarjetas_rojas'][i]
            faltas_recibidas = stats['faltas_recibidas'][i]
            faltas_cometidas = stats['faltas_cometidas'][i]
            balones_perdidos = stats['balones_perdidos'][i]
            balones_recuperados = stats['balones_recuperados'][i]
            fueras_de_juego_en_contra = stats['fueras_de_juego_en_contra'][i]

            insert_query = """
                INSERT INTO estadisticas (
                    id_partido, equipo, intervenciones_portero, tarjetas_amarillas, 
                    tarjeta_roja,faltas_recibidas, faltas_cometidas, balones_perdidos, 
                    balones_recuperados, fuera_de_juego_en_contra
                ) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                partido_id, equipo, intervenciones_portero, tarjetas_amarillas,
                tarjetas_rojas,faltas_recibidas, faltas_cometidas, balones_perdidos,
                balones_recuperados, fueras_de_juego_en_contra
            ))

        conn.commit()
        print("Datos insertados correctamente.")

        return stats

    except requests.RequestException as e:
        print(f"Error al realizar la solicitud HTTP: {e}")
        return None


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

            #Extrae URL
            nav = soup_partido.find('nav', class_='nav-hor-wr sh')
            if nav:
                # Encontrar todos los elementos <a> dentro del nav
                links = nav.find_all('a')

                for link in links:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    if text == "ESTADÍSTICAS":
                        estadistica = "https://colombia.as.com/" + href;
                        print(f"Texto: {text}, Enlace: {estadistica}")
                        scraping_stadisticas(cursor, conn, estadistica,partido_id)



        else:
            print(f'Error al realizar la solicitud para {partido_url}: {response_partido.status_code}')

insertPartidos()
