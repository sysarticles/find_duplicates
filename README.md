# find_duplicates
it will find and show delete commands if files duplicates as name or duplicates as content


Here's how to use the script:

Save the code: Save the code above into a file named find_duplicates.py.

Install dependencies: You'll need the python-dotenv library to read the folder path from a .env file. Install it using pip:

Bash

pip install python-dotenv
Create a .env file: In the same directory where you saved find_duplicates.py, create a file named .env.

Edit the .env file: Add the path to the folder you want to scan into the .env file like this:

LOOKUP_FOLDER="/path/to/your/music_or_media_folder"
Replace /path/to/your/music_or_media_folder with the actual path to your directory.

Run the script: Open your terminal, navigate to the directory where you saved the files, and run the script:

Bash

python find_duplicates.py
The script will then scan the directory and print a list of original files and their duplicates, followed by the rm commands you can use to delete the duplicate files. You can then carefully review the output and copy-paste the commands into your terminal to remove the files.