import re

# Definimos el patrón para extraer los tiempos en segundos
time_pattern = re.compile(r"time: (\d+\.\d+) seconds")

def analyze_log_times(log_file):
    total_seconds = 0.0  # Inicializamos el total de segundos
    count_above_5 = 0    # Contador para tiempos mayores a 5 segundos

    # Abrimos y leemos el archivo línea por línea
    with open(log_file, "r") as f:
        for line in f:
            # Buscamos los tiempos en cada línea usando la expresión regular
            match = time_pattern.search(line)
            if match:
                time_value = float(match.group(1))  # Extraemos el tiempo como float
                total_seconds += time_value  # Sumamos el tiempo al total

                # Verificamos si el tiempo es mayor a 5 segundos
                if time_value > 5.0:
                    count_above_5 += 1

    return total_seconds, count_above_5

# Ruta del archivo log
log_file = "api_calls.log"

# Analizamos el log y obtenemos los resultados
total_time, above_5_count = analyze_log_times(log_file)

# Mostramos los resultados
print(f"Tiempo total: {total_time:.4f} segundos")
print(f"Número de tiempos mayores a 5 segundos: {above_5_count}")
