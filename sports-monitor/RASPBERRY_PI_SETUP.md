# Raspberry Pi IR Transmitter Setup

## Hardware Setup
1. IR LED (940nm)
2. 2N2222 transistor
3. 100Ω resistor
4. Connect to Pi GPIO:
   - GPIO 17 → Transistor base (through 1kΩ resistor)
   - Transistor collector → IR LED cathode
   - IR LED anode → 3.3V (through 100Ω resistor)
   - Transistor emitter → Ground

## Software Setup

```bash
# On Raspberry Pi
sudo apt-get update
sudo apt-get install lirc python3-pip

# Configure LIRC
sudo nano /etc/lirc/lirc_options.conf
# Set: driver = default
# Set: device = /dev/lirc0

# Enable IR transmit on GPIO 17
sudo nano /boot/config.txt
# Add: dtoverlay=gpio-ir-tx,gpio_pin=17

sudo reboot
```

## Python Server on Pi

```python
# ir_server.py
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/send/<button>')
def send_ir(button):
    # Send IR command using irsend
    subprocess.run(['irsend', 'SEND_ONCE', 'vseebox', button])
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

## From Mac

```python
import requests
requests.get('http://pi_ip:8888/send/CHANNEL_UP')
```

Want me to write the complete setup script?
