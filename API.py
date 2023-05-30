import pandas as pd
import requests

#Entramos en la API de eamet
public_key = "Introduce tu clave"

url = "https://opendata.aemet.es/opendata/sh/76791451"

response = requests.get(url)
response_json=response.json()
response_json

idema=[]
ubi = []
lat=[]
lon=[]
alt=[]


for dato in response_json:
    if dato["idema"] not in idema:  
        idema.append(dato["idema"])
        ubi.append(dato["ubi"])
        lat.append(dato["lat"])
        lon.append(dato["lon"])
        alt.append(dato["alt"])
    else:
        break

#Creo el dataframe
estaciones=pd.DataFrame({"idema":idema,"ubi":ubi,"lat":lat,"lon":lon,"alt":alt})
estaciones.to_csv("estaciones.csv",index=False)

