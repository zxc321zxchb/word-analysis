"""Test script to parse document and return JSON format."""
import sys
import os
import json

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

def parse_to_json(sections, max_sections=50):
    """Parse sections to JSON format with hierarchical structure."""
    result = {
        "document_info": {
            "total_sections": len(sections)
        },
        "sections": []
    }
    
    current_context = {}
    
    for index, section in enumerate(sections):
        if index >= max_sections:
            break
            
        level = extract_heading_level(section.number_path)
        heading_label = get_heading_label(level)
        
        section_data = {
            "heading": heading_label,
            "number_path": section.number_path,
            "level": section.level,
            "title": section.title,
            "parent": None
        }
        
        if level > 0:
            parent_level = level - 1
            parent_heading = get_heading_label(parent_level)
            if parent_heading in current_context:
                section_data["parent"] = {
                    "heading": parent_heading,
                    "number_path": current_context[parent_heading]["number_path"],
                    "title": current_context[parent_heading]["title"]
                }
        
        current_context[heading_label] = {
            "number_path": section.number_path,
            "title": section.title
        }
        
        for l in range(level + 1, 5):
            deeper_label = get_heading_label(l)
            if deeper_label in current_context:
                del current_context[deeper_label]
        
        if section.paragraphs:
            section_data["content"] = {
                "text": section.paragraphs,
                "tables": [],
                "images": []
            }
        else:
            section_data["content"] = {
                "text": [],
                "tables": [],
                "images": []
            }
        
        if section.tables:
            section_data["content"]["tables"] = [
                {
                    "rows": table.rows,
                    "cols": table.cols,
                    "html": table.html
                }
                for table in section.tables
            ]
        
        if section.images:
            section_data["content"]["images"] = [
                {
                    "filename": image.filename,
                    "mime_type": image.mime_type,
                    "width": image.width,
                    "height": image.height
                }
                for image in section.images
            ]
        
        result["sections"].append(section_data)
    
    return result

def test_json_output():
    """Test parsing document and output JSON format."""
    print("Testing JSON output for real_test.docx file...")
    
    file_path = 'real_test.docx'
    if not os.path.exists(file_path):
        error_result = {
            "error": f"File not found: {file_path}"
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        return False
    
    with open(file_path, 'rb') as f:
        doc_content = f.read()
    
    print("Parsing document...")
    parser = DocxParser()
    parsed = parser.parse(doc_content, "real_test.docx")
    
    print(f"Found {len(parsed.sections)} sections")
    
    sorted_sections = sorted(parsed.sections, key=hierarchical_sort_key)
    json_result = parse_to_json(sorted_sections, max_sections=20)
    
    json_result["document_info"]["filename"] = parsed.original_filename
    json_result["document_info"]["file_size"] = parsed.file_size
    json_result["document_info"]["file_hash"] = parsed.file_hash
    
    print("\n" + "="*60)
    print("JSON Output:")
    print("="*60)
    print(json.dumps(json_result, ensure_ascii=False, indent=2))
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    try:
        test_json_output()
    except Exception as e:
        error_result = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)
