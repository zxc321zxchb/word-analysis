#!/usr/bin/env python3
"""Test script to verify image extraction from Word document."""
import io
import base64
import os
from docx import Document

# Test file path
TEST_FILE_PATH = "/Users/life/Documents/网凝/副本厦门市轨道交通4号线（后溪至翔安机场段）工程车辆采购项目用户需求书（最终版ok）.docx"

print(f"Testing image extraction with file: {TEST_FILE_PATH}")
print()

# Check if file exists
if not os.path.exists(TEST_FILE_PATH):
    print(f"Error: File not found at {TEST_FILE_PATH}")
    exit(1)

# Check file size
file_size = os.path.getsize(TEST_FILE_PATH)
print(f"File size: {file_size} bytes")
print()

# Test image extraction
try:
    # Load document
    doc = Document(TEST_FILE_PATH)
    print("Document loaded successfully.")
    print()
    
    # Extract images
    print("Extracting images...")
    images = []
    image_index = 0
    
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            try:
                image_data = rel.target_part.blob
                base64_str = base64.b64encode(image_data).decode("utf-8")
                mime_type = rel.target_part.content_type
                
                print(f"Found image: {rel.target_ref.split('/')[-1]}")
                print(f"  MIME type: {mime_type}")
                print(f"  Size: {len(image_data)} bytes")
                print(f"  Base64 length: {len(base64_str)} characters")
                print()
                
                images.append({
                    "filename": rel.target_ref.split("/")[-1],
                    "mime_type": mime_type,
                    "size": len(image_data)
                })
                
                image_index += 1
            except Exception as e:
                print(f"Error extracting image: {str(e)}")
                print()
    
    print(f"Total images found: {len(images)}")
    print()
    
    if images:
        print("✅ Images extracted successfully!")
    else:
        print("❌ No images found in the document.")
        
    # Test paragraph image detection
    print("\nTesting paragraph image detection...")
    for i, element in enumerate(doc.element.body):
        from docx.oxml.text.paragraph import CT_P
        if isinstance(element, CT_P):
            # Create Paragraph object from element
            from docx.text.paragraph import Paragraph
            paragraph = Paragraph(element, doc)
            text = paragraph.text.strip()
            
            # Check for images in this paragraph
            has_images = False
            for child in paragraph._element.iter():
                if child.tag.endswith('drawing'):
                    has_images = True
                    break
            
            if has_images:
                print(f"Paragraph {i+1} contains images!")
                print(f"  Text: {text[:100]}..." if text else "  No text")
                print()
                
except Exception as e:
    print(f"Error: {str(e)}")
