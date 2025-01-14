# dayone-to-obsidian
Convert a [Day One](https://dayoneapp.com/) JSON export into individual entries for [Obsidian](https://obsidian.md). Each entry is created as a separate page. 

> *This repository is no longer being monitored. The code remains available for the use of others, but no support will be given.*

## Requirements
* Python 3.x
* pytz (pip install pytz) for timezone functions
* Possible Visual Studio Code as your IDE. People have reported issues using another IDE. I don't know the specifics but think its most likely the need to match properly the version of Python and libraries you are using when running code within the IDE itself.

## Day One version
This script works with export files from version 2023.26 (1527) of Day One. It has not been tested with any other versions.

## Setup

**DO NOT do this in your current vault. Create a new vault for the purpose of testing. You are responsible for ensuring against data loss**
**This script renames files**
1. Export your journal from [Day One in JSON format](https://help.dayoneapp.com/en/articles/440668-exporting-entries) 
2. Expand that zip file
3. For each of the journals, adjust the root, export directory and base_tags (more details in comments)
4. Run the notebook cell-by-cell and follow instructions OR update the variables in the main function in the .py file (Not Tested)
5. Check results in Obsidian
6. If happy, move all the *journal*, *photos* *videos* and *audio* folders to whatever vault you want them in.

## Features
* Processes all entries, including any blank ones you may have. 
* Entries are titled using a zettelkasten style title (YYYYMMDDHHMMSS)
* Adds metadata for whatever exists at bottom of file
   * minimum date and timezone
   * Location as text, linked to a page
   * Tags and starred flag as tag
* Every entry has the date inserted in the text for easier reading (with a calendar icon to help you quickly distinguish from other entries in your vault)
* If location is specified, it is given under the date, linked to Google Search
* Base tags for every page (e.g. #dayoneimport) can be defined in Obsidian separate from other note tags
