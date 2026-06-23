import machine
import utime
import sys
import uselect
from bno055 import BNO055

print("=" * 50)
print("     STEP-BY-STEP BNO055 CALIBRATION TOOL    ")
print("=" * 50)

# Initialize I2C bus (50 kHz frequency is recommended for WCMCU-055 stability)
i2c = machine.SoftI2C(sda=machine.Pin(4), scl=machine.Pin(5), freq=50000)
sensor = BNO055(i2c, address=0x28)

# Configure keyboard polling
poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

def clear_keyboard_buffer():
    """Hard clear of the input buffer to prevent automatic step skipping"""
    utime.sleep_ms(300)
    while poller.poll(0):
        sys.stdin.read(1)

def wait_for_input(prompt):
    """Wait for user input before proceeding to the next step"""
    print(prompt)
    clear_keyboard_buffer()
    while True:
        if poller.poll(100):
            sys.stdin.readline()
            break
        utime.sleep_ms(10)

try:
    # -----------------------------------------------------------------
    # STEP 1: GYROSCOPE CALIBRATION
    # -----------------------------------------------------------------
    print("\n[ STEP 1/3 ]: GYROSCOPE STABILIZATION")
    print(" Place the sensor/antenna on a flat, stable surface and let it rest.")
    print(" Watch the log. Once 'G' reaches 3, click in the Thonny Shell and hit [ ENTER ]...")
    print("-" * 50)
    
    while True:
        _, gyro, _, _ = sensor.calibration_status
        print(f"Gyro Status -> [ G:{gyro} ] (Target: 3). Hit ENTER to proceed...", end="\r")
        
        if poller.poll(0):
            sys.stdin.readline()
            print(f"\n[ OK ] Step 1 complete! Gyro status: {gyro}")
            break
        utime.sleep_ms(100)

    # -----------------------------------------------------------------
    # STEP 2: COMPASS & TRUE NORTH ALIGNMENT
    # -----------------------------------------------------------------
    print("\n" + "-" * 50)
    print("[ STEP 2/3 ]: TRUE NORTH LOCK & MAGNETOMETER CALIBRATION")
    print(" Point the sensor's X-axis (antenna) exactly to MAGNETIC NORTH using a reference.")
    print(" Move the board in 'figure-8' patterns in the air to calibrate the magnetometer.")
    print(" Return the antenna to the North position and hold it steady.")
    print(" Once 'M' reaches 3, hit [ ENTER ] to lock the North offset!")
    print("-" * 50)
    
    north_offset = 0.0
    clear_keyboard_buffer()
    
    while True:
        _, _, _, mag = sensor.calibration_status
        heading, _, _ = sensor.euler
        print(f"Compass -> [ M:{mag} ] | Raw Heading: {heading:.2f}° | Hit ENTER to lock...", end="\r")
        
        if poller.poll(0):
            sys.stdin.readline()
            utime.sleep_ms(200) # Give it a moment to stabilize
            raw_heading, _, _ = sensor.euler
            print(f"\n[ OK ] Compass calibrated! North set at raw heading: {raw_heading:.2f}°")
            north_offset = -raw_heading
            break
        utime.sleep_ms(100)

    # -----------------------------------------------------------------
    # STEP 3: ACCELEROMETER CALIBRATION
    # -----------------------------------------------------------------
    print("\n" + "-" * 50)
    print("[ STEP 3/3 ]: ACCELEROMETER CALIBRATION")
    print(" Slowly tilt the platform/sensor to various angles (45-90 degrees).")
    print(" Once 'A' reaches 3, return the device to flat orientation and hit [ ENTER ].")
    print("-" * 50)
    
    clear_keyboard_buffer()
    
    while True:
        _, _, accel, _ = sensor.calibration_status
        print(f"Accel Status -> [ A:{accel} ] (Target: 3). Hit ENTER to finish...", end="\r")
        
        if poller.poll(0):
            sys.stdin.readline()
            print(f"\n[ OK ] Accelerometer successfully calibrated!")
            break
        utime.sleep_ms(100)

    # -----------------------------------------------------------------
    # FINAL RESULTS
    # -----------------------------------------------------------------
    print("\n" + "=" * 50)
    print("        CALIBRATION DATA FOR YOUR PROJECT        ")
    print("=" * 50)
    
    # Read the 22-byte calibration snapshot from the BNO memory
    iron_profile = sensor.get_calibration()
    
    print("\n Copy these lines into the top of your main.py:\n")
    print(f"calib_profile = {iron_profile}")
    print(f"COMPASS_OFFSET = {north_offset:.2f}")
    print("\n" + "=" * 50)

except Exception as e:
    print("\n[ CRITICAL ERROR ]: ", e)
