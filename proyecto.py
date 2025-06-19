from machine import Pin, PWM, time_pulse_us
from time import sleep
from practicas_iot_3P.display import draw_heart, draw_closed
from practicas_iot_3P.gas_sensor import check_gas
from practicas_iot_3P.alcohol_sensor import check_alcohol

import network
import urequests
import time
import json
import ntptime

# ---------- CONFIGURACIÓN ----------


POS_CERRADO = 0
POS_ABIERTO = 90
UMBRAL = 4.5  # cm ajustado

# ---------- Conexión WiFi ----------
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando a WiFi...")
    while not wlan.isconnected():
        sleep(1)
    print("Conectado:", wlan.ifconfig())
    try:
        ntptime.settime()
        print("Hora sincronizada con NTP")
    except:
        print("No se pudo sincronizar la hora NTP")

conectar_wifi()

# ---------- Pines ----------

# Entrada
trig_in = Pin(5, Pin.OUT)
echo_in = Pin(18, Pin.IN)
servo_in = PWM(Pin(21), freq=50)

# Salida
trig_out = Pin(4, Pin.OUT)
echo_out = Pin(19, Pin.IN)
servo_out = PWM(Pin(22), freq=50)

# Sensor infrarrojo
infrared_sensor1 = Pin(23, Pin.IN)

# LEDs de ocupación
led1 = Pin(2, Pin.OUT)
led2 = Pin(13, Pin.OUT)

# ---------- Variables ----------
entrada_abierta = False
salida_abierta = False
estado_anterior = 1
estado_estacionamiento = False

ocupados = 0
entradas = 0
salidas = 0
disponibles = 1
lugarA = False

# ---------- Funciones ----------

def verificar_estado_estacionamiento():
    fecha = obtener_fecha_local()
    url = f"{FIREBASE_URL}/{fecha}/estado_estacionamiento.json"
    try:
        response = urequests.get(url)
        estado = response.json()
        response.close()
        print("Estado del estacionamiento:", estado)
        return estado == True
    except:
        print("Error consultando estado del estacionamiento.")
        return False

def mover_servo(servo, angulo):
    duty = int((angulo / 180) * 102 + 26)
    servo.duty(duty)

def medir_distancia(trig, echo):
    trig.off()
    sleep(0.002)
    trig.on()
    sleep(0.00001)
    trig.off()
    try:
        duracion = time_pulse_us(echo, 1, 20000)
        if duracion < 0:
            return None
        return (duracion / 2) / 29.1
    except:
        return None

def distancia_estable(trig, echo, repeticiones=3, delay=0.05):
    lecturas = []
    for _ in range(repeticiones):
        d = medir_distancia(trig, echo)
        if d is not None:
            lecturas.append(d)
        sleep(delay)
    if len(lecturas) < repeticiones:
        return None
    return sum(lecturas) / len(lecturas)

def obtener_fecha_local():
    t = time.localtime()
    timezone_offset = -6 
    seconds = time.mktime(t) + timezone_offset * 3600
    local_time = time.localtime(seconds)
    return "{:04d}-{:02d}-{:02d}".format(local_time[0], local_time[1], local_time[2])

def actualizar_ocupados():
    fecha = obtener_fecha_local()
    url = f"{FIREBASE_URL}/{fecha}.json"
    payload = {
        "entradas": entradas,
        "salidas": salidas,
        "ocupados": ocupados,
        "ganancias": entradas * 1.5,
        "estado_estacionamiento": estado_estacionamiento,
        "lugarA": lugarA
    }
    try:
        response = urequests.patch(url, data=json.dumps(payload))
        print("Firebase actualizado:", response.text)
        response.close()
    except Exception as e:
        print("Error al actualizar Firebase:", e)

def check_infrared():
    global ocupados, lugarA, disponibles, estado_anterior
    estado_actual = infrared_sensor1.value()

    if estado_actual != estado_anterior:
        if estado_actual == 0 and not lugarA:
            lugarA = True
            ocupados += 1
            disponibles = 0
        elif estado_actual == 1 and lugarA:
            lugarA = False
            ocupados = max(0, ocupados - 1)
            disponibles = 1

        print("Sensor IR cambió. Ocupados:", ocupados)
        actualizar_ocupados()
        estado_anterior = estado_actual

# ---------- Inicializar servos ----------
mover_servo(servo_in, POS_CERRADO)
mover_servo(servo_out, POS_CERRADO)
sleep(0.5)

# ---------- Bucle principal ----------
while True:
    estado_estacionamiento = verificar_estado_estacionamiento()
    
    if estado_estacionamiento:
        check_infrared()
        check_gas()
        check_alcohol()
        draw_heart(disponibles, True)

        # Sensor de entrada
        if disponibles > 0:
            distancia_in = distancia_estable(trig_in, echo_in)
            if distancia_in is not None:
                print("Entrada (prom): {:.2f} cm".format(distancia_in))
                if distancia_in < UMBRAL and not entrada_abierta:
                    mover_servo(servo_in, POS_ABIERTO)
                    entrada_abierta = True
                elif distancia_in >= UMBRAL and entrada_abierta:
                    sleep(1.2)
                    mover_servo(servo_in, POS_CERRADO)
                    entrada_abierta = False
                    entradas += 1
                    actualizar_ocupados()

        # Sensor de salida
        distancia_out = distancia_estable(trig_out, echo_out)
        if distancia_out is not None:
            print("Salida (prom): {:.2f} cm".format(distancia_out))
            if distancia_out < UMBRAL and not salida_abierta:
                mover_servo(servo_out, POS_ABIERTO)
                salida_abierta = True
            elif distancia_out >= UMBRAL and salida_abierta:
                sleep(1.2)
                mover_servo(servo_out, POS_CERRADO)
                salida_abierta = False
                salidas += 1
                actualizar_ocupados()
    else:
        draw_heart(disponibles, False)

    sleep(0.5)

