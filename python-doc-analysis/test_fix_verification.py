#!/usr/bin/env python3
"""
Test script to verify that images are now included in the images field of the API response.
"""
import os
import json
import urllib.request
import urllib.error

def test_image_inclusion():
    """Test that images appear in both content_html and images fields."""
    # API endpoint
    api_url = 'http://localhost:8000/api/v1/documents/parse'
    
    # File path provided by user
    file_path = '/Users/life/Documents/网凝/副本厦门市轨道交通4号线（后溪至翔安机场段）工程车辆采购项目用户需求书（最终版ok）.docx'
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return False
    
    print(f"Testing with file: {file_path}")
    print(f"API endpoint: {api_url}")
    
    try:
        # Prepare multipart/form-data request
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        filename = os.path.basename(file_path)
        
        # Build request body
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f'Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n'
            f'\r\n'
        ).encode('utf-8')
        
        body += file_content
        body += (
            f'\r\n--{boundary}--\r\n'
        ).encode('utf-8')
        
        # Prepare request
        req = urllib.request.Request(api_url)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        req.add_header('Content-Length', str(len(body)))
        req.method = 'POST'
        
        # Send request
        with urllib.request.urlopen(req, body) as response:
            data = response.read().decode('utf-8')
            result = json.loads(data)
        
        print(f"\nResponse received:")
        print(f"Document ID: {result.get('document_id')}")
        print(f"Filename: {result.get('filename')}")
        print(f"Sections count: {result.get('sections_count')}")
        
        # Check for sections with images
        sections_with_images = []
        for section in result.get('sections', []):
            # Check if images field exists and has content
            if section.get('images') and len(section.get('images', [])) > 0:
                sections_with_images.append(section)
                print(f"\nSection with images found:")
                print(f"  Number path: {section.get('number_path')}")
                print(f"  Level: {section.get('level')}")
                print(f"  Title: {section.get('title')}")
                print(f"  Images count: {len(section.get('images', []))}")
                
                # Show first image details
                if section.get('images'):
                    first_image = section.get('images')[0]
                    print(f"  First image: {first_image.get('filename')}")
                    print(f"  MIME type: {first_image.get('mime_type')}")
                    print(f"  Has base64 data: {'Yes' if first_image.get('base64_data') else 'No'}")
            
            # Check if content_html contains images
            if '<img src="data:image' in section.get('content_html', ''):
                print(f"\nSection with images in content_html:")
                print(f"  Number path: {section.get('number_path')}")
                print(f"  Level: {section.get('level')}")
        
        if sections_with_images:
            print(f"\n✓ SUCCESS: Found {len(sections_with_images)} sections with images in the images field")
            return True
        else:
            print(f"\n✗ FAILURE: No sections found with images in the images field")
            return False
            
    except urllib.error.URLError as e:
        print(f"Error connecting to API: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_image_inclusion()
    exit(0 if success else 1)
