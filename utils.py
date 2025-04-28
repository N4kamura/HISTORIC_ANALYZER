import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd

########################
# INDIVIDUAL FUNCTIONS #
########################
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

def list_names(json_data: str) -> list:
    names_list = []
    for i in range(len(json_data['routes'])):
        names_list.append(json_data['routes'][i]['name'])

    return names_list

def recognize_avenue(json_data, name: str) -> dict:
    for i in range(len(json_data['routes'])):
        name_avenue = json_data['routes'][i]['name']
        if name.lower() in name_avenue.lower():
            return json_data['routes'][i]
        
def extract_information(selected_avenue) -> dict:
    dict = {
        "Nombre": selected_avenue['name'],
        "Tiempo de viaje": selected_avenue['time'],
        "Tiempo de viaje promedio": selected_avenue['historicTime'],
        "Longitud": selected_avenue['length'],
    }

    if selected_avenue['leadAlert'] is not None:
        alert = {
            "Tipo": selected_avenue['leadAlert']['type'],
            "Subtipo": selected_avenue['leadAlert']['subType'],
            "Calle": selected_avenue['leadAlert']['street'],
            "Ciudad": selected_avenue['leadAlert']['city'],
            "Latitud Longitud": selected_avenue['leadAlert']['position'],
            "Comentarios cantidad": selected_avenue['leadAlert']['numComments'],
            "Me gusta cantidad": selected_avenue['leadAlert']['numThumbsUp'],
            "No hubo cantidad": selected_avenue['leadAlert']['numNotThereReports']
        }

    dict['Alerta'] = alert

    return dict

#####################
# GROUP INFORMATION #
#####################

def extract_delays(folder_path: str, name: str) -> dict:
    json_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]

    results = {} #TODO: Hay casos en que no hay datos ¡CUIDADO!

    for json_file in json_list:
        json_name = os.path.basename(json_file)
        if "(" in json_name:
            # print(json_name) # TODO: Colocarlo en un logger.
            continue
        with open(json_file) as f:
            data = json.load(f)
            for i in range(len(data['routes'])):
                if data['routes'][i]['name'] == name:
                    dict_result = {
                        "travel_time": int(data['routes'][i]['time']),
                        "mean_travel_time": int(data['routes'][i]['historicTime']),
                        "length": int(data['routes'][i]['length']),
                        "speed": round(float(
                            int(data['routes'][i]['length']) / int(data['routes'][i]['time'])
                        ),2)*3.6,
                        "mean_speed": round(float(
                            int(data['routes'][i]['length']) / int(data['routes'][i]['historicTime'])
                        ),2)*3.6
                    }
                    results[json_name[:-5]] = dict_result

    return results

def draw_graph(results: dict, variable: str, day: str, selected_corridor: str, step_minutes: int = 30, smoothing_window: int = 5) -> None:
    if variable == "travel_time":
        title = "tiempo de viaje"
        units = "s"
    elif variable == "speed":
        title = "velocidad"
        units = "km/h"

    X = list(results.keys())
    X = [datetime.strptime(elem, "%H%M%S") for elem in X]

    Y1 = []
    Y2 = []
    for dict_result in results.values():
        Y1.append(dict_result[variable])
        Y2.append(dict_result[f"mean_{variable}"])

    Y1_smooth = pd.Series(Y1).rolling(window=smoothing_window, center=True).mean()
    # Y2_smooth = pd.Series(Y2).rolling(window=smoothing_window, center=True).mean()

    fig, ax = plt.subplots()

    ax.plot(X, Y1_smooth, label=f"{title.upper()} REAL")
    ax.plot(X, Y2, label=f"{title.upper()} PROMEDIO")
    ax.set_xlabel('HORA')
    ax.set_ylabel(f"{title.upper()} ({units.upper()})")
    ax.set_title(f"GRÁFICA DE {title.upper()}\n{day.upper()}\n{selected_corridor.upper()}")
    ax.legend()
    ax.grid(True)

    # Formatear bien el eje X con horas
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=step_minutes))


    # Opcionalmente limitar un rango de horas
    ax.set_xlim([datetime.strptime("06:35:00", "%H:%M:%S"), datetime.strptime("21:00:00", "%H:%M:%S")])

    fig.autofmt_xdate()  # Para rotar las fechas automáticamente
    plt.tight_layout()
    plt.show()

###########################
# MULTI-GROUP INFORMATION #
###########################

def list_days(folder_path: str):
    days_list = [f"{file[:2]}/{file[2:4]}/{file[4:]}" for file in os.listdir(folder_path)]
    print(days_list)

def show_names(folder_path: str, day: str):
    formated_date = day.replace('/','')
    day_folder = os.path.join(folder_path, formated_date)

    last_json_path = [os.path.join(day_folder, file) for file in os.listdir(day_folder)][-1]
    list_names(last_json_path)