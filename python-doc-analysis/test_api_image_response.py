#!/usr/bin/env python3
"""Test script to verify API returns images in response."""
import io
import os
import base64
import requests

# Test file path
TEST_FILE_PATH = "/app/test_doc_with_images.docx"

print(f"Testing API image response with file: {TEST_FILE_PATH}")
print()

# Check if file exists
if not os.path.exists(TEST_FILE_PATH):
    print(f"Error: File not found at {TEST_FILE_PATH}")
    print("Please copy the test file to the Docker container first.")
    exit(1)

# API endpoint
API_URL = "http://localhost:8000/api/v1/documents/parse"

print(f"Using API endpoint: {API_URL}")
print()

# Test API response
try:
    # Read file content
    with open(TEST_FILE_PATH, "rb") as f:
        files = {"file": (os.path.basename(TEST_FILE_PATH), f)}
    
    # Send request to API
    print("Sending file to API for parsing...")
    response = requests.post(API_URL, files=files, timeout=60)
    
    # Check response
    if response.status_code == 201:
        print("\n✅ API Response:")
        print(f"Status code: {response.status_code}")
        
        # Parse JSON response
        data = response.json()
        
        print(f"Document ID: {data['document_id']}")
        print(f"Filename: {data['filename']}")
        print(f"Sections count: {data['sections_count']}")
        print()
        
        # Find sections with images
        print("🔍 Checking sections for images...")
        sections_with_images = []
        for section in data['sections']:
            if section.get('images', []):
                sections_with_images.append(section)
                print(f"  Section {section['number_path']}: {section['title']}")
                print(f"    Number of images: {len(section['images'])}")
                for i, image in enumerate(section['images']):
                    print(f"      Image {i+1}: {image['filename']} ({image['mime_type']})")
        print()
        
        if sections_with_images:
            print(f"✅ Total sections with images: {len(sections_with_images)}")
        else:
            print("❌ No sections found with images!")
            
        # Check section 1.1.1 specifically
        print("\n🔍 Checking section 1.1.1:")
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
                    print(f"  Image {i+1}: {image['filename']}")
            else:
                print("❌ No images found in section 1.1.1")
        else:
            print("❌ Section 1.1.1 not found")
            
    else:
        print(f"\n❌ API Error:")
        print(f"Status code: {response.status_code}")
        print(f"Error message: {response.text}")
        
except Exception as e:
    print(f"\n❌ Test failed with error:")
    print(f"{str(e)}")
    import traceback
    traceback.print_exc()
