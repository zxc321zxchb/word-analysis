"""Test script to parse existing test.docx file."""
import sys
import os

# Add src to path
sys.path.insert(0, '/Users/life/project/cursor/word-analysis/python-doc-analysis/src')

from doc_analysis.parser.docx import DocxParser

def test_existing_document():
    """Test parsing existing test.docx file."""
    print("Testing existing test.docx file...")
    
    # Check if test.docx exists
    if not os.path.exists('test.docx'):
        print("Error: test.docx not found!")
        return False
    
    # Read the file
    with open('test.docx', 'rb') as f:
        doc_content = f.read()
    
    print("\nParsing document...")
    parser = DocxParser()
    parsed = parser.parse(doc_content, "test.docx")
    
    print(f"\nDocument Info:")
    print(f"  Filename: {parsed.original_filename}")
    print(f"  File Size: {parsed.file_size} bytes")
    print(f"  File Hash: {parsed.file_hash}")
    print(f"  Sections Found: {len(parsed.sections)}")
    
    print(f"\nSections:")
    for section in parsed.sections:
        print(f"  [{section.number_path}] Level {section.level}: {section.title}")
        print(f"    - Parent: {section.parent_path}")
        print(f"    - Paragraphs: {len(section.paragraphs)}")
        print(f"    - Tables: {len(section.tables)}")
        for i, p in enumerate(section.paragraphs):
            print(f"      > Paragraph {i+1}: {p[:100]}...")
        for i, table in enumerate(section.tables):
            print(f"      > Table {i+1}: {table.rows}x{table.cols}")
            print(f"        HTML: {table.html[:100]}...")
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_existing_document()
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
