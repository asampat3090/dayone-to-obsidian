import datetime
import dateutil.parser
import json
import pytz  # pip install pytz
import re
import os
import sys
import shutil
import time


def create_obsidian_entry_from_day_one(
    import_dir: str,
    day_one_entry_json: json,
    export_dir: str = ".",
    tags: list = ["#dayoneimport"],
):
    """Create an Obsidian entry from a Day One entry and stores it in the folder specified by export_dir.

    Args:
        import_dir (str): folder where the Day One entry is stored and metadata is stored
        day_one_entry_json (json): Day One entry in JSON format
        export_dir (str): folder where the output obsidian file will be stored
        tags (list): list of base tags to add to the obsidian file
    """
    newEntry = []

    # create a title for the entry in format "20210618211541 - Fri Jun 18 2021.md"
    createDate = dateutil.parser.isoparse(day_one_entry_json["creationDate"])
    localDate = createDate.astimezone(
        pytz.timezone(day_one_entry_json["timeZone"])
    )  # It's natural to use our local date/time as reference point, not UTC
    # TODO: check if this works for win32 and macOSX
    newMDfilename = "%s - %s.md" % (
        localDate.strftime("%Y%m%d%H%M%S"),
        localDate.strftime("%a %b %d %Y"),
    )
    newJSONfilename = "%s - %s.json" % (
        localDate.strftime("%Y%m%d%H%M%S"),
        localDate.strftime("%a %b %d %Y"),
    )

    # --------------- FRONTMATTER ------------------------

    # Add location and date created to the front matter of the MD file
    location = ""
    for locale in ["placeName", "localityName", "administrativeArea", "country"]:
        try:
            location = "%s, %s" % (location, day_one_entry_json["location"][locale])
        except KeyError:
            pass
    location = location[2:]

    dateCreated = str(createDate)
    coordinates = ""

    frontmatter = (
        """---
- created: """
        + dateCreated
        + """
"""
    )

    if "location" in day_one_entry_json:
        coordinates = (
            str(day_one_entry_json["location"]["latitude"])
            + ","
            + str(day_one_entry_json["location"]["longitude"])
        )
        frontmatter = frontmatter + "- location: [" + coordinates + "]"
    frontmatter = (
        frontmatter
        + """
---
"""
    )
    newEntry.append(frontmatter)

    # --------------- BODY ------------------------

    # Add date as page header, removing time if it's 12 midday as time obviously not read
    if sys.platform == "win32":
        newEntry.append(
            "## %s\n"
            % (
                localDate.strftime("%A, %#d %B %Y at %#I:%M %p").replace(
                    " at 12:00 PM", ""
                ),
            )
        )
    else:
        newEntry.append(
            "## %s\n"
            % (
                localDate.strftime("%A, %-d %B %Y at %-I:%M %p").replace(
                    " at 12:00 PM", ""
                ),
            )
        )  # untested

    # Add body text if it exists (can have the odd blank entry), after some tidying up
    try:
        newText = day_one_entry_json["text"].replace("\\", "")
        newText = newText.replace("\u2028", "\n")
        newText = newText.replace("\u1C6A", "\n\n")

        # update photo references and file names if they exist
        if "photos" in day_one_entry_json:
            # Correct photo links. First we need to rename them. The filename is the md5 code, not the identifier
            # subsequently used in the text. Then we can amend the text to match. Will only to rename on first run
            # through as then, they are all renamed.

            for p in day_one_entry_json["photos"]:
                pfn = os.path.join(
                    import_dir, "photos", "%s.%s" % (p["md5"], p["type"])
                )
                if os.path.isfile(pfn):
                    newfn = os.path.join(
                        import_dir, "photos", "%s.%s" % (p["identifier"], p["type"])
                    )
                    print("Renaming photo file from %s to %s" % (pfn, newfn))
                    os.rename(pfn, newfn)
                # Now to replace the text to point to the new file
                newText = re.sub(
                    r"(\!\[\]\(dayone-moment:\/\/)" + p["identifier"] + "(\))",
                    r"![[" + p["identifier"] + "." + p["type"] + "]]",
                    newText,
                )

        # update video references and file names if they exist
        if "videos" in day_one_entry_json:
            # Correct video links. First we need to rename them. The filename is the md5 code, not the identifier
            # subsequently used in the text. Then we can amend the text to match. Will only to rename on first run
            # through as then, they are all renamed.
            # Need to account for .mov and .mp4 file types (and potentially others)

            for v in day_one_entry_json["videos"]:
                # try .mov extention else try .mp4
                vfn = os.path.join(
                    import_dir, "videos", "%s.%s" % (v["md5"], v["type"])
                )
                if os.path.isfile(vfn):
                    newfn = os.path.join(
                        import_dir, "videos", "%s.%s" % (v["identifier"], v["type"])
                    )
                    print("Renaming video file from %s to %s" % (vfn, newfn))
                    os.rename(vfn, newfn)

                # Now to replace the text to point to the file in obsidian
                newText = re.sub(
                    r"(\!\[\]\(dayone-moment:\/video\/)" + v["identifier"] + "(\))",
                    r"![[" + v["identifier"] + "." + v["type"] + "]]",
                    newText,
                )

        # update audio references and file names if they exist
        if "audios" in day_one_entry_json:
            # Correct audio links. First we need to rename them. The filename is the md5 code, not the identifier
            # subsequently used in the text. Then we can amend the text to match. Will only to rename on first run
            # through as then, they are all renamed.
            # Only handles .m4a format (seems to be the only one used by DayOne but not sure)

            for a in day_one_entry_json["audios"]:
                afn = os.path.join(import_dir, "audios", "%s.%s" % (a["md5"], "m4a"))
                if os.path.isfile(afn):
                    newfn = os.path.join(
                        import_dir, "audios", "%s.%s" % (a["identifier"], "m4a")
                    )
                    print("Renaming audio file from %s to %s" % (afn, newfn))
                    os.rename(afn, newfn)

                # Now to replace the text to point to the file in obsidian
                newText = re.sub(
                    r"(\!\[\]\(dayone-moment:\/audio\/)" + a["identifier"] + "(\))",
                    r"![[" + a["identifier"] + "." + "m4a" + "]]",
                    newText,
                )

        newEntry.append(newText)
    except KeyError:
        pass

    # --------------- BACKMATTER  ------------------------

    newEntry.append("\n\n---\n")

    if location:
        if coordinates == []:
            locationString = location
        else:
            locationString = "[" + location + "](geo:" + coordinates + ")"
        newEntry.append(locationString)

        # Add GPS, not all entries have this
        try:
            newEntry.append(
                "\n- GPS: [%s, %s](https://www.google.com/maps/search/?api=1&query=%s,%s)\n"
                % (
                    day_one_entry_json["location"]["latitude"],
                    day_one_entry_json["location"]["longitude"],
                    day_one_entry_json["location"]["latitude"],
                    day_one_entry_json["location"]["longitude"],
                )
            )
        except KeyError:
            pass

    if "tags" in day_one_entry_json:
        tags_to_add = tags
        for t in day_one_entry_json["tags"]:
            tags_to_add.append("%s%s" % ("#", t.replace(" ", "-").replace("---", "-")))
        if day_one_entry_json["starred"]:
            tags.append("#starred")
    if len(tags) > 0:
        newEntry.append("- Tags: %s\n" % " ".join(tags))

    # Write the new file to a file in the appropriate place
    with open(os.path.join(export_dir, newMDfilename), "w", encoding="utf-8") as f:
        print("Writing obsidian md file %s" % os.path.join(export_dir, newMDfilename))
        for line in newEntry:
            f.write(line)

    # Write out the day one meta data to a json file with the same name
    with open(os.path.join(export_dir, newJSONfilename), "w", encoding="utf-8") as f:
        print(
            "Writing day one json file to %s"
            % os.path.join(export_dir, newJSONfilename)
        )
        json.dump(day_one_entry_json, f, indent=4)


