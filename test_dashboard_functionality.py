#!/usr/bin/env python3
"""
Test script to verify dashboard functionality end-to-end
"""

import requests
import json

def test_dashboard_functionality():
    """Test the complete dashboard functionality"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 TESTING DASHBOARD FUNCTIONALITY")
    print("=" * 50)
    
    # Test 1: Test API endpoint directly
    print("📡 Test 1: API Endpoint")
    try:
        response = requests.get(f"{base_url}/uav-service/api/dashboard-stats")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response Data: {json.dumps(data, indent=2)}")
            
            # Validate data structure
            expected_keys = ['total_incidents', 'open_incidents', 'sla_breached', 'maintenance_due']
            missing_keys = [key for key in expected_keys if key not in data]
            
            if missing_keys:
                print(f"   ❌ Missing keys: {missing_keys}")
            else:
                print(f"   ✅ All expected keys present")
                
            # Check if values are reasonable
            for key, value in data.items():
                if isinstance(value, int) and value >= 0:
                    print(f"   ✅ {key}: {value} (valid)")
                else:
                    print(f"   ⚠️  {key}: {value} (unexpected type or value)")
        else:
            print(f"   ❌ API Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {e}")
    
    # Test 2: Test dashboard page
    print(f"\n🌐 Test 2: Dashboard Page")
    try:
        response = requests.get(f"{base_url}/uav-service/dashboard")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Dashboard page loads successfully")
            
            # Check if JavaScript is present
            content = response.text
            if 'loadDashboardStats' in content:
                print(f"   ✅ JavaScript function found")
            else:
                print(f"   ❌ JavaScript function missing")
                
            if 'api/dashboard-stats' in content:
                print(f"   ✅ API endpoint reference found")
            else:
                print(f"   ❌ API endpoint reference missing")
        else:
            print(f"   ❌ Dashboard Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {e}")
    
    print(f"\n📋 Test Summary:")
    print(f"   • API endpoint should return JSON with statistics")
    print(f"   • Dashboard page should load with JavaScript")
    print(f"   • Browser console should show debug logs")
    print(f"   • Numbers should replace dashes (-) automatically")
    
    print(f"\n🔧 Troubleshooting:")
    print(f"   1. Open browser console (F12) on dashboard page")
    print(f"   2. Look for console.log messages")
    print(f"   3. Check for any JavaScript errors")
    print(f"   4. Verify API calls in Network tab")

if __name__ == '__main__':
    test_dashboard_functionality()
