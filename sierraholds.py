#!/usr/bin/python2.7

import sys

## REINSTATE TO USE COMMAND LINE ARGUMENT
#if (len(sys.argv) <= 1):
#    print "Please specify file."
#    exit()

# Length of the label for each line
LABEL_LENGTH = 18

# rip out page numbers
PAGE_STRING = "Page "

# detect header
HEADER_FOUND = -1
HEADER_STRING = "Outstanding Holds Placed Before "
timeString = ""

# list of possible labels
LABELS = {
    "number": "#",
    "date_placed": "Date Placed",
    "not_needed_after": "Not Needed After",
    "not_needed_before": "Not Needed Before",
    "patron_info": "Patron Info",
    "title": "TITLE",
    "call_num": "CALL #",
    "barcode": "BARCODE",
    "location": "LOCATION",
    "pickup_location": "Pickup Location",
    "hold_status": "Hold Status",
    "status": "STATUS",
    "hold_note": "Hold Note"
}

## METHODS
# Clean a string
def cleanString(line):
    return line.replace("\n", "").strip()

# Update the row with data from the line, return the variable that was set
def setRowDataFromLine(row, line_label, line_val, last_var_name):
    clean_label = cleanString(line_label)
    clean_val = cleanString(line_val)

    for var_name in LABELS.keys():
        if line_label.find(LABELS[var_name]) == 0:
            row[var_name] = clean_val
            return var_name

    # we didn't find a matching variable, assume that we're still writing the previous variable data
    # patron_info should be the only thing that stores blank lines
    # its also possible that label is non-empty, but val is empty, in that case prepend label to val
    if (len(clean_val) > 0 or len(clean_label) > 0 or last_var_name == "patron_info") and clean_val.find(PAGE_STRING) != 0:

        if len(clean_label) > 0:
            clean_val = clean_label + clean_val

        row[last_var_name] = row[last_var_name] + "\n" + clean_val

    return last_var_name

## MAIN EXECUTION
# read the file into a list
hold_data = []

## REINSTATE TO USE COMMAND LINE ARGUMENT
#path = sys.argv[1]

# path of reliable filename
path = "./mail.google.com"

f = open(path, 'r')
for line in f:
    hold_data.append(line)

# store the data in rows for a csv
rows = []
row = {}
last_var_name = ""

# detect report header
for j in range(len(hold_data)):
    if hold_data[j].find(HEADER_STRING) != -1:
        HEADER_FOUND = j
        break

# save timestamp of report and cut off header
if HEADER_FOUND != -1:
    timeString=cleanString(hold_data[HEADER_FOUND+1]).replace(" ","_").replace(":","")
    hold_data=hold_data[(HEADER_FOUND+5):]

for i in range(len(hold_data)):
    # split the line into its relevant pieces
    line = hold_data[i]
    line_label = line[:LABEL_LENGTH]
    line_val = line[LABEL_LENGTH:]

    # if we're on the number, then we're creating a new row
    if line_label.find(LABELS["number"]) == 0:
        if (len(row) != 0):
            rows.append(row)
        row = {}

    # save the line's data to the row
    last_var_name = setRowDataFromLine(row, line_label, line_val, last_var_name)

# add the final row
rows.append(row)

# prepare output file
f = open('holds_'+timeString+'.csv','w')

# output the csv header to file
print >> f, '"number","date_placed","not_needed_after","not_needed_before","patron_name","patron_number","patron_email","patron_phone","title","call_num","barcode","location","pickup_location","hold_status","status","hold_note"'

# output the csv body to file
for row in rows:
    patron_info = row["patron_info"].split("\n")

    print >> f, '"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"' % (
        row["number"],
        row["date_placed"],
        row["not_needed_after"],
        row["not_needed_before"],
        "" if (len(patron_info) < 1) else patron_info[0],
        "" if (len(patron_info) < 2) else patron_info[1],
        "" if (len(patron_info) < 3) else patron_info[2],
        "" if (len(patron_info) < 4) else patron_info[3],
        row["title"],
        row["call_num"],
        row["barcode"],
        row["location"],
        row["pickup_location"],
        row["hold_status"],
        row["status"],
        row["hold_note"])

f.close()