# ------------------------ MAIN ------------------------
if __name__ == "__main__":
    # Go through each of the journals
    # TODO: switch to parser to enable user to specify variables at command line

    def convert_day_one_journal_to_obsidian(
        root, import_journal, export_journal, base_tags
    ):
        """Converts a Day One journal to Obsidian format.

        Args:
            root (str): root folder where the Day One journal is stored
            import_journal (str): name of the Day One journal
            export_journal (str): name of directory to stor obsidian journal entries
            base_tags (list): list of base tags to add to the Obsidian journal
        """
        # Create the export folder if it doesn't exist
        if not os.path.exists(export_journal):
            os.mkdir(export_journal)

        # Read the journal file
        with open(import_journal, "r") as f:
            journal = json.load(f)

        print(len(journal["entries"]))

        counter = 0
        # Iterate through the journal entries
        for entry in journal["entries"]:
            create_obsidian_entry_from_day_one(
                root, entry, export_journal, tags=base_tags
            )
            time.sleep(1)  # sleep for 1 second to avoid duplicate filenames
            counter += 1
        print("Complete: %d entries processed." % counter)

    ########## SPECIFIC JOURNALS FOR ANAND (NEED TO GENERALIZE) ##########
    # TODO: generalize below to allow any user to input their own journal exports

    # Daily Reflections
    root = "/Volumes/External/01-01-2024_9-10-PM"
    import_journal = os.path.join(root, "Daily Reflection.json")
    export_journal = os.path.join(root, "Daily Reflection")
    base_tags = ["#dailyjournal", "#dayoneimport"]
    convert_day_one_journal_to_obsidian(root, import_journal, export_journal, base_tags)

    # Health Journal
    root = "/Volumes/External/01-01-2024_9-10-PM"
    import_journal = os.path.join(root, "Health Journal.json")
    export_journal = os.path.join(root, "Health Journal")
    base_tags = ["#healthjournal", "#dayoneimport"]
    convert_day_one_journal_to_obsidian(root, import_journal, export_journal, base_tags)

    # Gratitude Journal
    root = "/Volumes/External/01-01-2024_9-10-PM"
    import_journal = os.path.join(root, "Gratitude Journal.json")
    export_journal = os.path.join(root, "Gratitude Journal")
    base_tags = ["#gratitudejournal", "#dayoneimport"]
    convert_day_one_journal_to_obsidian(root, import_journal, export_journal, base_tags)

    # Yearly Reflections
    root = "/Volumes/External/01-01-2024_9-10-PM"
    import_journal = os.path.join(root, "Yearly Reflections.json")
    export_journal = os.path.join(root, "Yearly Reflections")
    base_tags = ["#yearlyreflection", "#dayoneimport"]
    convert_day_one_journal_to_obsidian(root, import_journal, export_journal, base_tags)
