import json
from datetime import datetime
import os
import shutil

def ensure_archive_dir():
    """Create archives directory if it doesn't exist"""
    archive_dir = 'archives'
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    return archive_dir

def archive_processed_files(processed_file):
    """Move processed JSON files to archives folder"""
    archive_dir = ensure_archive_dir()
    
    # Get the base filename without path
    base_name = os.path.basename(processed_file)
    
    # Create archive filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_name = f"processed_{timestamp}_{base_name}"
    archive_path = os.path.join(archive_dir, archive_name)
    
    try:
        # Move the processed file
        shutil.move(processed_file, archive_path)
        print(f"\nMoved {processed_file} to archives/{archive_name}")
        
        # Also move any related files (like mangas copy*.json)
        base_without_ext = os.path.splitext(base_name)[0]
        for file in os.listdir('.'):
            if file.endswith('.json') and 'copy' in file.lower():
                related_archive_name = f"processed_{timestamp}_{file}"
                related_archive_path = os.path.join(archive_dir, related_archive_name)
                shutil.move(file, related_archive_path)
                print(f"Moved {file} to archives/{related_archive_name}")
        
        # Create a new empty mangas.json file
        open('mangas.json', 'w').close()
        print(f"\nCreated new empty mangas.json file")
                
    except Exception as e:
        print(f"Error archiving files: {str(e)}")

def extract_manga_titles(manga_data):
    manga_entry = {
        'main_en': None,
        'alt_titles': []  # Combined list for all alternative titles
    }
    
    # Extract main title if it exists
    if "attributes" in manga_data:
        attributes = manga_data["attributes"]
        
        # Get main title
        if "title" in attributes:
            title_obj = attributes["title"]
            # Try to get English title first
            if "en" in title_obj:
                manga_entry['main_en'] = title_obj["en"]
            # If no English title, use any other language as main title
            else:
                for lang, title in title_obj.items():
                    manga_entry['main_en'] = title
                    break
        
        # Get all alternative titles from all languages
        if "altTitles" in attributes:
            for alt_title in attributes["altTitles"]:
                for lang, title in alt_title.items():
                    if title not in manga_entry['alt_titles']:  # Avoid duplicates
                        manga_entry['alt_titles'].append(title)
    
    # Return entry if it has at least one title
    if manga_entry['main_en'] or manga_entry['alt_titles']:
        return manga_entry
    return None

def parse_manga_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                json_data = json.load(file)
                
                # Handle the nested structure
                if "data" in json_data and isinstance(json_data["data"], list):
                    manga_entries = []
                    for manga in json_data["data"]:
                        manga_entry = extract_manga_titles(manga)
                        if manga_entry:
                            manga_entries.append(manga_entry)
                    return manga_entries
                else:
                    print("Error: Unexpected JSON structure. Expected 'data' array.")
                    return []
                    
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON format in the file: {str(e)}")
                return []
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []

def format_manga_entry(entry):
    lines = []
    
    # Add main title
    if entry['main_en']:
        lines.append(f"Main Title: {entry['main_en']}")
    
    # Add all alternative titles
    if entry['alt_titles']:
        lines.append("Alternative Titles:")
        # Filter out the main title from alternatives to avoid duplication
        alt_titles = [title for title in entry['alt_titles'] if title != entry['main_en']]
        for title in alt_titles:
            lines.append(f"  • {title}")
    
    return "\n".join(lines)

def save_to_library(manga_entries, library_file='my_library.txt'):
    try:
        # Open file in append mode
        with open(library_file, 'a', encoding='utf-8') as f:
            # Write timestamp for this batch
            f.write(f"\n\nBatch added on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
            
            # Write each manga entry
            for i, entry in enumerate(manga_entries, 1):
                f.write(f"\nManga #{i}:\n")
                f.write("-" * 40 + "\n")
                f.write(format_manga_entry(entry) + "\n")
            
            f.write("=" * 80 + "\n")
        return True
    except Exception as e:
        print(f"Error saving to library file: {str(e)}")
        return False

def main():
    file_path = 'mangas.json'  # Direct file path instead of input
    manga_entries = parse_manga_file(file_path)
    
    if manga_entries:
        print("\nManga titles found:")
        print("=" * 80)
        for i, entry in enumerate(manga_entries, 1):
            print(f"\nManga #{i}:")
            print("-" * 40)
            print(format_manga_entry(entry))
        print("\n" + "=" * 80)
        
        # Save to library file
        if save_to_library(manga_entries):
            print(f"\nSuccessfully appended {len(manga_entries)} manga entries to my_library.txt")
            # Archive the processed files
            archive_processed_files(file_path)
        else:
            print("\nFailed to save to library file")
    else:
        print("No titles found in the file.")

if __name__ == "__main__":
    main() 