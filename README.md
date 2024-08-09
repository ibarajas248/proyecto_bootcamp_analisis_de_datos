# Informe de Web Scraping de Resultados y Estadísticas de Fútbol

## Introducción

Este informe describe el proceso de web scraping realizado para extraer resultados y estadísticas de partidos de fútbol de la liga francesa durante la temporada 2018-2019. El código desarrollado se encarga de obtener los datos de resultados, goleadores y estadísticas de los partidos, y almacenarlos en una base de datos MySQL. El propósito es analizar y organizar la información obtenida para su posterior análisis.

## Estructura del Código

### 1. Funciones Auxiliares

- **`clean_minute_format(gol)`**: Limpia el formato del minuto en el que se marcó el gol, extrayendo únicamente el minuto.
- **`extraer_nombre(scorer)`**: Extrae el nombre del jugador goleador eliminando cualquier número o formato innecesario.
- **`insertar_goleadores(cursor, conn, partido_id, scorers, equipo)`**: Inserta los datos de los goleadores en la tabla `goles` de la base de datos. Si un jugador tiene múltiples goles, se inserta un registro por cada minuto.

### 2. Función Principal: `insertPartidos()`

Esta función es el núcleo del proceso de scraping:

![image](https://github.com/user-attachments/assets/4937b49f-db88-4231-b71d-31b802c86b82)


- **Iteración por Jornadas**: Se recorren 29 jornadas de la liga, construyendo la URL de cada una y realizando la solicitud HTTP para obtener el HTML de la página.
- **Extracción de Información de Partidos**:
  - Se extraen los nombres de los equipos locales y visitantes, el resultado del partido, la fecha y la liga.
  - Se analiza el HTML para identificar si el partido ha comenzado, ha terminado o aún no ha iniciado.
  - Si el partido tiene un resultado disponible, se separan los goles de los equipos locales y visitantes.
- **Almacenamiento en la Base de Datos**:
  - Los datos del partido se almacenan en la tabla `partidos`.
  - Si se encuentra información sobre los goleadores, se llama a la función `procesar_goles()` para extraer y almacenar los goleadores en la tabla `goles`.
 
    ![image](https://github.com/user-attachments/assets/fbf36552-e079-481f-86e8-7bad88b97a8e)


### 3. Función de Procesamiento de Goles: `procesar_goles(cursor, conn, partidosConURL)`
![image](https://github.com/user-attachments/assets/94e57b54-f1dc-4fb2-93ed-1011511df6dd)


- **Extracción de Goleadores**: 
  - Utiliza la URL del partido para obtener los nombres de los jugadores que anotaron goles, tanto del equipo local como del visitante.
  - Se almacenan en la tabla `goles` con el minuto exacto del gol.
- **Extracción de Estadísticas**:
  - Navega a la sección de estadísticas de cada partido y extrae datos como intervenciones del portero, tarjetas amarillas, tarjetas rojas, faltas, balones perdidos y recuperados, y fuera de juego.
  - Los datos se almacenan en la tabla `estadisticas`.
 
    ![image](https://github.com/user-attachments/assets/b349ca89-1938-41d6-b79a-1a2999258c1f)


### 4. Función de Scraping de Estadísticas: `scraping_stadisticas(cursor, conn, estadistica, partido_id)`
![image](https://github.com/user-attachments/assets/bfc14843-faa3-4bc0-9012-4ece05d77c7f)

  
- **Extracción Detallada de Estadísticas**:
  - Se obtienen las estadísticas individuales de cada equipo, y se almacenan en la base de datos.
  - Esta función asegura que se capturen todos los aspectos relevantes del partido, más allá de los goles.
  ![image](https://github.com/user-attachments/assets/5a860708-1638-47ab-a6c4-d80b891ea1cf)


## Base de Datos

Se utilizan dos tablas principales en la base de datos MySQL:

- **Tabla `partidos`**: Almacena la información básica de cada partido, como los equipos, resultado, fecha, jornada y liga.
- **Tabla `goles`**: Contiene los detalles de los goles anotados en cada partido, incluyendo el nombre del jugador, el equipo y el minuto en que se marcó.
- **Tabla `estadisticas`**: Recoge diversas métricas de rendimiento para cada equipo en los partidos.

  ![image](https://github.com/user-attachments/assets/59099f2a-30f6-49a8-8211-6f091dfe694b)


## Conclusión

El proceso de web scraping implementado permite recopilar información detallada sobre los partidos de fútbol, desde los resultados hasta las estadísticas avanzadas. Los datos están organizados en una base de datos que facilita su análisis posterior. Este enfoque automatiza la recolección de información y garantiza que los datos sean precisos y consistentes, lo que es crucial para cualquier análisis deportivo.







# dataframes y analisis 

![image](https://github.com/user-attachments/assets/6fbccc04-f182-45d4-b9bf-f9228b165d32)


![image](https://github.com/user-attachments/assets/7b711ead-2f1c-425e-a642-d37093a34163)

![image](https://github.com/user-attachments/assets/09f51e3d-faa6-4f62-8664-cd8b59d8e7f5)

![image](https://github.com/user-attachments/assets/52335c3c-fd40-4991-b57f-36a82886029a)


![image](https://github.com/user-attachments/assets/f1749b14-04f7-4191-9c9d-6ca490386c57)
![image](https://github.com/user-attachments/assets/a8413677-246b-427f-af60-c47c6d1bad30)
![image](https://github.com/user-attachments/assets/264ae787-5d69-406e-9dd1-518d9e4c8b9d)












# Sistema de Calificación ELO

## Introducción

El sistema ELO es un método para calcular la habilidad relativa de los jugadores en juegos de dos participantes, como el ajedrez, deportes electrónicos, y otros juegos competitivos. Fue desarrollado por el profesor de física húngaro-americano Arpad Elo, y ha sido adoptado por muchas organizaciones y deportes alrededor del mundo.

## Cómo Funciona

### Puntuaciones Iniciales
Cada jugador comienza con una puntuación inicial, que puede variar dependiendo de la organización. En muchos sistemas de ajedrez, la puntuación inicial es de 1000 o 1200 puntos.

### Cálculo de Expectativa de Victoria
Antes de cada partida, se calcula la expectativa de victoria para cada jugador basada en la diferencia de sus puntuaciones ELO. La fórmula general es:

$$
E_A = \frac{1}{1 + 10^{\frac{R_B - R_A}{400}}}
$$

Donde:
- \(E_A\) es la expectativa de victoria del Jugador A.
- \(R_A\) y \(R_B\) son las puntuaciones ELO de los Jugadores A y B, respectivamente.

### Actualización de Puntuaciones
Después de la partida, las puntuaciones de los jugadores se actualizan en función del resultado real comparado con el resultado esperado. La fórmula es:

$$
R_A' = R_A + K \times (S_A - E_A)
$$

Donde:
- \(R_A'\) es la nueva puntuación de ELO del Jugador A.
- \(K\) es el factor de ajuste (un valor que determina la velocidad de cambio de las puntuaciones; valores típicos son 10, 20 o 40).
- \(S_A\) es el resultado de la partida para el Jugador A (1 para una victoria, 0.5 para un empate, 0 para una derrota).

### Ejemplo
Si el Jugador A con un ELO de 1600 juega contra el Jugador B con un ELO de 1400, la expectativa de victoria para el Jugador A sería:

$$
E_A = \frac{1}{1 + 10^{\frac{1400 - 1600}{400}}} \approx 0.76
$$

Si el Jugador A gana, su nueva puntuación sería:

$$
R_A' = 1600 + 20 \times (1 - 0.76) = 1600 + 4.8 = 1604.8
$$


![image](https://github.com/user-attachments/assets/889a314c-5dea-4a9f-966d-95191da4cb22)

![image](https://github.com/user-attachments/assets/015e6c48-d69b-4e17-9aa7-5854d3d18831)
![image](https://github.com/user-attachments/assets/ae96dd05-0cff-4d69-9e17-cdf5a6d180f7)





![image](https://github.com/user-attachments/assets/55a90515-b80d-4f83-805a-637ea08156e3)
