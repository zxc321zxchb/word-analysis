"""Test script to parse document by h1, h2, h3, h4, h5 headings."""
import sys
import os

# Add src to path
sys.path.insert(0, '/Users/life/project/cursor/word-analysis/python-doc-analysis/src')

from doc_analysis.parser.docx import DocxParser

def hierarchical_sort_key(section):
    """Generate sort key for hierarchical ordering of sections."""
    parts = section.number_path.split('.')
    try:
        return tuple(map(int, parts))
    except ValueError:
        return tuple(parts)

def extract_heading_level(number_path):
    """Extract heading level from number_path like '1', '1.1', '1.1.1'."""
    return number_path.count('.')

def get_heading_label(level):
    """Get heading label like 'h1', 'h2', etc."""
    return f"h{level + 1}"

def iterative_parse_sections(sections):
    """Iteratively parse sections in hierarchical order with h1-h5 labels."""
    current_context = {}  # Store current context for each level
    
    for index, section in enumerate(sections):
        level = extract_heading_level(section.number_path)
        heading_label = get_heading_label(level)
        
        print(f"\n=== Parsing [{heading_label}] [{section.number_path}] ===")
        print(f"Title: {section.title}")
        
        # Show parent context
        if level > 0:
            parent_level = level - 1
            parent_heading = get_heading_label(parent_level)
            if parent_heading in current_context:
                print(f"Parent [{parent_heading}]: {current_context[parent_heading]}")
        
        # Update current context
        current_context[heading_label] = section.title
        # Clear deeper levels
        for l in range(level + 1, 5):
            deeper_label = get_heading_label(l)
            if deeper_label in current_context:
                del current_context[deeper_label]
        
        # Parse text content
        if section.paragraphs:
            print("Text Content:")
            for i, para in enumerate(section.paragraphs):
                print(f"  Paragraph {i+1}: {para}")
        else:
            print("Text Content: None")
        
        # Parse tables
        if section.tables:
            print("Tables:")
            for i, table in enumerate(section.tables):
                print(f"  Table {i+1}: {table.rows}x{table.cols}")
                print(f"    HTML: {table.html}")
        else:
            print("Tables: None")
        
        # Parse images
        if section.images:
            print("Images:")
            for i, image in enumerate(section.images):
                print(f"  Image {i+1}: {image.filename}")
                print(f"    MIME Type: {image.mime_type}")
                print(f"    Dimensions: {image.width}x{image.height}")
        else:
            print("Images: None")
    
    print("\nAll sections parsed successfully!")

def test_hierarchical_parsing():
    """Test parsing document in hierarchical order with h1-h5 labels."""
    print("Testing hierarchical parsing (h1, h2, h3, h4, h5) of real_test.docx file...")
    print("Non-heading content will be grouped under the most recent heading.")
    
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
        print("\nStarting hierarchical parsing (h1→h2→h3→h4→h5)...")
        sorted_sections = sorted(parsed.sections, key=hierarchical_sort_key)
        iterative_parse_sections(sorted_sections[:20])
    else:
        print("\nNo sections found in the document!")
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_hierarchical_parsing()
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
