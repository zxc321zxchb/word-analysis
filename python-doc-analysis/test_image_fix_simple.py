#!/usr/bin/env python3
"""Simple test script to verify image parsing fix using urllib."""
import urllib.request
import urllib.error
import json
import os
import mimetypes

# Test file path
TEST_FILE_PATH = "/Users/life/Documents/网凝/副本厦门市轨道交通4号线（后溪至翔安机场段）工程车辆采购项目用户需求书（最终版ok）.docx"

# API endpoint
API_URL = "http://localhost:8000/api/v1/documents/parse"

print(f"Testing image parsing with file: {TEST_FILE_PATH}")
print(f"Using API endpoint: {API_URL}")
print()

# Check if file exists
if not os.path.exists(TEST_FILE_PATH):
    print(f"Error: File not found at {TEST_FILE_PATH}")
    exit(1)

# Check file size
file_size = os.path.getsize(TEST_FILE_PATH)
print(f"File size: {file_size} bytes")
print()

# Prepare file for upload
try:
    # Read file content
    with open(TEST_FILE_PATH, "rb") as f:
        file_content = f.read()
    
    # Prepare multipart form data
    boundary = "---------------------------974767299852498929531610575"
    filename = os.path.basename(TEST_FILE_PATH)
    
    # Create form data
    form_data = (
        f"{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
        f"Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n"
        f"\r\n"
    ).encode('utf-8')
    
    form_data += file_content
    form_data += (
        f"\r\n{boundary}--\r\n"
    ).encode('utf-8')
    
    # Prepare request
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(form_data)),
    }
    
    req = urllib.request.Request(API_URL, data=form_data, headers=headers, method='POST')
    
    # Send request to API
    print("Sending file to API for parsing...")
    with urllib.request.urlopen(req, timeout=60) as response:
        # Check response
        if response.status == 201:
            print("\n✅ API Response:")
            print(f"Status code: {response.status}")
            
            # Parse JSON response
            data = json.loads(response.read().decode('utf-8'))
            
            print(f"Document ID: {data['document_id']}")
            print(f"Filename: {data['filename']}")
            print(f"Sections count: {data['sections_count']}")
            print()
            
            # Find section 1.1.1 and check for images
            print("🔍 Checking section 1.1.1 for images...")
            section_1_1_1 = None
            for section in data['sections']:
                if section['number_path'] == "1.1.1":
                    section_1_1_1 = section
                    break
            
            if section_1_1_1:
                print(f"Found section 1.1.1: {section_1_1_1['title']}")
                print(f"Number of images: {len(section_1_1_1.get('images', []))}")
                
                if section_1_1_1.get('images', []):
                    print("✅ Images found in section 1.1.1!")
                    for i, image in enumerate(section_1_1_1['images']):
                        print(f"  Image {i+1}: {image['filename']} ({image['mime_type']})")
                else:
                    print("❌ No images found in section 1.1.1")
            else:
                print("❌ Section 1.1.1 not found")
                
            # Check all sections for images
            print()
            print("📊 Summary of images in all sections:")
            sections_with_images = 0
            total_images = 0
            
            for section in data['sections']:
                num_images = len(section.get('images', []))
                if num_images > 0:
                    sections_with_images += 1
                    total_images += num_images
                    print(f"  Section {section['number_path']}: {num_images} images")
            
            print()
            print(f"Total sections with images: {sections_with_images}")
            print(f"Total images found: {total_images}")
            
        else:
            print(f"\n❌ API Error:")
            print(f"Status code: {response.status}")
            print(f"Error message: {response.read().decode('utf-8')}")
            
except urllib.error.HTTPError as e:
    print(f"\n❌ HTTP Error:")
    print(f"Status code: {e.code}")
    print(f"Error message: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"\n❌ Test failed with error:")
    print(f"{str(e)}")
