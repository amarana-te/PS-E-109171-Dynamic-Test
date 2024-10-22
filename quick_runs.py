import os
import random
import json  # Utilizamos json para formatear correctamente los datos

# Definimos los grupos de URLs
agg_group5 = [
    "https://10.100.10.1/RxConnectRxP/", "https://10.100.10.2/RxConnectRxP/",
    "https://10.100.10.3/RxConnectRxP/", "https://10.100.10.4/RxConnectRxP/",
    "https://10.100.10.5/RxConnectRxP/"
]
agg_group2 = [
    "https://10.100.20.1/RxConnectRxP/", "https://10.100.20.2/RxConnectRxP/",
    "https://10.100.20.3/RxConnectRxP/", "https://10.100.20.4/RxConnectRxP/",
    "https://10.100.20.5/RxConnectRxP/"
]
agg_group3 = [
    "https://10.100.30.1/RxConnectRxP/", "https://10.100.30.2/RxConnectRxP/",
    "https://10.100.30.3/RxConnectRxP/", "https://10.100.30.4/RxConnectRxP/",
    "https://10.100.30.5/RxConnectRxP/"
]
agg_group4 = [
    "https://10.100.40.1/RxConnectRxP/", "https://10.100.40.2/RxConnectRxP/",
    "https://10.100.40.3/RxConnectRxP/", "https://10.100.40.4/RxConnectRxP/",
    "https://10.100.40.5/RxConnectRxP/"
]
agg_group1 = [
    "https://10.100.50.1/RxConnectRxP/", "https://10.100.50.2/RxConnectRxP/",
    "https://10.100.50.3/RxConnectRxP/", "https://10.100.50.4/RxConnectRxP/",
    "https://10.100.50.5/RxConnectRxP/"
]

# Mapear los rangos a sus grupos correspondientes
group_map = {
    1000: agg_group1,
    2000: agg_group2,
    3000: agg_group3,
    4000: agg_group4,
    5000: agg_group5
}

# Directorio donde se guardarán los archivos
path = os.path.join(os.getcwd(), "cvs_folder")
os.makedirs(path, exist_ok=True)  # Crear la carpeta si no existe

# Función para seleccionar URLs aleatorias de 1 a 5 elementos
def get_random_urls(group):
    return random.sample(group, random.randint(1, 5))

# Generar agentes para cada rango
for start, group in group_map.items():
    # Definimos el rango superior según la lista
    if start == 1000:
        end = 1143
    elif start == 2000:
        end = 2136
    elif start == 3000:
        end = 3123
    elif start == 4000:
        end = 4109
    elif start == 5000:
        end = 5112

    # Generar archivos JSON para cada agente dentro del rango
    for i in range(start, end + 1):
        agent_name = f"thousandeyes_{i}.localdomain"
        urls = get_random_urls(group)  # URLs aleatorias de 1 a 5 elementos

        # Crear el diccionario de datos
        data = {
            "name": agent_name,
            "urls": urls
        }

        # Guardar el archivo JSON con indentación para una mejor lectura
        file_path = os.path.join(path, f"{agent_name}.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Archivo {agent_name}.json creado con éxito.")
