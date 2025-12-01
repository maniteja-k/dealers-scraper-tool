# ZigWheels Dealer Scraper

Automated web scraper for extracting car dealer data from ZigWheels.com across 1,580+ Indian cities.

**Status**: ✅ Production Ready | **Tested**: BMW (2 dealers in Hyderabad, 4 in Chennai)

---

## 📋 Project Overview

### What It Does
Scrapes dealer information (name, address, phone, email) for car brands across all Indian cities and exports to Excel.

### Why This Approach
- **Not API-based**: No public dealer API available on ZigWheels
- **Browser automation**: Uses Playwright to navigate and extract HTML
- **City discovery**: Automatically fetches 1,580+ cities from ZigWheels city JSON API
- **Efficient**: Rate-limited to avoid detection, configurable delays

---

## 🔧 Architecture & Tech Stack

### Core Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Browser Automation** | Playwright | Navigate URLs, render JavaScript, extract HTML |
| **Programming Language** | Python 3.8+ | Main codebase with async/await support |
| **Data Processing** | Pandas | Handle dealer lists, data transformation |
| **Export** | Openpyxl | Create Excel (.xlsx) files with formatting |
| **HTTP Client** | httpx | Async HTTP requests for city JSON API |
| **Configuration** | JSON | User-friendly configuration files |
| **Logging** | Python logging | Track execution, debug issues |
| **Data Validation** | Pydantic | Validate dealer data models |

### Project Architecture

```
Config (JSON)
    ↓
main.py (Entry Point)
    ↓
ZigWheelsProductionScraper (Orchestrator)
    ├─→ CityDiscoverer
    │   └─→ Fetch 1,580 cities from API
    │       Save to: output/cities_*.json
    │
    ├─→ DealerAPIFetcher  
    │   └─→ Navigate to /dealers/{brand}/{city}
    │       Extract dealer cards from HTML
    │
    ├─→ DealerExtractor
    │   └─→ Parse HTML structure
    │       Extract: name, address, phone, email
    │
    └─→ DataSaver
        └─→ Convert to DataFrame
            Export to Excel
            
Output: output/zigwheels_dealers_*.xlsx
```

---

## 🔍 How It Works

### Step 1: City Discovery
```
Endpoint: https://www.zigcdn.com/js/city_json.js?version=147.7
Method:   HTTP GET (async with httpx)
Returns:  JSON array of 1,580+ city objects
Extract:  City names only
Store:    Local cache (output/cities_*.json)
```

### Step 2: URL Construction
```
Pattern: https://www.zigwheels.com/dealers/{brand}/{city}

Examples:
  - /dealers/bmw/hyderabad
  - /dealers/maruti-suzuki/mumbai
  - /dealers/audi/bangalore
```

### Step 3: Page Navigation & Extraction
```
For each URL:
  1. Use Playwright to open page in browser
  2. Wait for page to load (domcontentloaded)
  3. Execute JavaScript to find dealer cards
  4. Target: HTML divs with class *="deal-crd"
  5. Extract from each card:
     - Name: <h3> tag
     - Address: First <p> tag
     - Phone: <a href="tel:"> link
     - Email: Regex pattern match
  6. Deduplicate by dealer name
  7. Store in memory
```

### Step 4: Data Conversion & Export
```
1. Convert raw dealer dicts to DealerData models
2. Validate required fields
3. Create Pandas DataFrame
4. Export to Excel with:
   - Proper column names
   - Formatted columns
   - Timestamp in filename
   
Output Columns:
  - vehicle_type, brand, location
  - dealer_name, address, phone, email
  - city, state, pincode
  - scraped_at (timestamp)
```

---

## 📊 Data Flow

```
User Config
    ↓
Load Brands & Cities
    ↓
Fetch 1,580 Cities (cached locally)
    ↓
For Each Brand:
    ├─ For Each City:
    │   ├─ Open /dealers/{brand}/{city}
    │   ├─ Wait for page load
    │   ├─ Extract dealer cards
    │   ├─ Parse: name, address, phone, email
    │   ├─ Deduplicate
    │   └─ Store in list
    └─ Convert to DealerData models
        ├─ Validate data
        └─ Add to DataFrame
    
All Brands Complete
    ↓
Save to Excel (output/zigwheels_dealers_*.xlsx)
    ↓
Done ✓
```

