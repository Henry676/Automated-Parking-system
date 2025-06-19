from machine import Pin, ADC, PWM
from time import sleep
from practicas_iot_3P.buzzer import sound_buzzer

mq6_adc = ADC(Pin(34))
mq6_adc.atten(ADC.ATTN_11DB)


def check_gas():
    gas_val = mq6_adc.read()
    if gas_val > 1000:
        buzzer = PWM(Pin(17, Pin.OUT))
        print("Alerta de gas, valor: ", gas_val)
        sound_buzzer(buzzer)
        return
    return

