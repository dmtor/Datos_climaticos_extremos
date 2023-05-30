import pandas as pd
import glob

# Lista vacia para los df
dfs = []
columnas = ['Estación', 'Provincia', 'Temperatura máxima (ºC)', 'Temperatura mínima (ºC)', 'Temperatura media (ºC)', 'Racha (km/h)', 'Velocidad máxima (km/h)', 'Precipitación 00-24h (mm)', 'Precipitación 00-06h (mm)', 'Precipitación 06-12h (mm)', 'Precipitación 12-18h (mm)', 'Precipitación 18-24h (mm)']


# Dirección de los archivos xls para llamarlos con glob.
ruta = "data/AEMET_XLS/*.xls"
archivos_xls = glob.glob(ruta)

# Bucle seleccionando los datos que necesitamos y añadiendo la columna fecha.
for filename in archivos_xls:
    df = pd.read_excel(filename, header=4, skiprows=2, names=columnas)
    df['fecha'] = filename[-14:-4]
    #printeo el filename, porque he descubierto algunos archivos corruptos, para poder identificarlos y borrarlos.
    print(filename)
    dfs.append(df)

df_final = pd.concat(dfs, axis=0, ignore_index=True)
#Este es el Excel para vincular los ids a la estaciones.
df_idema = pd.read_excel("data/Ides_estaciones.xlsx") 

df_idema_final=pd.merge(df_final,df_idema,on="Estación")
#Guardo el dataframe en un cs.
df_idema_final.to_csv('df_unido.csv', index=False)

df_idema_final=pd.read_csv('data/df_unido.csv')

df_limpieza=df_idema_final
#Cambio el nombre de las columnas
df_limpieza = df_limpieza.rename(columns={"Temperatura máxima (ºC)":"TMax",
                                          "Temperatura mínima (ºC)":"TMin",
                                          "Temperatura media (ºC)":"TMed",
                                          "Racha (km/h)":"Racha",
                                          "Velocidad máxima (km/h)":"VelMax",
                                          "Precipitación 00-24h (mm)":"PreTotal",
                                          "Precipitación 00-06h (mm)":"Pre_6h",
                                          "Precipitación 06-12h (mm)":"Pre_12h",
                                          "Precipitación 12-18h (mm)":"Pre_18h",
                                          "Precipitación 18-24h (mm)":"Pre_24h",
                                          "fecha":"Fecha"})

#Elimino la hora que no la queremos para nada y transformamos la serie específica en float, para poder operar.
df_limpieza["TMax"]=df_limpieza['TMax'].str.split(' ').str[0].astype(float)
df_limpieza["TMin"]=df_limpieza['TMin'].str.split(' ').str[0].astype(float)
df_limpieza["Racha"]=df_limpieza['Racha'].str.split(' ').str[0].astype(float)
df_limpieza["VelMax"]=df_limpieza['VelMax'].str.split(' ').str[0].astype(float)

#transformamos el resto de series en float y fecha.
df_limpieza["TMed"]=df_limpieza["TMed"].astype(float)
df_limpieza["PreTotal"]=df_limpieza["PreTotal"].astype(float)
df_limpieza["Pre_6h"]=df_limpieza["Pre_6h"].astype(float)
df_limpieza["Pre_12h"]=df_limpieza["Pre_12h"].astype(float)
df_limpieza["Pre_18h"]=df_limpieza["Pre_18h"].astype(float)
df_limpieza["Pre_24h"]=df_limpieza["Pre_24h"].astype(float)
df_limpieza["Fecha"] = pd.to_datetime(df_limpieza["Fecha"], format="%Y-%m-%d")


#hay estaciones con dos nombres distintos, selecciono Idema y estación en un nuevo dataframe, elimino los duplicados de Idema para quedarme con un valor de estación

df_adecuar_estaciones = df_limpieza.loc[:, ['Idema', 'Estación']]
df_adecuar_estaciones=df_adecuar_estaciones.drop_duplicates(subset=['Idema'],keep='first')
df_limpieza=df_limpieza.drop("Estación", axis=1)
df_limpieza = pd.merge(df_limpieza, df_adecuar_estaciones[['Idema', 'Estación']], on='Idema', how='left')

