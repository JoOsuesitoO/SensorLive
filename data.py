import machine
import time
import network
import urequests  # Librería para peticiones HTTP
import gc         # Garbage Collector para limpiar memoria

# 1. Tus credenciales de WiFi
WIFI_SSID = "estudiantes"
WIFI_PASS = "987654312.#"

# 2. Tus credenciales de Adafruit IO
AIO_USER = "JoOshua05"
AIO_KEY = "aio_OtqT54tyMq7whhWjyxGikL60rXWk"

# 3. Configuración de UART y Cifrado
llave = 1
uart = machine.UART(0, baudrate=9600)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        # Esperar hasta conectar
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            wlan.connect(WIFI_SSID, WIFI_PASS)
            timeout -= 1
            print(f"Esperando... {timeout}")
            
    if wlan.isconnected():
        print('¡WiFi conectado!', wlan.ifconfig())
        return True
    else:
        print('Fallo en la conexión WiFi')
        return False

def enviar_a_adafruit(feed_name, valor):
    """
    Envía un dato a un feed específico de Adafruit IO vía HTTP REST
    """
    try:
        # Construimos la URL de la API
        url = f"https://io.adafruit.com/api/v2/{AIO_USER}/feeds/{feed_name}/data"
        
        # Cabeceras necesarias
        headers = {'X-AIO-Key': AIO_KEY, 'Content-Type': 'application/json'}
        
        # El dato debe ir en formato JSON
        data = {'value': valor}
        
        # Hacemos el envío (POST)
        respuesta = urequests.post(url, json=data, headers=headers)
        respuesta.close() # Importante cerrar para liberar memoria
        print(f"-> Enviado a {feed_name}: {valor}")
        
    except Exception as e:
        print(f"Error enviando a Adafruit ({feed_name}): {e}")

def convertir_seguro(dato_recibido):
    if dato_recibido is None: return None
    texto_limpio = dato_recibido.strip()
    if len(texto_limpio) > 0 and texto_limpio.isdigit():
        try:
            return int(texto_limpio)
        except:
            return None
    return None



conectar_wifi()

print("Sistema iniciado. Esperando datos del Arduino...")

while True:
    try:
        if uart.any():
            # 1. Leer datos cifrados
            raw_luz = uart.readline()
            raw_temp = uart.readline()
            raw_ant = uart.readline()
            raw_agua = uart.readline()

            # 2. Limpiar y validar
            Luz_Cifrada = convertir_seguro(raw_luz)
            Temp_Cifrada = convertir_seguro(raw_temp)
            Ant_Cifrada = convertir_seguro(raw_ant)
            Agua_Cifrada = convertir_seguro(raw_agua)

            # Verificar integridad
            if (Luz_Cifrada is None or Temp_Cifrada is None or 
                Ant_Cifrada is None or Agua_Cifrada is None):
                continue 

            # 3. Desencriptar (XOR)
            ValorLuz = Luz_Cifrada ^ llave
            ValorTemp = Temp_Cifrada ^ llave
            ValorAnt = Ant_Cifrada ^ llave
            ValorAgua = Agua_Cifrada ^ llave
            
            # Cálculo de temperatura real
            TempReal = ValorTemp * 0.488

            # Imprimir en consola local (para depurar)
            print("-" * 30)
            print(f"Luz: {ValorLuz} | Temp: {TempReal:.2f} | Ant: {ValorAnt} | Agua: {ValorAgua}")

            # 4. ENVIAR A LA NUBE (Adafruit IO)
            # Nota: Los nombres de los feeds aquí deben coincidir con los que creaste
            enviar_a_adafruit("luz", ValorLuz)
            enviar_a_adafruit("temperatura", TempReal)
            enviar_a_adafruit("antena", ValorAnt)
            enviar_a_adafruit("agua", ValorAgua)
            
            # Limpieza de memoria (importante en loops con red)
            gc.collect()


            print("Esperando 10 segundos para siguiente envío...")
            time.sleep(10)

    except Exception as e:
        print(f"Error en el bucle principal: {e}")
        while uart.any(): uart.read()
        time.sleep(2)
