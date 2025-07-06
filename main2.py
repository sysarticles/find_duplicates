import os
import hashlib
from collections import defaultdict
from dotenv import load_dotenv

def find_files(directory):
    """Recursively find all files in a directory."""
    for root, _, files in os.walk(directory):
        for name in files:
            yield os.path.join(root, name)

def group_by_name(files):
    """Group files by their names, ignoring extensions."""
    groups = defaultdict(list)
    for file_path in files:
        # os.path.splitext splits the path into a pair (root, ext)
        # We take the root part of the filename as the key.
        file_name_without_extension = os.path.splitext(os.path.basename(file_path))[0]
        groups[file_name_without_extension].append(file_path)
    # Return only those names that have more than one file path (i.e., duplicates)
    return {name: paths for name, paths in groups.items() if len(paths) > 1}

def hash_file(path, block_size=65536):
    """Generate SHA256 hash for a file."""
    hasher = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            # Read the file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(block_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except IOError:
        # Return None if the file cannot be read
        print(f"Warning: Could not read file to hash: {path}")
        return None

def find_duplicates_by_content(files):
    """Find duplicate files by comparing their hashes."""
    hashes = defaultdict(list)
    for file_path in files:
        file_hash = hash_file(file_path)
        if file_hash:
            hashes[file_hash].append(file_path)
    # Return only those hashes that have more than one file path (i.e., duplicates)
    return {h: paths for h, paths in hashes.items() if len(paths) > 1}

def generate_rm_commands(duplicates):
    """Generate 'rm' commands for duplicate files, properly escaping single quotes."""
    commands = []
    # The 'duplicates' dictionary is expected to have the original file path as the key
    # and a list of duplicate file paths as the value.
    for _, dup_list in duplicates.items():
        for duplicate in dup_list:
            # To handle filenames with single quotes, we replace each ' with '\''
            # This effectively closes the single-quoted string, adds an escaped single quote,
            # and then re-opens the single-quoted string for the shell.
            escaped_duplicate = duplicate.replace("'", "'\\''")
            commands.append(f"rm '{escaped_duplicate}'")
    return commands

def main():
    """Main function to find and report duplicates."""
    load_dotenv()
    lookup_folder = os.getenv("LOOKUP_FOLDER")

    if not lookup_folder or not os.path.isdir(lookup_folder):
        print("Error: LOOKUP_FOLDER not found or is not a valid directory.")
        print("Please create a .env file with LOOKUP_FOLDER=/path/to/your/folder")
        return

    print(f"Scanning for files in: {lookup_folder}\n")
    all_files = list(find_files(lookup_folder))
    
    # --- Define specific audio extensions to check for name duplicates ---
    audio_extensions = {'.mp3', '.m4a', '.3gp'}
    audio_files = [f for f in all_files if os.path.splitext(f)[1].lower() in audio_extensions]


    # --- Find duplicates by name for AUDIO FILES ONLY ---
    name_duplicates = group_by_name(audio_files)
    if name_duplicates:
        print("--- Audio Duplicates Found by Name (Keeping Smallest File) ---")
        name_rm_commands = []
        for name, paths in name_duplicates.items():
            # Sort paths by file size in ASCENDING order (smallest first)
            try:
                paths.sort(key=os.path.getsize)
            except FileNotFoundError as e:
                print(f"Warning: Could not access a file to check its size: {e}")
                continue

            original = paths[0]
            duplicates = paths[1:]
            
            # Display file sizes for clarity
            original_size = os.path.getsize(original)
            print(f"\nOriginal (Smallest): {original} ({original_size / 1024 / 1024:.2f} MB)")
            
            for dup in duplicates:
                dup_size = os.path.getsize(dup)
                print(f"Duplicate (Larger):  {dup} ({dup_size / 1024 / 1024:.2f} MB)")
            
            if duplicates:
                name_rm_commands.extend(generate_rm_commands({original: duplicates}))

        if name_rm_commands:
            print("\n--- ZSH Commands to Remove Larger Audio Duplicates ---")
            for cmd in name_rm_commands:
                print(cmd)
        print("-" * 50)
    else:
        print("No audio duplicates found by name for specified extensions (.mp3, .m4a, .3gp).\n")


    # --- Find duplicates by content (for ALL file types) ---
    content_duplicates = find_duplicates_by_content(all_files)
    if content_duplicates:
        print("\n--- Duplicates Found by Content (File Hash) ---")
        content_rm_commands = []
        for file_hash, paths in content_duplicates.items():
            # Sort paths alphabetically to have a consistent "original"
            paths.sort()
            original = paths[0]
            duplicates = paths[1:]
            
            print(f"\nHash: {file_hash}")
            print(f"Original: {original}")
            for dup in duplicates:
                print(f"Duplicate: {dup}")
            
            if duplicates:
                content_rm_commands.extend(generate_rm_commands({original: duplicates}))

        if content_rm_commands:
            print("\n--- ZSH Commands to Remove Content Duplicates ---")
            for cmd in content_rm_commands:
                print(cmd)
        print("-" * 50)
    else:
        print("No duplicates found by content.\n")


if __name__ == "__main__":
    main()
