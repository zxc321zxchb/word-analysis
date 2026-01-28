#!/usr/bin/env python3
"""
Test script to verify the pagination endpoint works correctly.
"""
import json
import urllib.request
import urllib.error

def test_pagination_endpoint():
    """Test the pagination endpoint with different page sizes."""
    # API endpoint
    api_url = 'http://localhost:8000/api/v1/documents'
    
    print(f"Testing pagination endpoint: {api_url}")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        (1, 10, "First page, 10 items"),
        (1, 5, "First page, 5 items"),
        (2, 10, "Second page, 10 items"),
        (1, 20, "First page, 20 items"),
    ]
    
    for page, page_size, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Request: page={page}, page_size={page_size}")
        
        try:
            # Build request URL
            url = f"{api_url}?page={page}&page_size={page_size}"
            
            # Send request
            with urllib.request.urlopen(url) as response:
                data = response.read().decode('utf-8')
                result = json.loads(data)
            
            print(f"Status: {'Success' if response.status == 200 else 'Error'}")
            print(f"Total documents: {result.get('total')}")
            print(f"Current page: {result.get('page')}")
            print(f"Page size: {result.get('page_size')}")
            print(f"Total pages: {result.get('pages')}")
            print(f"Items returned: {len(result.get('items', []))}")
            
            # Show first few items
            if result.get('items'):
                print(f"\nFirst 3 items:")
                for i, item in enumerate(result.get('items')[:3]):
                    print(f"  {i+1}. ID: {item.get('id')}")
                    print(f"     Filename: {item.get('original_filename')}")
                    print(f"     Size: {item.get('file_size')} bytes")
                    print(f"     Sections: {item.get('sections_count')}")
                    print(f"     Created: {item.get('created_at')}")
                    print()
                    
        except urllib.error.URLError as e:
            print(f"Error: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == '__main__':
    test_pagination_endpoint()
