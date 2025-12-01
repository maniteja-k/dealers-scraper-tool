#!/usr/bin/env python3
"""Quick validation test"""

import asyncio
import json
from pathlib import Path
from src.scraper.core.city_discoverer import CityDiscoverer
from src.scraper.core.dealer_api_fetcher import DealerAPIFetcher
from playwright.async_api import async_playwright

async def test_cities():
    """Test city discovery"""
    print("=" * 60)
    print("TEST 1: City Discovery")
    print("=" * 60)
    
    city_discoverer = CityDiscoverer()
    cities = await city_discoverer.discover_all_cities()
    
    print(f"✓ Found {len(cities)} cities")
    print(f"Sample: {cities[:5]}")
    assert len(cities) > 1000, "City count too low"
    assert "Hyderabad" in cities, "Hyderabad not found"
    assert "Chennai" in cities, "Chennai not found"
    print("✓ PASS\n")

async def test_dealers():
    """Test dealer extraction"""
    print("=" * 60)
    print("TEST 2: Dealer Extraction (BMW in Hyderabad)")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        fetcher = DealerAPIFetcher()
        dealers = await fetcher.get_dealers(page, "bmw", "Hyderabad")
        
        print(f"✓ Found {len(dealers)} dealers")
        for d in dealers:
            print(f"  - {d.get('dealer_name')}")
        
        assert len(dealers) == 2, f"Expected 2 dealers, got {len(dealers)}"
        print("✓ PASS\n")
        
        await browser.close()

async def test_multiple_cities():
    """Test multiple cities"""
    print("=" * 60)
    print("TEST 3: BMW in Multiple Cities")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        fetcher = DealerAPIFetcher()
        
        results = {}
        for city in ["Hyderabad", "Chennai"]:
            dealers = await fetcher.get_dealers(page, "bmw", city)
            results[city] = len(dealers)
            print(f"  {city}: {len(dealers)} dealers")
        
        total = sum(results.values())
        print(f"✓ Total: {total} dealers")
        
        assert results["Hyderabad"] == 2, "Hyderabad count mismatch"
        assert results["Chennai"] == 4, "Chennai count mismatch"
        print("✓ PASS\n")
        
        await browser.close()

async def main():
    try:
        await test_cities()
        await test_dealers()
        await test_multiple_cities()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYou can now run: python3 main.py")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
