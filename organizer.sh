#!/bin/bash
# organizer.sh - archives grades.csv with a timestamp, resets the workspace
# with a new empty grades.csv, and logs the operation to organizer.log.

ARCHIVE_DIR="archive"
LOG_FILE="organizer.log"
SOURCE="grades.csv"

# Create the archive directory if it does not exist
if [ ! -d "$ARCHIVE_DIR" ]; then
    mkdir "$ARCHIVE_DIR" || { echo "Error: could not create '$ARCHIVE_DIR'."; exit 1; }
fi

# Make sure there is something to archive
if [ ! -f "$SOURCE" ]; then
    echo "Error: '$SOURCE' not found in $(pwd). Nothing to archive."
    exit 1
fi

TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
NEW_NAME="grades_${TIMESTAMP}.csv"

# Never overwrite an existing archive (e.g. two runs within the same second)
if [ -e "$ARCHIVE_DIR/$NEW_NAME" ]; then
    sleep 1
    TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
    NEW_NAME="grades_${TIMESTAMP}.csv"
fi

# Archive the file, then immediately create a fresh empty grades.csv
mv "$SOURCE" "$ARCHIVE_DIR/$NEW_NAME" || { echo "Error: could not archive '$SOURCE'."; exit 1; }
touch "$SOURCE"

# Append the details to the log (the log accumulates across runs)
echo "[$TIMESTAMP] Original: $SOURCE | Archived as: $ARCHIVE_DIR/$NEW_NAME" >> "$LOG_FILE"

echo "Archived $SOURCE as $ARCHIVE_DIR/$NEW_NAME"
