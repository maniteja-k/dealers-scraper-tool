# 🚀 START HERE - ZigWheels Dealer Scraper

## What You Have

A **production-ready automated scraper** that fetches car dealer data from ZigWheels across all 1,580+ Indian cities.

**Tested & Verified**: BMW dealers
- Hyderabad: 2 dealers ✓
- Chennai: 4 dealers ✓

---

## 3-Step Quick Start

### Step 1: Install (2 minutes)
```bash
# Create environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install
```

### Step 2: Configure (1 minute)
Edit `config/scraper_config.json`:
```json
{
  "brands": [
    {"name": "maruti-suzuki", "locations": "all"}
  ]
}
```

Choose your brand from:
- **Budget**: maruti-suzuki, hyundai, tata, mahindra, ford
- **Premium**: bmw, audi, mercedes-benz, skoda, volkswagen  
- **Luxury**: porsche, jaguar, lamborghini, ferrari
- **Electric**: tesla, byd

### Step 3: Run (varies)
```bash
python3 main.py
```

Output: `output/zigwheels_dealers_*.xlsx`

---

## What Happens

1. **City Discovery** → Automatically fetches 1,580+ cities from ZigWheels API
2. **URL Building** → Creates URLs like `/dealers/maruti-suzuki/mumbai`
3. **Browser Navigation** → Opens each city's dealer page
4. **Data Extraction** → Parses dealer name, address, phone, email
5. **Excel Export** → Saves all dealers to Excel file

**Time**: ~1 second per city × 1,580 = ~26-80 minutes depending on delays

---

## Example Configurations

### Single Brand, All Cities
```json
{"name": "maruti-suzuki", "locations": "all"}
```

### Multiple Brands
```json
[
  {"name": "bmw", "locations": "all"},
  {"name": "audi", "locations": "all"},
  {"name": "mercedes-benz", "locations": "all"}
]
```

### Specific Cities Only (Faster)
```json
{
  "name": "hyundai",
  "locations": ["Mumbai", "Delhi", "Bangalore"]
}
```

---

## Output

**File**: Excel spreadsheet with columns:
- Dealer Name
- Address (complete)
- Phone Number
- Email
- City, State, Pincode
- Brand, Vehicle Type
- Timestamp

---

## Documentation

If you need more details:

- **QUICKSTART.md** → 5-minute setup with examples
- **SETUP.md** → Complete configuration guide
- **IMPLEMENTATION.md** → Technical architecture
- **PROJECT_SUMMARY.md** → Features overview
- **config/examples.json** → 7 ready-to-use configurations

---

## Verify It Works

Test the scraper with 2 cities (takes <1 minute):
```bash
# Edit config/scraper_config.json:
{"name": "bmw", "locations": ["Hyderabad", "Chennai"]}

# Run:
python3 main.py

# Expected output: 6 dealers (2 + 4)
```

---

## Next Steps

1. ✅ Install dependencies (copy Step 1 above)
2. ✅ Edit `config/scraper_config.json` with your brand
3. ✅ Run `python3 main.py`
4. ✅ Open generated Excel file in `output/`

---

## Common Questions

**Q: How long does it take?**
- All 1,580 cities × 1 brand: 26-80 minutes (depending on delays)
- 10 cities × 1 brand: ~10 minutes
- Test (2 cities): <1 minute

**Q: Which brands work?**
- Any brand that appears on ZigWheels
- Check URL format: `zigwheels.com/dealers/{brand}/{city}`

**Q: Can I stop and resume?**
- Currently no, but you can scrape specific cities by editing config

**Q: Does it get blocked?**
- Has rate limiting (1-3s delays) to avoid detection
- If blocked, increase delays in config

**Q: What if there are no dealers in a city?**
- Cities with no dealers show 0 dealers (that's correct)

---

## Troubleshooting

**No dealers found?**
```
1. Check brand name is correct (lowercase with hyphens)
2. Try a single city first: ["Mumbai"]
3. Check logs in: tail logs/scraper_*.log
```

**Slow/timing out?**
```
1. Increase timeout in config: "timeout": 20000
2. Reduce number of cities
3. Check your internet connection
```

**Browser issues?**
```
1. Set "headless": false in config to see browser
2. Run: playwright install --with-deps
3. Check system has enough RAM
```

---

## That's It!

You now have everything you need. Just:

1. Install (copy commands from Step 1)
2. Configure (edit config file)
3. Run (python3 main.py)
4. View results (open Excel file)

For detailed information, see the documentation files listed above.

---

**Ready?** Start with Step 1 above! 🚀