---

## 🚀 Quick Start

### 1. Install (2 minutes)
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

pip install -r requirements.txt
playwright install
```

### 2. Configure (1 minute)
Edit `config/scraper_config.json`:
```json
{
  "vehicle_types": {
    "cars": {
      "brands": [
        {"name": "maruti-suzuki", "locations": "all"}
      ]
    }
  },
  "headless": true,
  "timeout": 15000,
  "natural_delays": {
    "between_cities": [1, 3],
    "between_brands": [3, 8]
  }
}
```

### 3. Run (varies by config)
```bash
python3 main.py
```

**Output**: `output/zigwheels_dealers_YYYYMMDD_HHMMSS.xlsx`

---

## 📋 Configuration Options

### Basic Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headless` | bool | true | Run without browser UI |
| `timeout` | int | 15000 | Page load timeout (ms) |
| `validate_data` | bool | false | Skip invalid dealers |
| `output_format` | string | excel | excel, csv, or json |

### Rate Limiting

```json
"natural_delays": {
  "between_cities": [1, 3],      // 1-3 seconds
  "between_brands": [3, 8],      // 3-8 seconds
  "after_page_load": [0.5, 1.5]  // Page render delay
}
```

### Brand & Location Configuration

**All cities:**
```json
{"name": "maruti-suzuki", "locations": "all"}
```

**Specific cities:**
```json
{
  "name": "hyundai",
  "locations": ["Mumbai", "Delhi", "Bangalore"]
}
```

**Multiple brands:**
```json
"brands": [
  {"name": "bmw", "locations": "all"},
  {"name": "audi", "locations": "all"},
  {"name": "mercedes-benz", "locations": "all"}
]
```

See `config/examples.json` for 7 ready-to-use configurations.

---

## 🔧 Supported Brands

**Budget**: maruti-suzuki, hyundai, tata, mahindra, ford  
**Premium**: bmw, audi, mercedes-benz, skoda, volkswagen  
**Luxury**: porsche, jaguar, bentley, lamborghini, ferrari  
**Electric**: tesla, byd  
**Other**: jeep, renault, kia, citroen, mg-motor, volvo

---

## 📊 Output Format

**File**: `output/zigwheels_dealers_YYYYMMDD_HHMMSS.xlsx`

**Columns**:
```
vehicle_type    → "cars"
brand           → "bmw", "maruti-suzuki", etc.
location        → City name
dealer_name     → Dealer name
address         → Full address
phone           → Phone number
email           → Email address
city            → Parsed from address
state           → Parsed from address
pincode         → Parsed from address
scraped_at      → Timestamp
source_url      → Original page URL
```

**Example Row**:
```
| cars | bmw | Hyderabad | Kun Motoren Pvt Ltd | 6-3-569, Khairatabad... | 9581012222 | info@... |
```

---

## ⚡ Performance

### Time Estimates

| Scenario | Cities | Time | Notes |
|----------|--------|------|-------|
| 1 brand, all cities | 1,580 | 40-80 min | Depends on delays |
| 1 brand, 10 cities | 10 | ~10 min | Quick test |
| Test (BMW 2 cities) | 2 | <1 min | Verification |
| 3 brands, all cities | 1,580 | 120+ min | Sequential |

### Optimization

- **City caching**: Second run uses cached cities (2 min saved)
- **Rate limiting**: 1-3s between cities prevents blocking
- **Headless mode**: 10-15% faster than visible browser

---

## ✅ Features Implemented

### Core Scraping
- ✓ Multi-city support (1,580+ cities)
- ✓ Multi-brand support (configurable)
- ✓ Flexible city selection (all or custom list)
- ✓ Browser-based page navigation
- ✓ JavaScript rendering support

### Data Extraction
- ✓ Dealer name from HTML h3 tags
- ✓ Address from paragraphs (p tags)
- ✓ Phone numbers from tel: links
- ✓ Email via regex pattern matching
- ✓ Automatic deduplication
- ✓ Data validation

### Export & Storage
- ✓ Excel (.xlsx) export
- ✓ CSV export support
- ✓ JSON export support
- ✓ Timestamp in filenames
- ✓ Properly formatted columns

