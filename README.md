# Apex Exotics

Evan's exotic car trading business - where luxury meets performance.

## About
Apex Exotics specializes in trading rare and exotic vehicles, connecting discerning collectors with their dream cars.

## Vehicle Intelligence Platform

### VIN Decoder
Validates and decodes Vehicle Identification Numbers for authenticity verification and vehicle information extraction.

```bash
python vin_decoder.py KM8R54HE1LU066808
```

### BaT Monitor
Tracks Bring a Trailer auctions to analyze market trends and pricing for exotic vehicles.

```bash
cd bat-monitor
python monitor.py --add "https://bringatrailer.com/listing/..." --title "Vehicle Name"
python monitor.py --list
```

See `bat-monitor/README.md` for detailed usage.

## Architecture
Cloud-native, event-driven microservices:
- **VIN Validation Service** - Decode and validate VINs
- **Market Intelligence** - BaT auction monitoring and analysis
- **Forensic Documentation** - Service history and legal export (coming soon)
