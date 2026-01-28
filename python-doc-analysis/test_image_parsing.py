"""Update parser to handle images in paragraphs."""
import sys
import os

# Add src to path
sys.path.insert(0, '/Users/life/project/cursor/word-analysis/python-doc-analysis/src')

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from doc_analysis.parser.docx import DocxParser

def test_image_parsing():
    """Test image parsing in document."""
    print("Testing image parsing...")
    
    doc_path = '/Users/life/Documents/网凝/副本厦门市轨道交通4号线（后溪至翔安机场段）工程车辆采购项目用户需求书（最终版ok）.docx'
    
    with open(doc_path, 'rb') as f:
        doc_content = f.read()
    
    parser = DocxParser()
    parsed = parser.parse_by_heading(doc_content, 'test_with_images.docx')
    
    print(f"\nTotal sections: {len(parsed.sections)}")
    
    # Check sections with images
    print("\nSections with images:")
    for section in parsed.sections:
        if section.images:
            print(f"  [{section.number_path}] {section.title[:50]}...")
            print(f"    Images: {len(section.images)}")
            for img in section.images:
                print(f"      - {img.filename} ({img.mime_type})")

if __name__ == "__main__":
    test_image_parsing()
