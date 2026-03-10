# VSeeBox Channel Switching Options

## Option 1: Broadlink RM4 Mini IR Blaster ($25)

**Setup:**
```bash
pip install broadlink
```

**Learn remote codes:**
```python
import broadlink
device = broadlink.discover()[0]
device.auth()
device.enter_learning()  # Press VSeeBox remote button
ir_code = device.check_data()
```

**Send channel command:**
```python
device.send_data(ir_code)
```

## Option 2: Raspberry Pi + IR LED ($5)
- Use GPIO pins + IR LED
- LIRC software
- More DIY but cheaper

## Option 3: Arduino + IR LED ($10)
- Program Arduino to send IR codes
- Serial commands from Mac

## Option 4: Network Control (if VSeeBox has API)
- Check if VSeeBox exposes HTTP/WebSocket API
- Reverse engineer Android app traffic

## Recommended: Broadlink RM4 Mini
- Easiest setup
- Python library
- Can control multiple devices
- Amazon: ~$25

Once you have it, I'll write the auto-switcher that:
1. Checks excitement scores every 30s
2. Switches to most exciting game
3. Logs all switches
