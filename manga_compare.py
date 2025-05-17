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
    current_titles = []
    
    try:
        with open(library_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line.startswith('Main Title:'):
                title = line.replace('Main Title:', '').strip()
                norm_title = normalize_title(title)
                titles[norm_title] = {'original': title, 'alt_titles': []}
            elif line.startswith('  • '):
                title = line.replace('  • ', '').strip()
                norm_title = normalize_title(title)
                # Add as alternative title if we have a current main title
                if titles:
                    last_main = list(titles.keys())[-1]
                    titles[last_main]['alt_titles'].append(title)
                # Also add as its own entry in case it matches
                titles[norm_title] = {'original': title, 'alt_titles': []}
                
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
    
    # Check each normalized library title against normalized CSV titles
    for lib_norm, lib_data in library_titles.items():
        if lib_norm in csv_titles:
            # Found a match
            match_info = {
                'library_title': lib_data['original'],
                'csv_title': csv_titles[lib_norm]['original'],
                'library_alt_titles': lib_data['alt_titles'],
                'csv_alt_titles': csv_titles[lib_norm]['alt_titles']
            }
            matches.append(match_info)
            continue
        
        # Check alternative titles
        for csv_norm, csv_data in csv_titles.items():
            if lib_norm in [normalize_title(alt) for alt in csv_data['alt_titles']]:
                match_info = {
                    'library_title': lib_data['original'],
                    'csv_title': csv_data['original'],
                    'library_alt_titles': lib_data['alt_titles'],
                    'csv_alt_titles': csv_data['alt_titles']
                }
                matches.append(match_info)
                break
    
    return matches

def format_matching_titles(matching_titles):
    lines = []
    lines.append(f"Matching Titles Found: {len(matching_titles)}")
    lines.append("=" * 80)
    
    for i, match in enumerate(sorted(matching_titles, key=lambda x: x['library_title'].lower()), 1):
        lines.append(f"\nManga #{i}:")
        lines.append("-" * 40)
        lines.append(f"Library Title: {match['library_title']}")
        if match['library_title'] != match['csv_title']:
            lines.append(f"CSV Title: {match['csv_title']}")
        
        # Add alternative titles if they exist
        if match['library_alt_titles']:
            lines.append("\nLibrary Alternative Titles:")
            for alt in match['library_alt_titles']:
                lines.append(f"  • {alt}")
        
        if match['csv_alt_titles']:
            lines.append("\nCSV Alternative Titles:")
            for alt in match['csv_alt_titles']:
                lines.append(f"  • {alt}")
        
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