#Ordeno
df_limpieza=df_limpieza[["Idema","Fecha","Estación","Provincia","TMax","TMin","TMed","Racha","VelMax","PreTotal","Pre_6h","Pre_12h","Pre_18h","Pre_24h"]]
df_limpieza

#ahora elimino todas las filas sin Idema, son estaciones que no se han conseguido identificar por lo tanto las debo eliminar.
df_limpieza = df_limpieza.dropna(subset=['Idema'])

#vuelvo a comprobar que se han borrado.
num_nans = df_limpieza["Idema"].isna().sum()


#he decidido crear un nuevo csv limpio, para facilitar el resto de operaciones.
df_limpieza.to_csv('df_limpio.csv', index=False)

df_filtro=df_limpieza

#He tenido muchos problemas para trabajar con Fecha, por lo tanto he decidido dividirla en 3 nuevas columnas.

df_filtro['Año'] = df_filtro['Fecha'].dt.year
df_filtro['Mes'] = df_filtro['Fecha'].dt.month
df_filtro['Día'] = df_filtro['Fecha'].dt.day



# Observo que tengo años que no están completos y no son Nan, por lo tanto hago filtros para eliminar esos años.
incompletos = df_filtro.groupby(['Idema', 'Año'])

# Verifico que en Mes tienen 12 valores únicos y aplico la mascara
mascara_filtro = incompletos['Mes'].nunique() == 12
años_completos = mascara_filtro[mascara_filtro].index

# Filtrar el dataframe original para mantener sólo los grupos válidos
df_filtro = df_filtro.set_index(['Idema', 'Año']).loc[años_completos].reset_index()




#Temperatura
#Ahora voy a establecer un criterio en el que voy a eliminar los años en los que en un mes tengan más de 20 Nans.
#empiezo con un conteo de Nans por dia y los guardo en un dataframe
contar_nans = df_filtro.groupby(['Idema','Estación', 'Año', 'Mes'])['TMax'].apply(lambda x: x.isna().sum()).reset_index(name='NaNs')

#Filtro los nans superiores a 20.
filtro_nans = contar_nans[contar_nans['NaNs'] > 20]

#Elimino los duplicados, para quedarme con Año e Idema
idema_año_filter = filtro_nans[['Idema', 'Año']].drop_duplicates()

#Hago un merge con las columnas Idema y Año.
df_unido_nan = df_filtro.merge(idema_año_filter[['Idema', 'Año']], on=['Idema', 'Año'], how='left', indicator=True)
df_temperatura = df_unido_nan[df_unido_nan['_merge'] == 'left_only'].drop(columns=['_merge'])

#He pensado en dividir los csvs en 3 partes temperatura, viento y precipitacion, debido a que hay estaciones que por ejemplo no contabilizan-
#todos los valores, por ese motivo voy a eliminar las columnas que no vaya a necesitar.
df_temperatura.drop(['Racha', 'VelMax','PreTotal','Pre_6h','Pre_12h','Pre_18h','Pre_24h'], axis=1, inplace=True)

#Las ordeno.
df_temperatura=df_temperatura[['Idema','Estación','Provincia','Fecha','Año','Mes','Día','TMax','TMin','TMed']]
df_temperatura.to_csv('df_temperatura.csv', index=False)




#Precipitación
#Aqui me he dado cuenta de un gran error, estamos hablando de acumulados por lo tanto he tenido que bajar el umbral para que sea más correcto.

