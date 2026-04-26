# Smart Bag Theft Detection System

**Course:** Microprocessor and Computer Architecture (MPCA)  
**Institution:** PES University, Bengaluru  
**Program:** B.Tech Computer Science and Engineering (Artificial Intelligence & Machine Learning)

## Team Members

- **Aarav Yuval Babu Girish** (SRN: PES1UG24AM004)
- **Ahan A Mysore** (SRN: PES1UG24AM019)
- **Amogh Shetty** (SRN: PES1UG24AM034)

## Project Overview

The Smart Bag Theft Detection System is an Internet of Things (IoT) security solution engineered to mitigate the risk of personal property theft in public spaces. By leveraging an ESP32 microcontroller running MicroPython, the system interfaces with a sensor fusion array to provide real-time, localized monitoring of a user's bag. The system hosts a localized web server over Wi-Fi, allowing the user to seamlessly arm and disarm the security protocol via a smartphone interface. Upon detecting unauthorized access or movement, the system triggers a physical auditory alarm and a digital web alert.

## Video Demonstration

The following video demonstrates the hardware setup, the web interface, and the system's real-time response to simulated theft events.

https://github.com/PES1UG24AM004/MPCA-Bag-Theft-Detector/assets/demo_vid.mp4
_(Note: Once pushed to GitHub, this link will automatically render as an embedded video player.)_

## Hardware Architecture

The system utilizes the following component matrix, wired to specific General-Purpose Input/Output (GPIO) pins on the ESP32:

- **ESP32 Microcontroller:** Functions as the central processing unit and web server host.
- **MPU6050 Module (Accelerometer & Gyroscope):** Interfaces with the ESP32 via the I2C protocol (SCL: Pin 22, SDA: Pin 21). It monitors the orientation and acceleration vectors to detect sudden movement.
- **LDR Sensor Module:** A Light Dependent Resistor connected to a digital input (Pin 26). It monitors the ambient light state to detect if the bag has been opened or tampered with.
- **5V Active Buzzer:** A piezoelectric audio signaling device connected to a digital output (Pin 25), providing an immediate auditory deterrent.

## Software Design and Implementation

The system firmware is developed using MicroPython. It utilizes a continuous execution loop that handles socket connections for the web server while independently polling sensor states.

### Key Modules

- `network` & `socket`: Manages Wi-Fi station interface (STA_IF) connectivity and hosts the HTTP web server on port 80.
- `machine.Pin` & `machine.I2C`: Manages GPIO states and I2C serial communication.
- `mpu6050`: A custom driver to parse raw accelerometer and gyroscope data.

### Operational Workflow

1. **Network Initialization:** Upon boot, the ESP32 connects to a predefined Wi-Fi network and allocates an IP address for the web server.
2. **Baseline Calibration:** The system establishes a baseline reading from the MPU6050 to understand its resting state.
3. **Active Monitoring:** The microcontroller continuously calculates the absolute difference between current kinetic data and the baseline. It simultaneously polls the digital state of the LDR.
4. **Intrusion Detection:**
   - _Kinetic Intrusion:_ If the kinetic difference exceeds the programmed threshold (4000) for longer than 0.7 seconds, a movement flag is triggered.
   - _Light Intrusion:_ If the LDR registers a sustained state change for longer than 2.0 seconds, a light anomaly flag is triggered.
5. **Alarm Trigger:** If an intrusion flag is raised while the system is in the "ARMED" state, the ESP32 pulses the buzzer (LOW to trigger, HIGH to silence) and dynamically updates the HTTP response to serve a red "THEFT DETECTED" banner.
6. **Resolution:** The alarm state and buzzer sequence persist until explicitly terminated via a `/disarm` GET request from the user's web interface.
