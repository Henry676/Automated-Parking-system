from machine import Pin, ADC, PWM
from time import sleep
from practicas_iot_3P.buzzer import sound_buzzer


# Configurar ADC en GPIO32 (ADC1_CH4)
adc = ADC(Pin(32))
adc.atten(ADC.ATTN_11DB)  # Permite rango de voltaje de 0 a ~3.6V
adc.width(ADC.WIDTH_12BIT) # Resolución de 12 bits (0-4095)

 

def check_alcohol():
    alc_val = adc.read()
    if alc_val > 4000:
        print("Hay un borracho, lectura: ",alc_val)
        buzzer = PWM(Pin(17, Pin.OUT))
        sound_buzzer(buzzer)
        return
    return


