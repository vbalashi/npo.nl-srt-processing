#!/usr/bin/env python3
import re
import os
import sys

def clean_text(input_file, output_file=None):
    """
    Clean up line breaks in a markdown file.
    - Preserves chapter headings (lines that start with numbers)
    - Merges text lines to form complete paragraphs
    - Keeps empty lines as paragraph separators
    - Ensures proper sentence flow within paragraphs
    """
    if output_file is None:
        # If no output file is specified, create one with '_clean' appended
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_clean{ext}"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # First, normalize line endings
    content = content.replace('\r\n', '\n')
    
    # Split the content to separately process the header/intro and the chapters
    match = re.search(r'^(1\s+\S[^\n]*)', content, re.MULTILINE)
    if match:
        first_chapter_pos = match.start()
        intro = content[:first_chapter_pos].strip()
        rest = content[first_chapter_pos:]
    else:
        intro = content
        rest = ""
    
    clean_content = []
    
    # Special handling for the document title and introduction
    intro_lines = intro.split('\n')
    
    # Process the title parts (first few lines that are typically titles)
    title_parts = []
    i = 0
    
    # Process the title and subtitle (usually the first 3-4 lines)
    while i < min(4, len(intro_lines)) and (not intro_lines[i].strip() or not re.search(r'[.!?]', intro_lines[i])):
        if intro_lines[i].strip():
            title_parts.append(intro_lines[i].strip())
        else:
            # If we hit an empty line, add the title we've accumulated so far
            if title_parts:
                clean_content.append(' '.join(title_parts))
                title_parts = []
            clean_content.append('')  # Keep the empty line
        i += 1
    
    # Add any remaining title parts
    if title_parts:
        clean_content.append(' '.join(title_parts))
    
    # Now find the main introduction paragraph (the large text block)
    main_intro_text = ' '.join(line.strip() for line in intro_lines[i:] if line.strip())
    if main_intro_text:
        clean_content.append(main_intro_text)
    
    # Process the chapters
    if rest:
        # Split by chapter headings (numbered headings)
        chapter_blocks = re.split(r'^(\d+\s+[\w\s]+)$', rest, flags=re.MULTILINE)
        
        # Skip the first empty element if it exists
        if not chapter_blocks[0].strip():
            chapter_blocks = chapter_blocks[1:]
        
        # Process each chapter and its content
        for i in range(0, len(chapter_blocks), 2):
            if i < len(chapter_blocks):
                # Add the chapter heading
                clean_content.append(chapter_blocks[i].strip())
                
                # Process chapter content if it exists
                if i+1 < len(chapter_blocks):
                    chapter_content = chapter_blocks[i+1]
                    if chapter_content.strip():
                        # Split into paragraphs by empty lines
                        paragraphs = re.split(r'\n\s*\n+', chapter_content)
                        for para in paragraphs:
                            if para.strip():
                                # Join all lines in the paragraph
                                clean_para = ' '.join(line.strip() for line in para.split('\n') if line.strip())
                                if clean_para:
                                    clean_content.append(clean_para)
    
    # Join everything with double newlines
    final_content = '\n\n'.join(clean_content)
    
    # Write the cleaned content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Cleaned text saved to {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_text.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    clean_text(input_file, output_file) 