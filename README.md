# Text Cleaner for Het Verhaal van Nederland

This repository contains Python scripts to clean and format text from various sources related to "Het Verhaal van Nederland" (The Story of the Netherlands) series.

## Scripts

### clean_srt.py
Cleans subtitle (SRT) files from the TV series by:
- Removing timestamps and sequence numbers
- Removing text in all capital letters (typically sound cues)
- Joining lines with the same font color into paragraphs
- Creating new paragraphs when font color changes
- Removing font tags to produce clean text
- Removing common interjections and commands
- Cleaning up sound descriptions and advertisements

### clean_text.py
Cleans markdown text files by:
- Preserving chapter headings (lines that start with numbers)
- Merging text lines to form complete paragraphs
- Keeping empty lines as paragraph separators
- Ensuring proper sentence flow within paragraphs
- Special handling for document titles and introductions

## Usage

### For Subtitle (SRT) Files

1. Download the SRT files from the TV series episodes:
   - Visit [NPO Start - Het Verhaal van Nederland](https://npo.nl/start/serie/het-verhaal-van-nederland)
   - Use [DownloadGemist](https://downloadgemist.nl/) to download the SRT files
2. Clean the SRT file:
   ```bash
   python clean_srt.py input.srt [output.txt]
   ```
   If no output file is specified, it will create one with '_clean.txt' appended.

### For Text Files

1. Download the PDF files from the [NTR Podwalks](https://hetverhaalvannederland.ntr.nl/podwalks/)
2. Convert the PDF to Markdown using [MSFTMD](https://msftmd.replit.app/)
3. Clean the resulting markdown file:
   ```bash
   python clean_text.py input.md [output.md]
   ```
   If no output file is specified, it will create one with '_clean.md' appended.

## Requirements

- Python 3.x
- No additional dependencies required

## License

This project is open source and available under the MIT License. 