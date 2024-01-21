# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 11:01:48 2024

@author: migue
"""
import geopandas as gpd
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


paths=[r"G:\My Drive\04. Passion Projects\poblacion_1_enero.csv",
       r"G:\My Drive\04. Passion Projects\Barrios\Barrios.shp",
       r"G:\My Drive\04. Passion Projects\Distritos\Distritos_20210712.shp",
       r"G:\My Drive\04. Passion Projects\Ranking barrios - Hoja 1.csv"]


barrios_shp,distritos_shp = gpd.read_file(paths[1]),gpd.read_file(paths[2])
rankings,poblacion=pd.read_csv(paths[3],delimiter=","),pd.read_csv(paths[0],delimiter=";")
# Print the first few rows of the GeoDataFrame
poblacion=poblacion.loc[(poblacion['fecha']=="1 de enero de 2023") & (poblacion['barrio']!=poblacion['distrito'])]


# URL of the Wikipedia page
url = "https://es.wikipedia.org/wiki/Anexo:Barrios_administrativos_de_Madrid"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table on the page
    table = soup.find('table', {'class': 'wikitable'})

    # Extract data from the table and create a list of dictionaries
    data = []
    headers = []
    for row_idx, row in enumerate(table.find_all('tr')):
        cells = row.find_all(['th', 'td'])
        if row_idx == 0:
            # Header row
            headers = [re.sub(r'\W+', '', cell.text.strip()) for cell in cells]
        else:
            # Data rows
            row_data = [re.sub(r'\W+', ' ', cell.text.replace('\xa0', ' ').strip()) for cell in cells]
            if len(row_data)==5:
                row_data.pop(0)
            data.append(dict(zip(headers, row_data)))

    # Convert the list of dictionaries to a DataFrame
    areas = pd.DataFrame(data)

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

def remove_non_numeric(value):
    return float(''.join(c for c in value if c.isdigit()).strip('²'))/1000

# Apply the function to the 'Nombre' column
areas['Nombre'] = areas['Nombre'].apply(remove_non_numeric)


# Define the function to add space before capitalized letters
def add_spaces_to_series(series):
    result_series = []
    for s in series:
        result_series.append(add_space(s))
    return result_series

def add_space(s):
    result = []
    i = 0
    while i < len(s):
        # Check for "de" or "del" before a capitalized letter
        if i + 2 < len(s) and s[i:i + 2].lower() == 'de' and i + 3 < len(s) and s[i + 2].isupper():
            result.append(' ')
        elif i + 3 < len(s) and s[i:i + 3].lower() == 'del' and i + 4 < len(s) and s[i + 3].isupper():
            result.append(' ')
        
        # Add space before capitalized letters
        if i > 0 and s[i].isupper() and not s[i - 1].isspace():
            result.append(' ')
        
        result.append(s[i])
        i += 1
    
    return ''.join(result)
poblacion['barrio']= add_spaces_to_series(poblacion['barrio'])
barrios_shp.columns.values
rankings.columns.values
distritos_shp.columns.values
poblacion.columns.values
areas.columns.values


def procesar_serie(serie):
    def reemplazar_vocales_con_acento(texto):
        # Definir un diccionario con las vocales con acento y sus correspondientes sin acento
        reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}
        
        # Aplicar los reemplazos en el texto
        for vocal_acentuada, vocal_sin_acento in reemplazos.items():
            texto = texto.lower().replace(vocal_acentuada, vocal_sin_acento)
        
        return texto

    # Aplicar la función de reemplazo y convertir a mayúsculas
    serie_procesada = serie.apply(lambda x: reemplazar_vocales_con_acento(x).upper())
    
    return serie_procesada

barrios_shp["NOMDIS"]= procesar_serie(barrios_shp["NOMDIS"])
rankings['Barrio']=procesar_serie(rankings['Barrio'])
poblacion['barrio']=procesar_serie(poblacion['barrio'])
areas['Código']=procesar_serie(areas['Código'])

#renaming columns
rankings=rankings.rename(columns={'Barrio':'barrio'})
barrios_shp=barrios_shp.rename(columns={'BARRIO_MAY':'barrio','NOMDIS':'distrito'})
areas=areas.rename(columns={'Código':'barrio'})
distritos_shp=distritos_shp.rename(columns={'DISTRI_MAY':'distrito'})