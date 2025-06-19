from machine import Pin, SPI
import max7219

spi = SPI(1, baudrate=10000000, sck=Pin(25), mosi=Pin(14))
cs = Pin(15, Pin.OUT)
display = max7219.Matrix8x8(spi, cs, 1)


def draw_0():
    puntos = [
        (2,1), (3,1), (4,1), 
        (2,2),        (4,2),
        (2,3),        (4,3),
        (2,4),        (4,4),
        (2,5),        (4,5),
        (2,6), (3,6), (4,6)
    ]
    for x, y in puntos:
        display.pixel(x, y, 1)


def draw_1():
    puntos = [
        (3,1), (3,2), (3,3), (3,4), (3,5), (3,6)
    ]
    for x, y in puntos:
        display.pixel(x, y, 1)
        
def draw_closed():
    puntos = [
        (1,1), (2,2), (3,3), (4,4), (5,5), (6,6),
        (6,1), (5,2), (4,3), (3,4), (2,5), (1,6)
    ]
    for x, y in puntos:
        display.pixel(x, y, 1)

def draw_heart(cupo, estado):
    display.fill(0)
    if not estado:
        draw_closed()
        display.show()
    elif cupo == 0:
        draw_0()
    elif cupo == 1:
        draw_1()
    display.show()


