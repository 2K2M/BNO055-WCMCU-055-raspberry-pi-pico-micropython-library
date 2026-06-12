# BNO055-WCMCU-055-raspberry-pi-pico-micropython-library
A lightweight I2C MicroPython library for the Bosch BNO055 (WCMCU-055) 9-axis sensor on Raspberry Pi Pico, featuring an interactive zero-dependency calibration suite with magnetic True-North alignment.
If you are using a cheap Chinese **WCMCU-055** clone board, it **will not work out of the box** with standard I2C code. You must perform the following hardware modifications:

1. **Protocol Selection Jumpers:** You must physically short (solder bridge) both the **S0** and **S1** jumpers located at the bottom of the board to force the internal MCU into I2C mode instead of UART.
2. **I2C Pin Mapping:** * **ATX** pin on the board acts as **SDA**
   * **LRX** pin on the board acts as **SCL**
3. **Address Pin Pull-down:** To prevent the communication bus from floating, you must pull the address select pin down to Ground (**GND**).

<img width="169" height="205" alt="Wiring" src="https://github.com/user-attachments/assets/929802fa-d556-4985-9c6a-f1738abc8595" />


* **Strict 50kHz I2C Clock:** You **MUST** initialize `SoftI2C` at exactly `freq=50000` (50 kHz). At 100 kHz or higher, the co-processor on these clone boards encounters internal timing timeouts, drops data packets, and locks up the entire bus (`ENODEV` / `EIO`).
* **The Address Bug:** When running an I2C bus scanner on the Raspberry Pi Pico, the board responds and shows up at address **`0x29`**. However, due to bit-shifting quirks in the clone firmware's implementation during actual memory register reading/writing, the library functions only successfully communicate when initialized with address **`0x28`**. If you initialize it at `0x29`, register reads will fail.

---

## 🎯 Advanced Multi-Stage Interactive Calibration Suite

This project includes a specialized `сalibration.py` script designed for absolute real-world tracking accuracy (e.g., antenna rotators):

* **Strict Hardware Sequence:** Calibrates layers step-by-step (**Gyroscope ➡️ Compass/True-North ➡️ Accelerometer**).
* **Manual True-North Zeroing:** Allows you to physically align your device's X-axis with the real-world North using a reference compass, hit `ENTER`, and visually freeze the math offset (`COMPASS_OFFSET`) into your final deployment profile.
* **Anti-Skip Terminal Lock:** Bypasses MicroPython IDE buffer overflow glitches, ensuring the calibration manager never auto-skips steps.
