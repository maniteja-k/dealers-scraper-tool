# Quick Start Guide

## 1. Setup (One-Time)

```bash
# Clone/navigate to project
cd zigwheels-scraper

# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

## 2. Configure Brand

Edit `config/scraper_config.json`:

### Example 1: Scrape All Maruti Dealers Across India
```json
{
  "vehicle_types": {
    "cars": {
      "brands": [
        {
          "name": "maruti-suzuki",
          "locations": "all"
        }
      ]
    }
  }
}
```

### Example 2: Scrape 3 Brands
```json
{
  "vehicle_types": {
    "cars": {
      "brands": [
        {"name": "bmw", "locations": "all"},
        {"name": "audi", "locations": "all"},
        {"name": "mercedes-benz", "locations": "all"}
      ]
    }
  }
}
```

### Example 3: Specific Cities Only
```json
{
  "vehicle_types": {
    "cars": {
      "brands": [
        {
          "name": "hyundai",
          "locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad"]
        }
      ]
    }
  }
}
```

## 3. Run Scraper

```bash
python3 main.py
```

**Output**:
- File: `output/zigwheels_dealers_YYYYMMDD_HHMMSS.xlsx`
- Logs: `logs/scraper_YYYYMMDD_HHMMSS.log`

## 4. View Results

Open the Excel file in your preferred application:
- **Columns**: dealer_name, address, phone, email, city, state, location, brand, vehicle_type, etc.
- **Filter/Sort**: Use Excel features to analyze

---

## Common Configurations

### Scrape Maruti Across India (Estimated 30-60 min)
```json
{"name": "maruti-suzuki", "locations": "all"}
```

### Test with 2 Cities (5 min)
```json
{"name": "bmw", "locations": ["Hyderabad", "Chennai"]}
```

### Top 5 Metro Cities
```json
{
  "name": "maruti-suzuki",
  "locations": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]
}
```

---

## Brand Slugs Reference

| Brand | Slug |
|-------|------|
| Maruti Suzuki | `maruti-suzuki` |
| Hyundai | `hyundai` |
| Mahindra | `mahindra` |
| Tata | `tata` |
| BMW | `bmw` |
| Audi | `audi` |
| Mercedes Benz | `mercedes-benz` |
| Skoda | `skoda` |
| Volkswagen | `volkswagen` |
| Renault | `renault` |
| Jeep | `jeep` |
| MG Motor | `mg-motor` |
| Citroen | `citroen` |
| Kia | `kia` |
| Ford | `ford` |
| Tesla | `tesla` |
| BYD | `byd` |

---

## Troubleshooting

**No dealers found?**
- Verify brand slug is correct (check ZigWheels URL format)
- Try a specific city first instead of "all"

**Very slow?**
- Reduce `natural_delays` in config (but risk rate limiting)
- Scrape specific cities instead of "all"

**Browser not opening?**
- Set `"headless": false` in config temporarily to see browser
- Run `playwright install` again

---

## Next Steps

- See `SETUP.md` for detailed configuration options
- See `IMPLEMENTATION.md` for technical details
- Run `python3 test_quick.py` to verify everything works
