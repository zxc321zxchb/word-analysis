"""Test script to recursively parse document from first paragraph number."""
import sys
import os

# Add src to path
sys.path.insert(0, '/Users/life/project/cursor/word-analysis/python-doc-analysis/src')

from doc_analysis.parser.docx import DocxParser

def recursive_parse_sections(sections, index=0):
    """Recursively parse sections starting from first paragraph number.
    
    Args:
        sections: List of parsed sections
        index: Current section index
        
    Returns:
        None
    """
    if index >= len(sections):
        print("\nAll sections parsed successfully!")
        return
    
    section = sections[index]
    print(f"\n=== Parsing Section [{section.number_path}] ===")
    print(f"Title: {section.title}")
    print(f"Level: {section.level}")
    print(f"Parent: {section.parent_path}")
    
    # Parse text content
    if section.paragraphs:
        print("\nText Content:")
        for i, para in enumerate(section.paragraphs):
            print(f"  Paragraph {i+1}: {para}")
    else:
        print("\nText Content: None")
    
    # Parse tables
    if section.tables:
        print("\nTables:")
        for i, table in enumerate(section.tables):
            print(f"  Table {i+1}: {table.rows}x{table.cols}")
            print(f"    HTML: {table.html}")
    else:
        print("\nTables: None")
    
    # Parse images
    if section.images:
        print("\nImages:")
        for i, image in enumerate(section.images):
            print(f"  Image {i+1}: {image.filename}")
            print(f"    MIME Type: {image.mime_type}")
            print(f"    Dimensions: {image.width}x{image.height}")
    else:
        print("\nImages: None")
    
    # Continue to next section
    recursive_parse_sections(sections, index + 1)

def test_recursive_parsing():
    """Test recursive parsing of document starting from first paragraph number."""
    print("Testing recursive parsing of real_test.docx file...")
    
    # Check if real_test.docx exists
    file_path = 'real_test.docx'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Read the file
    with open(file_path, 'rb') as f:
        doc_content = f.read()
    
    print("\nParsing document...")
    parser = DocxParser()
    parsed = parser.parse(doc_content, "real_test.docx")
    
    print(f"\nDocument Info:")
    print(f"  Filename: {parsed.original_filename}")
    print(f"  File Size: {parsed.file_size} bytes")
    print(f"  Sections Found: {len(parsed.sections)}")
    
    if parsed.sections:
        print("\nStarting recursive parsing from first section...")
        # Sort sections by number_path to ensure correct order
        sorted_sections = sorted(parsed.sections, key=lambda s: s.number_path)
        recursive_parse_sections(sorted_sections)
    else:
        print("\nNo sections found in the document!")
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_recursive_parsing()
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
