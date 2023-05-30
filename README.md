![Cambios climáticos extremos](https://raw.githubusercontent.com/dmtor/Datos_climaticos_extremos/main/Titulo_clima.jpg)

Este proyecto de Análisis Exploratorio de Datos (EDA) se desarrolló como parte de mi formación en la escuela The Bridge. Se enfoca en el estudio de eventos climáticos extremos en España. Mediante el análisis de variables como temperatura, precipitación y viento, se busca identificar patrones, tendencias y la frecuencia de estos eventos. El objetivo es comprender mejor el comportamiento climático y sus implicaciones.

## Obtención de los datos

Mis datos los he obtenido en la web [https://datosclima.es/Aemet2013/DescargaDatos.html](https://datosclima.es/Aemet2013/DescargaDatos.html). Constaban de 3.277 archivos xls. Estos archivos son los que directamente proporciona Aemet en sus resúmenes diarios, los cuales son de acceso público. De un total de 820 estaciones del periodo 2014-2022.

Para gestionar estos datos, existe un gran problema, ya que no tienen ID de referencia y los nombres de las estaciones cambian a lo largo del periodo, lo que dificulta su identificación. Por ejemplo, utilicé la API de Aemet para obtener un listado con todas las estaciones disponibles, su ID, latitud, longitud y altitud. Incluso en este listado, los nombres también varían en comparación con los ofrecidos en la web de Aemet. Por ejemplo, "Tarragona Fac Geografía" es simplemente "Tarragona".

Para identificar los IDs con sus respectivas estaciones, tuve que buscar en Aemet y registrarlos manualmente en un archivo Excel, ya que muchas estaciones requerían una interpretación.

## Limpieza de datos

1. Para la carga de los datos, realicé un bucle for para iterar sobre la carpeta donde se encontraban todos los archivos xls. Descubrí que tenía 4 archivos corruptos que tuve que eliminar. Utilicé el nombre de los archivos para crear la columna de la fecha.
2. Cargué el Excel con los IDs y realicé una fusión (merge) con la columna correspondiente.
3. Renombré las columnas con nombres más sencillos para trabajar. En total, tenía más de 2 millones y medio de filas.
4. Transformé los datos y eliminé las horas de algunos de ellos, ya que no eran necesarias para mi análisis. Además, establecí la columna de fecha como tipo datetime.
5. Hubo dos estaciones que tenían el mismo nombre pero en distintas provincias. Utilicé un bucle for para asignarles sus IDs. Al duplicarse los resultados, eliminé las filas duplicadas (drop_duplicates).
6. Creé otro dataframe con ID y estación para eliminar las que tenían dos nombres, utilizando nuevamente drop_duplicates. Luego, ordené las columnas.
7. Eliminé las estaciones que no tenían ID y creé tres columnas para día, mes y año, ya que tuve problemas trabajando con la columna Fecha.
8. Eliminé las estaciones que no tenían un año completo de registros.
9. Decidí eliminar los años en los que un mes tenía más de 20 valores NaN. Realicé un conteo de NaN por día y los guardé en un dataframe utilizando groupby. Para las precipitaciones, como es un valor acumulativo, decidí filtrar por 5 valores NaN por día.
10. Guardé los dataframes en varios archivos csv, separándolos por temperatura, precipitación y viento, con la intención de incorporarlos en Streamlit, pero finalmente no tuve tiempo para hacerlo.
11. Creé nuevas columnas con la precipitación acumulada en 6 horas, temperatura máxima, mínima y media anual. Para el viento, agregué una columna de racha y velocidad máxima.
12. Creé un dataframe con las nuevas columnas y lo guardé en un archivo csv para trabajar con él.

## Representación de los datos

[Ver la historia de Tableau Public](https://public.tableau.com/views/EDA_16787293062250/Datosclimticos?:language=es-ES&:display_count=n&:origin=viz_share_link)

