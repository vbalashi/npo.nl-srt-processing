#!/usr/bin/env python3
import re
import os
import sys

def clean_srt(input_file, output_file=None):
    """
    Process an SRT file and convert it to readable text with proper paragraphs:
    - Remove timestamps and SRT sequence numbers
    - Remove text in all capital letters (typically sound cues)
    - Join lines with the same font color into paragraphs
    - Create new paragraphs when font color changes
    - Remove font tags to produce clean text
    """
    if output_file is None:
        # If no output file is specified, create one with '_clean' appended
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_clean.txt"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try another common encoding if UTF-8 fails
        with open(input_file, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # First, normalize line endings
    content = content.replace('\r\n', '\n')
    
    # Pre-process to fix split font tags within lines 
    # Replace </font><font color="xxx"> with a space
    content = re.sub(r'</font><font color="([^"]+)">', ' ', content)
    
    # Split into subtitle entries
    # An entry consists of: number, timestamp, subtitle text, and blank line
    entries = re.split(r'\n\s*\n+', content)
    
    # Pre-process to handle sound cues - replace entire sound cue entries with empty strings
    processed_entries = []
    for entry in entries:
        lines = entry.strip().split('\n')
        
        # Skip if entry is not properly formatted (should have at least 3 lines)
        if len(lines) < 3:
            processed_entries.append(entry)
            continue
            
        # Check if this entry contains only sound cues
        subtitle_text = ' '.join(lines[2:])
        if re.match(r'^<font color="[^"]+">(\([^)]+\))</font>$', subtitle_text):
            # Skip this entry entirely
            continue
            
        processed_entries.append(entry)
            
    # First pass: extract all text chunks with their colors
    text_chunks = []
    
    for entry in processed_entries:
        lines = entry.strip().split('\n')
        
        # Skip if entry is not properly formatted (should have at least 3 lines)
        if len(lines) < 3:
            continue
        
        # Extract the text lines (skipping sequence number and timestamp)
        subtitle_text = ' '.join(lines[2:])
        
        # Find all font tags with their colors and text
        font_pattern = r'<font color="([^"]+)">([^<]+)</font>'
        
        for match in re.finditer(font_pattern, subtitle_text):
            color = match.group(1)
            text = match.group(2)
            
            # Skip all-caps lines (sound effects/cues)
            if re.match(r'^[^a-z]*$', text) or text.startswith('('):
                continue
                
            # Skip common interjections
            if re.match(r'^(Ja,?\s+(op|los)|En\s+(op|los)|Los|Op|Ok(é|e),?\s+op)[!.]?\s*$', text, re.IGNORECASE):
                continue
                
            # Skip "De sliet" and similar standalone phrases
            if re.match(r'^(De\s+sliet)[!.]\s*$', text, re.IGNORECASE):
                continue
            
            # Record color and text if not filtered out
            text_chunks.append((color, text))
    
    # Second pass: create paragraphs based on color changes
    paragraphs = []
    current_paragraph = []
    current_color = None
    
    for color, text in text_chunks:
        # If color changes, start a new paragraph
        if color != current_color and current_paragraph:
            # Join the current paragraph and add to list
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
        
        # Add text to current paragraph
        current_paragraph.append(text)
        current_color = color
    
    # Don't forget the last paragraph
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    # Third pass: merge incomplete sentences across paragraphs
    merged_paragraphs = []
    skip_next = False
    
    for i in range(len(paragraphs)):
        if skip_next:
            skip_next = False
            continue
            
        current = paragraphs[i]
        
        # Check if this paragraph ends with an incomplete sentence
        ends_incomplete = (
            not re.search(r'[.!?]\s*$', current.rstrip()) or 
            current.rstrip().endswith('...') or
            re.search(r'[a-z]$', current) 
        )
        
        # Check if there's a next paragraph that might be a continuation
        if ends_incomplete and i + 1 < len(paragraphs):
            next_para = paragraphs[i + 1]
            # Check if next paragraph starts with lowercase (continuing the sentence)
            starts_lowercase = (
                re.match(r'^[a-z]', next_para.lstrip()) or
                next_para.strip().startswith('...')
            )
            
            if starts_lowercase:
                # Merge the paragraphs
                merged_paragraphs.append(f"{current} {next_para}")
                skip_next = True
            else:
                merged_paragraphs.append(current)
        else:
            merged_paragraphs.append(current)
    
    # Fourth pass: process the paragraphs to improve readability
    processed_paragraphs = []
    for paragraph in merged_paragraphs:
        # Skip empty or very short paragraphs
        if len(paragraph.strip()) < 3:
            continue
            
        # Remove ellipses that are often used to indicate line breaks in subtitles
        paragraph = re.sub(r'\.\.\.\s+', ' ', paragraph)
        
        # Fix spacing around ellipses
        paragraph = re.sub(r'\s*\.\.\.\s*', '... ', paragraph)
        
        # Remove extra spaces
        paragraph = re.sub(r'\s+', ' ', paragraph).strip()
        
        # Fix sentence joining by adding a space after periods
        paragraph = re.sub(r'\.(?=[A-Z])', '. ', paragraph)
        
        # Fix space after commas
        paragraph = re.sub(r',(?=\S)', ', ', paragraph)
        
        # Fix space after question marks and exclamation points
        paragraph = re.sub(r'([?!])(?=[A-Z])', r'\1 ', paragraph)
        
        # Fix specific cases like "jaar.." to "jaar..."
        paragraph = re.sub(r'\.\.(?=[^.])', '...', paragraph)
        
        # Remove common interjections and commands in subtitles
        paragraph = re.sub(r'\b(Ja|Nee|En|Los|Op), (op|los|ja|nee)!', '', paragraph, flags=re.IGNORECASE)
        paragraph = re.sub(r'\b(De sliet)\b', '', paragraph)
        paragraph = re.sub(r'\b(En los|En op|Los|Op|Ja op|Oké op)\! ', ' ', paragraph)
        paragraph = re.sub(r'^\s*\b(Drei Koggen)\.\s*$', '', paragraph)
        
        if paragraph.strip():
            processed_paragraphs.append(paragraph)
    
    # Join paragraphs with double newlines
    final_content = '\n\n'.join(processed_paragraphs)
    
    # Process the entire text for common issues
    
    # Remove common closing text like "information: service.npo.nl"
    final_content = re.sub(r'\n\ninformatie: [^\n]+$', '', final_content)
    
    # Remove advertisements for podwalk app (improved regex)
    final_content = re.sub(r'(Volgende keer in|Download nu|Via de app|Kijk, daar|Johnny en Tante Leen).*?(verhaal van|podwalk|ga er ?op ?uit).*?(\.\s*$|\n)', '.', final_content, flags=re.DOTALL|re.MULTILINE)
    
    # Fix inconsistent spacing
    final_content = re.sub(r' {2,}', ' ', final_content)
    
    # Cleanup sound descriptions in parentheses
    final_content = re.sub(r'\([^)]*?(?:rumoer|blaft|gejuich|gezang|podcast|geluid)[^)]*?\)', '', final_content)
    
    # Remove trailing dots
    final_content = re.sub(r'\.\s*\.\s*$', '.', final_content)
    
    # Write the cleaned content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Cleaned text saved to {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_srt.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    clean_srt(input_file, output_file) 