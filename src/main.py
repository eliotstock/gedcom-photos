#!/usr/bin/env python3
"""
Main entry point for the application.
"""
import argparse
import sys
import os
import re
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Python command line application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "ged_file",
        type=str,
        help="Path to the GEDCOM file",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    return parser.parse_args()


def validate_file(file_path):
    """Validate that the file exists and is readable."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"Error: File '{file_path}' is not readable.")
        return False
    return True


def create_person_id(name, birth_date):
    """Create a unique ID for a person from their name and birth date."""
    # Extract the name parts
    name_match = re.match(r'1 NAME (.*?) /(.*?)/', name)
    if not name_match:
        return None
    
    given_name = name_match.group(1).strip()
    surname = name_match.group(2).strip()
    
    # Parse the birth date
    date_match = re.match(r'2 DATE (\d+) (\w+) (\d+)', birth_date)
    if not date_match:
        return None
    
    day = int(date_match.group(1))  # Convert to integer
    month = date_match.group(2)
    year = date_match.group(3)
    
    # Convert month name to number
    try:
        month_num = datetime.strptime(month, '%b').month
    except ValueError:
        return None
    
    # Create the date part in YYYY-MM-DD format
    date_part = f"{year}-{month_num:02d}-{day:02d}"
    
    # Create the name part with underscores
    # Split the given name into parts and join with underscores
    name_parts = [part.strip() for part in given_name.split()]
    name_parts.append(surname)
    name_part = "_".join(name_parts).lower()
    
    # Remove any non-alphanumeric characters except underscores
    name_part = re.sub(r'[^a-z0-9_]', '', name_part)
    
    return f"{date_part}_{name_part}"


def download_photo(url, filename):
    """Download a photo from the given URL and save it to the specified filename."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False


def process_gedcom_file(file_path):
    """Process the GEDCOM file and download photos."""
    # Create photos directory if it doesn't exist
    photos_dir = Path("./photos")
    photos_dir.mkdir(exist_ok=True)
    
    current_person = None
    current_name = None
    current_birth_date = None
    photo_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Check for new person record
            if line.startswith('0 @I') and ' INDI' in line:
                current_person = line
                current_name = None
                current_birth_date = None
                photo_count = 0
                continue
            
            # Get name
            if line.startswith('1 NAME '):
                current_name = line
                continue
            
            # Get birth date
            if line.startswith('2 DATE '):
                current_birth_date = line
                continue
            
            # Process photo URL
            if line.startswith('2 FILE '):
                if current_name and current_birth_date:
                    person_id = create_person_id(current_name, current_birth_date)
                    if person_id:
                        url = line[7:]  # Remove '2 FILE ' prefix
                        photo_count += 1
                        filename = photos_dir / f"{person_id}_{photo_count:02d}.jpg"
                        print(f"Downloading {url} to {filename}")
                        download_photo(url, filename)


def main():
    """Main entry point."""
    args = parse_args()
    if not validate_file(args.ged_file):
        return 1
    
    process_gedcom_file(args.ged_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