contar_nans = df_filtro.groupby(['Idema','Estación', 'Año', 'Mes'])['PreTotal'].apply(lambda x: x.isna().sum()).reset_index(name='NaNs')
filtro_nans = contar_nans[contar_nans['NaNs'] > 5]
idema_año_filter = filtro_nans[['Idema', 'Año']].drop_duplicates()
df_unido_nan = df_filtro.merge(idema_año_filter[['Idema', 'Año']], on=['Idema', 'Año'], how='left', indicator=True)
df_Precipitacion = df_unido_nan[df_unido_nan['_merge'] == 'left_only'].drop(columns=['_merge'])
df_Precipitacion.drop(['Racha', 'VelMax','TMax','TMin','TMed',], axis=1, inplace=True)
df_Precipitacion=df_Precipitacion[['Idema','Estación','Provincia','Fecha','Año','Mes','Día','PreTotal','Pre_6h','Pre_12h','Pre_18h','Pre_24h']]
#cuento los meses unicos
contar_meses=df_Precipitacion.groupby(['Idema', 'Año'])['Mes'].nunique()
#filtramos los años imcompletos.
años_incompletos = contar_meses[contar_meses < 12].index
#eliminamos los años
df_Precipitacion = df_Precipitacion[~df_Precipitacion.set_index(['Idema', 'Año']).index.isin(años_incompletos)]
df_Precipitacion.to_csv('df_Precipitacion.csv', index=False)

#Viento

contar_nans = df_filtro.groupby(['Idema','Estación', 'Año', 'Mes'])['Racha'].apply(lambda x: x.isna().sum()).reset_index(name='NaNs')
filtro_nans = contar_nans[contar_nans['NaNs'] > 20]
idema_año_filter = filtro_nans[['Idema', 'Año']].drop_duplicates()
df_unido_nan = df_filtro.merge(idema_año_filter[['Idema', 'Año']], on=['Idema', 'Año'], how='left', indicator=True)
df_viento = df_unido_nan[df_unido_nan['_merge'] == 'left_only'].drop(columns=['_merge'])
df_viento.drop(['PreTotal','Pre_6h','Pre_12h','Pre_18h','Pre_24h','TMax','TMin','TMed',], axis=1, inplace=True)
df_viento=df_viento[['Idema','Estación','Provincia','Fecha','Año','Mes','Día','Racha', 'VelMax']]
df_viento.to_csv('df_viento.csv', index=False)


df_filtered = df_Precipitacion[(df_Precipitacion['Estación'] == 'Alforja') & (df_Precipitacion['Año'] == 2014)]

#Creo una columna con el máximo acumulado en 6h.
preci_max6 = df_Precipitacion.groupby(['Idema', 'Estación', 'Provincia', 'Año'])[['Pre_6h', 'Pre_12h', 'Pre_18h', 'Pre_24h']].max()
preci_max6['maximo_valor'] = preci_max6[['Pre_6h', 'Pre_12h', 'Pre_18h', 'Pre_24h']].max(axis=1)
preci_max6 = preci_max6.drop(columns=['Pre_6h', 'Pre_12h', 'Pre_18h', 'Pre_24h'])


#Creo un dataframe
temp_max = df_temperatura.groupby(['Idema','Estación','Provincia','Año'])['TMax'].max()
temp_min = df_temperatura.groupby(['Idema','Estación','Provincia','Año'])['TMin'].min()
temp_media = df_temperatura.groupby(['Idema','Estación','Provincia','Año'])['TMed'].mean()

racha = df_viento.groupby(['Idema','Estación','Provincia','Año'])['Racha'].max()
racha_df = racha.to_frame(name="Racha_Max")
vel_viento = df_viento.groupby(['Idema','Estación','Provincia','Año'])['VelMax'].max()

Preci_total_max = df_Precipitacion.groupby(['Idema','Estación','Provincia','Año'])['PreTotal'].max().rename("Pre_Total_Max")
Preci_total_sum = df_Precipitacion.groupby(['Idema','Estación','Provincia','Año'])['PreTotal'].sum().rename("Pre_Total_Sum")

df_graficas=pd.concat([temp_max,temp_min,temp_media,racha,vel_viento,Preci_total_max,Preci_total_sum,preci_max6], axis=1)
print(df_graficas)
df_graficas.reset_index(inplace=True)
df_estaciones = pd.read_csv('data/estaciones.csv')
df_estaciones = df_estaciones.rename(columns={"idema":"Idema"})
df_graficas_final = pd.merge(df_graficas, df_estaciones, on='Idema')

print(df_graficas_final)
df_graficas_final.to_csv('df_graficas.csv', index=False)
df_graficas_final.to_excel('df_graficas.xlsx', index=False)

