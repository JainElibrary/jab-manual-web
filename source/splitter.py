import os
import re

def clean_name(text):
    """lowercase, replace ä, roman to int, swap spaces for hyphens, and remove double hyphens."""
    roman_map = {
        r'\bix\b': '9', r'\bviii\b': '8', r'\bvii\b': '7', r'\bvi\b': '6',
        r'\bv\b': '5', r'\biv\b': '4', r'\biii\b': '3', r'\bii\b': '2', r'\bi\b': '1',
        r'\bx\b': '10'
    }
    text = text.lower()
    for roman, decimal in roman_map.items():
        text = re.sub(roman, decimal, text)

    text = text.replace('ä', 'a').replace('Ä', 'a')
    text = re.sub(r'[^\w\s-]', '', text).strip()
    text = text.replace(' ', '-')
    text = re.sub(r'-+', '-', text)
    return text

def get_short_name(suggested_name, type_label):
    if len(suggested_name) > 20:
        print(f"\n⚠️  {type_label} too long ({len(suggested_name)} chars): '{suggested_name}'")
        user_input = input(f"   Please provide a name under 20 chars (or Enter to truncate): ").strip()
        if user_input:
            return clean_name(user_input)
        else:
            return suggested_name[:20].rstrip('-')
    return suggested_name

def split_to_folders(input_file):
    base_output = "manual_output"
    toc_data = [] # List to store our TOC structure
    
    if not os.path.exists(base_output): os.makedirs(base_output)

    current_folder_path = base_output
    current_file = None
    h1_count, h2_count = 0, 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            h1_match = re.match(r'^#\s+(.*)', line)
            h2_match = re.match(r'^##\s+(.*)', line)

            if h1_match:
                if current_file: current_file.close()
                h1_count += 1
                h2_count = 0 
                
                original_h1 = h1_match.group(1).strip()
                suggested = clean_name(original_h1)
                
                print(f"\n--- Heading 1: '{original_h1}' ---")
                user_choice = input(f"Press Enter to use '{suggested}' or type new: ").strip()
                folder_slug = get_short_name(clean_name(user_choice) if user_choice else suggested, "Folder Name")
                
                folder_display_name = f"{h1_count:02d}-{folder_slug}"
                current_folder_path = os.path.join(base_output, folder_display_name)
                
                # Add Folder to TOC
                toc_data.append(f"\n📁 {folder_display_name}")
                
                if not os.path.exists(current_folder_path): os.makedirs(current_folder_path)
                current_file = open(os.path.join(current_folder_path, "00-intro.md"), 'w', encoding='utf-8')
                current_file.write(line)
                toc_data.append(f"   └── 00-intro.md")

            elif h2_match:
                if current_file: current_file.close()
                h2_count += 1
                
                original_h2 = h2_match.group(1).strip()
                file_slug = get_short_name(clean_name(original_h2), "File Name")
                
                file_display_name = f"{h2_count:02d}-{file_slug}.md"
                file_path = os.path.join(current_folder_path, file_display_name)
                
                # Add File to TOC
                toc_data.append(f"   └── {file_display_name}")
                
                print(f"  > Creating: {file_path}")
                current_file = open(file_path, 'w', encoding='utf-8')
                current_file.write(line)

            else:
                if current_file: current_file.write(line)

    if current_file: current_file.close()

    # --- Generate the TOC.txt - Table of Contents file ---
    with open("toc.txt", "w", encoding="utf-8") as summary_file:
        summary_file.write("TABLE OF CONTENTS\n")
        summary_file.write("=================\n")
        summary_file.write("\n".join(toc_data))

    print(f"\n✅ All done! 'toc.txt' has been created in the main directory.")

# Ensure this matches your actual filename
# Run it
split_to_folders('00_JAB_Manual-2024.md')