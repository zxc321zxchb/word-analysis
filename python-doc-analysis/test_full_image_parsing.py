#!/usr/bin/env python3
"""Test script to verify full image parsing with parse_by_heading method."""
import io
import os
from src.doc_analysis.parser.docx import DocxParser

# Test file path
TEST_FILE_PATH = "/Users/life/Documents/网凝/副本厦门市轨道交通4号线（后溪至翔安机场段）工程车辆采购项目用户需求书（最终版ok）.docx"

print(f"Testing full image parsing with file: {TEST_FILE_PATH}")
print()

# Check if file exists
if not os.path.exists(TEST_FILE_PATH):
    print(f"Error: File not found at {TEST_FILE_PATH}")
    exit(1)

# Check file size
file_size = os.path.getsize(TEST_FILE_PATH)
print(f"File size: {file_size} bytes")
print()

# Test full parsing
try:
    # Read file content
    with open(TEST_FILE_PATH, "rb") as f:
        file_content = f.read()
    
    # Create parser instance
    parser = DocxParser()
    
    # Parse document using heading styles
    print("Parsing document with parse_by_heading method...")
    parsed = parser.parse_by_heading(file_content, os.path.basename(TEST_FILE_PATH))
    
    print(f"\n✅ Parsing completed successfully!")
    print(f"Number of sections: {len(parsed.sections)}")
    print(f"Number of extracted images: {len(parser._images)}")
    print()
    
    # Print image details
    print("🔍 Extracted images:")
    for i, image in enumerate(parser._images):
        print(f"  Image {i+1}: {image.filename} ({image.mime_type})")
        print(f"    Base64 data length: {len(image.base64_data)} characters")
    print()
    
    # Find sections with images
    print("📊 Sections with images:")
    sections_with_images = []
    for section in parsed.sections:
        if section.images:
            sections_with_images.append(section)
            print(f"  Section {section.number_path}: {section.title}")
            print(f"    Number of images: {len(section.images)}")
            for i, image in enumerate(section.images):
                print(f"      Image {i+1}: {image.filename}")
    print()
    
    if sections_with_images:
        print(f"✅ Total sections with images: {len(sections_with_images)}")
    else:
        print("❌ No sections found with images!")
        
    # Check section 1.1.1 specifically
    print("\n🔍 Checking section 1.1.1:")
    section_1_1_1 = None
    for section in parsed.sections:
        if section.number_path == "1.1.1":
            section_1_1_1 = section
            break
    
    if section_1_1_1:
        print(f"Found section 1.1.1: {section_1_1_1.title}")
        print(f"Number of images: {len(section_1_1_1.images)}")
        if section_1_1_1.images:
            print("✅ Images found in section 1.1.1!")
            for i, image in enumerate(section_1_1_1.images):
                print(f"  Image {i+1}: {image.filename}")
        else:
            print("❌ No images found in section 1.1.1")
    else:
        print("❌ Section 1.1.1 not found")
        
    # Check if images are properly referenced
    print("\n🔍 Checking image references:")
    for section in parsed.sections:
        if section.images:
            print(f"Section {section.number_path} has {len(section.images)} images")
            for i, image in enumerate(section.images):
                # Check if image exists in parser._images
                image_found = False
                for parser_image in parser._images:
                    if parser_image.filename == image.filename:
                        image_found = True
                        break
                if image_found:
                    print(f"  Image {i+1}: {image.filename} - ✅ Found in parser._images")
                else:
                    print(f"  Image {i+1}: {image.filename} - ❌ Not found in parser._images")
    
    print()
    print("📋 Summary:")
    print(f"Total sections: {len(parsed.sections)}")
    print(f"Total extracted images: {len(parser._images)}")
    print(f"Total sections with images: {len(sections_with_images)}")
    
except Exception as e:
    print(f"\n❌ Test failed with error:")
    print(f"{str(e)}")
    import traceback
    traceback.print_exc()
