"""!
@file free_bike_laned_cars_fixed.py
@brief Fixed type conversion for stability
"""

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from upy_adafruit_mpu6050 import MPU6050
import utime
import random

# ================================
# Hardware Setup
# ================================
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
mpu = MPU6050(i2c)

# ================================
# Game Settings (Explicit Integers)
# ================================
ROAD_LEFT = 24
ROAD_RIGHT = 104
BIKE_WIDTH = 8
CAR_WIDTH = 12
LANE_POSITIONS = [34, 64, 94]  # 3 lanes for cars
MIN_CAR_GAP = 40
GAME_SPEED = 0.8

# ================================
# Game State
# ================================
bike_x = 64  # Starting position
cars = []
score = 0
filtered_tilt = 0.0
alpha = 0.2

def draw_road():
    oled.fill_rect(0, 0, 128, 64, 0)
    oled.rect(ROAD_LEFT, 0, ROAD_RIGHT-ROAD_LEFT, 64, 1)
    for y in range(0, 64, 8):
        for x in [44, 84]:
            oled.pixel(x, y, 1)

def draw_bike():
    x = int(bike_x - BIKE_WIDTH//2)
    oled.fill_rect(x, 54, BIKE_WIDTH, 8, 1)
    oled.fill_rect(x+2, 62, 4, 2, 1)

def create_car():
    if cars and (64 - cars[-1]['y']) < MIN_CAR_GAP:
        return
    
    cars.append({
        'lane': random.choice([0, 1, 2]),
        'y': -8,
        'x': LANE_POSITIONS[random.randint(0, 2)] - CAR_WIDTH//2
    })

def move_cars():
    global score
    bike_left = int(bike_x - BIKE_WIDTH//2)
    bike_right = bike_left + BIKE_WIDTH
    
    for car in cars:
        car['y'] += GAME_SPEED
        oled.fill_rect(car['x'], int(car['y']), CAR_WIDTH, 8, 1)
        
        # Convert all positions to integers for collision
        car_left = car['x']
        car_right = car_left + CAR_WIDTH
        car_bottom = int(car['y']) + 8
        
        if (car_bottom > 54) and \
           (car_left < bike_right) and \
           (car_right > bike_left):
            game_over()

    cars[:] = [c for c in cars if c['y'] < 64]
    score += 1

def game_over():
    oled.fill(0)
    oled.text("CRASH!", 40, 20, 1)
    oled.text(f"Score: {score}", 32, 40, 1)
    oled.show()
    utime.sleep(3)
    reset_game()

def reset_game():
    global bike_x, cars, score
    bike_x = 64
    cars = []
    score = 0

def main():
    global bike_x, filtered_tilt
    
    while True:
        # Force tilt value to float
        accel_x = float(-mpu.acceleration[1])
        filtered_tilt = alpha * accel_x + (1 - alpha) * filtered_tilt
        
        # Explicit integer conversion for road boundaries
        bike_x += filtered_tilt * 0.8
        bike_x = int(max(ROAD_LEFT + BIKE_WIDTH//2, 
                       min(ROAD_RIGHT - BIKE_WIDTH//2, bike_x)))
        
        draw_road()
        draw_bike()
        
        if random.random() < 0.03:
            create_car()
            
        move_cars()
        
        oled.text(str(score), 110, 0, 1)
        oled.show()
        utime.sleep_ms(50)

reset_game()
main()