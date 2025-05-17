import csv
from datetime import datetime

def normalize_title(title):
    """Normalize title for comparison by removing common variations"""
    title = title.lower().strip()
    # Remove leading "the " or "a " or "an "
    if title.startswith("the "):
        title = title[4:]
    elif title.startswith("a "):
        title = title[2:]
    elif title.startswith("an "):
        title = title[3:]
    return title

def read_library_titles(library_file='my_library.txt'):
    titles = {}  # Using dict to store both normalized and original titles
    current_main_title = None
    
    try:
        with open(library_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line.startswith('Main Title:'):
                # Store the main title
                current_main_title = line.replace('Main Title:', '').strip()
                norm_title = normalize_title(current_main_title)
                titles[norm_title] = {'original': current_main_title, 'alt_titles': []}
            elif line.startswith('  • ') and current_main_title:
                # Add alternative title to current main title's entry
                alt_title = line.replace('  • ', '').strip()
                norm_main = normalize_title(current_main_title)
                if alt_title != current_main_title and alt_title not in titles[norm_main]['alt_titles']:
                    titles[norm_main]['alt_titles'].append(alt_title)
                # Also add as its own entry for matching
                norm_alt = normalize_title(alt_title)
                if norm_alt not in titles:
                    titles[norm_alt] = {'original': alt_title, 'alt_titles': []}
                
        return titles
    except FileNotFoundError:
        print(f"Error: {library_file} not found")
        return {}
    except Exception as e:
        print(f"Error reading library file: {str(e)}")
        return {}

def read_csv_titles(csv_file='The Mangadex Massacre - Sheet1.csv'):
    titles = {}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            header = next(csv_reader)  # Skip header row
            
            for row in csv_reader:
                if row:  # Check if row is not empty
                    title = row[0].strip()
                    norm_title = normalize_title(title)
                    titles[norm_title] = {'original': title, 'alt_titles': []}
                    # If there's a second column with alternative title, add it
                    if len(row) > 1 and row[1].strip():
                        titles[norm_title]['alt_titles'].append(row[1].strip())
                    
        return titles
    except FileNotFoundError:
        print(f"Error: {csv_file} not found")
        return {}
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return {}

def find_matching_titles(library_titles, csv_titles):
    matches = []
    
    # Create a mapping of normalized titles to their original entries
    norm_to_lib = {}
    for lib_norm, lib_data in library_titles.items():
        # Add the main title mapping
        if lib_norm not in norm_to_lib:
            norm_to_lib[lib_norm] = set()
        norm_to_lib[lib_norm].add(lib_data['original'])
        # Add mappings for all alternative titles
        for alt in lib_data['alt_titles']:
            norm_alt = normalize_title(alt)
            if norm_alt not in norm_to_lib:
                norm_to_lib[norm_alt] = set()
            norm_to_lib[norm_alt].add(lib_data['original'])

    # Check each library title and its alternates against each CSV title and its alternates
    processed_matches = set()  # Keep track of matches we've already processed
    
    for lib_norm, lib_data in library_titles.items():
        # Create a set of all normalized library titles for this entry (main + alternates)
        lib_title_set = {lib_norm}
        lib_title_set.update(normalize_title(alt) for alt in lib_data['alt_titles'])
        
        for csv_norm, csv_data in csv_titles.items():
            # Skip if we've already processed this CSV title
            if csv_data['original'] in processed_matches:
                continue
                
            # Create a set of all normalized CSV titles for this entry (main + alternates)
            csv_title_set = {csv_norm}
            csv_title_set.update(normalize_title(alt) for alt in csv_data['alt_titles'])
            
            # If there's any overlap between the title sets, we have a match
            if lib_title_set & csv_title_set:
                # Collect all library titles that are related to any of the matching titles
                all_lib_titles = set()
                all_lib_alt_titles = set()
                
                # Add titles from the current library entry
                all_lib_titles.add(lib_data['original'])
                all_lib_alt_titles.update(lib_data['alt_titles'])
                
                # Add titles from any other library entries that match
                for norm_title in lib_title_set | csv_title_set:
                    if norm_title in norm_to_lib:
                        for original_title in norm_to_lib[norm_title]:
                            all_lib_titles.add(original_title)
                            # Add alt titles from this related entry
                            related_entry = next((data for _, data in library_titles.items() 
                                               if data['original'] == original_title), None)
                            if related_entry:
                                all_lib_alt_titles.update(related_entry['alt_titles'])
                
                match_info = {
                    'library_title': lib_data['original'],
                    'library_alt_titles': sorted(all_lib_alt_titles - all_lib_titles),  # Remove main titles from alt titles
                    'csv_title': csv_data['original'],
                    'csv_alt_titles': csv_data['alt_titles']
                }
                matches.append(match_info)
                processed_matches.add(csv_data['original'])
                break
    
    return matches

def format_matching_titles(matching_titles):
    lines = []
    lines.append(f"Matching Titles Found: {len(matching_titles)}")
    lines.append("=" * 80)
    
    for i, match in enumerate(sorted(matching_titles, key=lambda x: x['library_title'].lower()), 1):
        lines.append(f"\nManga #{i}:")
        lines.append("-" * 40)
        
        # Library Titles Section
        lines.append("From Your Library:")
        lines.append(f"  Main: {match['library_title']}")
        
        # Get all titles from my_library.txt for this manga
        try:
            with open('my_library.txt', 'r', encoding='utf-8') as f:
                library_content = f.read()
            
            # Find the section for this manga
            sections = library_content.split("Manga #")
            for section in sections:
                if match['library_title'] in section:
                    # Extract all titles from this section
                    section_lines = section.split('\n')
                    alt_titles = []
                    collecting_alts = False
                    for line in section_lines:
                        if line.strip() == "Alternative Titles:":
                            collecting_alts = True
                        elif collecting_alts and line.strip().startswith("•"):
                            alt_title = line.strip().replace("•", "").strip()
                            if alt_title not in alt_titles:
                                alt_titles.append(alt_title)
                        elif collecting_alts and (line.strip() == "" or line.strip().startswith("=")):
                            collecting_alts = False
                    
                    if alt_titles:
                        lines.append("  Alternative Titles:")
                        for alt in sorted(alt_titles):
                            lines.append(f"    • {alt}")
                    break
        except Exception as e:
            # If there's any error reading the file, fall back to the alt_titles we have
            if match['library_alt_titles']:
                lines.append("  Alternative Titles:")
                for alt in sorted(match['library_alt_titles']):
                    lines.append(f"    • {alt}")
        
        # CSV Titles Section
        lines.append("\nFrom MangaDex Massacre List:")
        lines.append(f"  Main: {match['csv_title']}")
        if match['csv_alt_titles']:
            lines.append("  Alternative Titles:")
            for alt in sorted(match['csv_alt_titles']):
                lines.append(f"    • {alt}")
        
        lines.append("-" * 40)
    
    return "\n".join(lines)

def save_matches(matching_titles, output_file='matching_titles.txt'):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Comparison performed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(format_matching_titles(matching_titles))
        return True
    except Exception as e:
        print(f"Error saving matches to file: {str(e)}")
        return False

def main():
    # Read titles from both files
    library_titles = read_library_titles()
    csv_titles = read_csv_titles()
    
    if not library_titles or not csv_titles:
        print("Error: Could not proceed with comparison due to missing data")
        return
    
    # Find matching titles
    matching_titles = find_matching_titles(library_titles, csv_titles)
    
    if matching_titles:
        # Display matches
        print("\nFound matching titles:")
        print(format_matching_titles(matching_titles))
        
        # Save to file
        if save_matches(matching_titles):
            print(f"\nSuccessfully saved {len(matching_titles)} matching titles to matching_titles.txt")
        else:
            print("\nFailed to save matching titles to file")
    else:
        print("\nNo matching titles found")

if __name__ == "__main__":
    main() 