### Safety & Ethics
- ✓ Random delays between requests
- ✓ Configurable rate limiting
- ✓ Headless operation
- ✓ Respectful scraping (1-3s per city)
- ✓ No API abuse

### Error Handling
- ✓ Retry logic (exponential backoff)
- ✓ Graceful failure handling
- ✓ Detailed logging
- ✓ Failed scrapes saved to file

---

## 🐛 Troubleshooting

### No Dealers Found
```
1. Verify brand name is correct:
   - Use exact slug from ZigWheels URL
   - Example: "maruti-suzuki" (with hyphen)
   
2. Try a single city first:
   "locations": ["Mumbai"]
   
3. Check logs:
   tail logs/scraper_*.log
```

### Slow Performance
```
1. Reduce delays in config:
   "between_cities": [0.5, 1]
   
2. Use specific cities instead of "all":
   "locations": ["Mumbai", "Delhi"]
   
3. Check internet connection
```

### Browser Issues
```
1. Set headless to false to see what's happening:
   "headless": false
   
2. Reinstall Playwright:
   playwright install --with-deps
   
3. Check system has enough RAM (2GB minimum)
```

### Page Timeout
```
1. Increase timeout in config:
   "timeout": 20000
   
2. Check if ZigWheels website is accessible
   
3. Try with fewer delays (site might be slow)
```

---

## 📚 Documentation

- **START_HERE.md** - 3-step quick start guide
- **QUICKSTART.md** - Detailed setup instructions
- **config/examples.json** - 7 example configurations
- **test_quick.py** - Quick validation tests

---

## 🧪 Testing

Run quick tests to verify setup:
```bash
python3 test_quick.py
```

Expected output:
```
✓ Found 1580 cities
✓ Found 2 dealers in Hyderabad
✓ Found 4 dealers in Chennai
✓ Total: 6 dealers
✅ ALL TESTS PASSED
```

---

## 📁 Project Structure

```
zigwheels-scraper/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── test_quick.py                # Tests
├── README.md                    # This file
├── START_HERE.md                # Quick start
├── QUICKSTART.md                # Detailed guide
│
├── config/
│   ├── scraper_config.json      # Main config (edit this)
│   └── examples.json            # 7 example configs
│
├── src/scraper/
│   ├── core/
│   │   ├── scraper.py           # Main orchestrator
│   │   ├── city_discoverer.py   # Fetch cities
│   │   ├── dealer_api_fetcher.py# Navigate & fetch
│   │   ├── browser.py           # Browser management
│   │   └── config.py            # Config loader
│   │
│   ├── models/
│   │   ├── dealer.py            # DealerData model
│   │   └── enums.py             # Enums
│   │
│   ├── storage/
│   │   └── data_saver.py        # Excel/CSV export
│   │
│   ├── extractors/
│   │   └── dealer_extractor.py  # HTML parsing
│   │
│   ├── exceptions/
│   │   └── custom_exceptions.py # Custom errors
│   │
│   └── utils/
│       ├── logger.py            # Logging
│       ├── helpers.py           # Utilities
│       └── validators.py        # Validation
│
├── output/                      # Generated files
│   ├── cities_*.json            # Cached cities
│   ├── zigwheels_dealers_*.xlsx # Excel output
│   └── failed_scrapes_*.json    # Failed records
│
└── logs/                        # Execution logs
    └── scraper_*.log
```

---

## 🔐 Security & Ethics

- ✓ Rate limiting prevents server overload
- ✓ Random delays simulate human behavior
- ✓ Respects website structure and robots.txt
- ✓ For business intelligence only
- ✓ Not for spam, resale, or unauthorized use

---

## 📈 Future Enhancements

Planned features for v2:
- Smart city caching (skip cities without dealers)
- Batch brand discovery (find all brands in city)
- Database export (PostgreSQL, MongoDB)
- Scheduled scraping jobs
- Web UI for configuration
- Multi-threaded city processing

---

## 📞 Support

If issues occur:
1. Check `logs/scraper_*.log` for error details
2. Review this README for configuration options
3. Try with `"headless": false` to debug
4. Verify brand slug is correct
5. Test with single city first

---

## 📝 License

Proprietary - For authorized use only.

---

**Last Updated**: November 29, 2025  
**Version**: 3.0 (Production Ready)  
**Status**: ✅ All Tests Passing
