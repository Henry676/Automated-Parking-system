import requests
import time

firebase_url = 'https://estacionamiento-iot-22853-default-rtdb.firebaseio.com/ingresos.json'  
blynk_token = 'C6jfHdE2u2sZ6BKc8ttSPaMSZ2LOfKlZ'

led_pins = {
    'lugarA': 'V0',
    'estado_estacionamiento': 'V4',
}

def get_firebase_data():
    try:
        response = requests.get(firebase_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("Error al leer Firebase:", e)
        return None

def update_blynk(pin, value):
    url = f'https://blynk.cloud/external/api/update?token={blynk_token}&{pin}={value}'
    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Error actualizando {pin} en Blynk:", e)

def get_blynk_value(pin):
    url = f'https://blynk.cloud/external/api/get?token={blynk_token}&{pin}'
    try:
        r = requests.get(url)
        r.raise_for_status()
        return int(r.text.strip())  # 1 o 0
    except requests.RequestException as e:
        print(f"Error leyendo {pin} de Blynk:", e)
        return 0


def main_loop():
    while True:
        data = get_firebase_data()
        if data:
            ultima_fecha = list(data.keys())[-1]
            estado_lugarA = data[ultima_fecha].get("lugarA", False)
            # Leer estado del botón desde Blynk
            estado_estacionamiento = bool(get_blynk_value(led_pins["estado_estacionamiento"]))

            # Actualizar campo en Firebase
            url_fecha = f"https://estacionamiento-iot-22853-default-rtdb.firebaseio.com/ingresos/{ultima_fecha}.json"
            try:
                response = requests.patch(url_fecha, json={"estado_estacionamiento": estado_estacionamiento})
                print("Firebase actualizado con estado_estacionamiento:", estado_estacionamiento)
            except requests.RequestException as e:
                print("Error al actualizar Firebase:", e)

            # Actualizar Blynk: LED para lugarA
            update_blynk(led_pins["lugarA"], 1 if estado_lugarA else 0)


            print(f"Última fecha: {ultima_fecha}")
            print(f"Lugar A: {'Ocupado' if estado_lugarA else 'Libre'}")
            print(f"Estacionamiento {'ABIERTO' if estado_estacionamiento else 'CERRADO'}")
            print("---")
        else:
            print("No se pudo obtener datos de Firebase.")

        time.sleep(1)


if __name__ == "__main__":
    main_loop()