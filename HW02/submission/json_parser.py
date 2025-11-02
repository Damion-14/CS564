
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)


def escape_field(field):
    """
    Escapes special characters in fields for SQLite bulk loading.
    Handles None values and converts to proper string format.
    """
    if field is None:
        return ""
    # Convert to string and replace any problematic characters
    field_str = str(field)
    # Escape double quotes by doubling them (SQL standard)
    field_str = field_str.replace('"', '""')
    # Replace newlines with spaces to avoid breaking the format
    field_str = field_str.replace('\n', ' ').replace('\r', ' ')
    return field_str

def parse_item(item):
    """
    Parse a single item from JSON and extract tuples for all tables.
    Returns sets of tuples for USERS, ITEMS, ITEM_CATEGORIES, and BIDS.
    """
    USERS = set()
    ITEMS = set()
    CATEGORIES = set()
    BIDS = set()

    # Extract seller information
    seller = item.get("Seller", {})
    seller_user_id = seller.get("UserID")
    seller_rating = seller.get("Rating")

    # Seller's location and country come from the item level
    seller_location = item.get("Location")
    seller_country = item.get("Country")

    # Add seller to USERS table
    if seller_user_id:
        USERS.add((seller_user_id, seller_rating, seller_location, seller_country))

    # Extract item information
    item_id = item.get("ItemID")
    item_name = item.get("Name")
    item_currently = transformDollar(item.get("Currently"))
    item_first_bid = transformDollar(item.get("First_Bid"))
    item_number_of_bids = item.get("Number_of_Bids")
    item_country = item.get("Country")
    item_started = transformDttm(item.get("Started"))
    item_ends = transformDttm(item.get("Ends"))
    item_description = item.get("Description")

    # Add to ITEMS table
    ITEMS.add((
        item_id, item_name, item_currently, item_first_bid,
        item_number_of_bids, item_country,
        item_started, item_ends, seller_user_id, item_description
    ))

    # Extract categories
    categories = item.get("Category", [])
    if categories:
        for cat in categories:
            CATEGORIES.add((item_id, cat))

    # Extract bids
    bids = item.get("Bids")
    if bids:
        for bid_entry in bids:
            bid = bid_entry.get("Bid", {})
            bidder = bid.get("Bidder", {})

            bidder_user_id = bidder.get("UserID")
            bidder_rating = bidder.get("Rating")
            bidder_location = bidder.get("Location")
            bidder_country = bidder.get("Country")

            # Add bidder to USERS table
            if bidder_user_id:
                USERS.add((bidder_user_id, bidder_rating, bidder_location, bidder_country))

            # Extract bid information
            bid_time = transformDttm(bid.get("Time"))
            bid_amount = transformDollar(bid.get("Amount"))

            # Add to BIDS table
            if bidder_user_id and item_id:
                BIDS.add((bidder_user_id, item_id, bid_time, bid_amount))

    return (USERS, ITEMS, CATEGORIES, BIDS)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file, all_users, all_items, all_categories, all_bids):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        for item in items:
            # Parse each item and collect data
            (users, items_data, categories, bids) = parse_item(item)

            # Add to global sets to handle duplicates automatically
            all_users.update(users)
            all_items.update(items_data)
            all_categories.update(categories)
            all_bids.update(bids)


def write_dat_files(all_users, all_items, all_categories, all_bids):
    """
    Write all collected data to .dat files for SQLite bulk loading.
    Uses | as the column separator as specified.
    All fields are wrapped in double quotes to handle special characters.
    """
    # Write USERS table
    with open('users.dat', 'w') as f:
        for user in all_users:
            user_id, rating, location, country = user
            # Wrap each field in quotes for CSV mode
            line = columnSeparator.join([
                '"' + escape_field(user_id) + '"',
                '"' + escape_field(rating) + '"',
                '"' + escape_field(location) + '"',
                '"' + escape_field(country) + '"'
            ])
            f.write(line + '\n')

    # Write ITEMS table
    with open('items.dat', 'w') as f:
        for item in all_items:
            item_id, name, currently, first_bid, num_bids, country, started, ends, seller_id, description = item
            # Wrap each field in quotes for CSV mode
            line = columnSeparator.join([
                '"' + escape_field(item_id) + '"',
                '"' + escape_field(name) + '"',
                '"' + escape_field(currently) + '"',
                '"' + escape_field(first_bid) + '"',
                '"' + escape_field(num_bids) + '"',
                '"' + escape_field(country) + '"',
                '"' + escape_field(started) + '"',
                '"' + escape_field(ends) + '"',
                '"' + escape_field(seller_id) + '"',
                '"' + escape_field(description) + '"'
            ])
            f.write(line + '\n')

    # Write ITEM_CATEGORIES table
    with open('item_categories.dat', 'w') as f:
        for category in all_categories:
            item_id, cat = category
            # Wrap each field in quotes for CSV mode
            line = columnSeparator.join([
                '"' + escape_field(item_id) + '"',
                '"' + escape_field(cat) + '"'
            ])
            f.write(line + '\n')

    # Write BIDS table
    with open('bids.dat', 'w') as f:
        for bid in all_bids:
            user_id, item_id, time, amount = bid
            # Wrap each field in quotes for CSV mode
            line = columnSeparator.join([
                '"' + escape_field(user_id) + '"',
                '"' + escape_field(item_id) + '"',
                '"' + escape_field(time) + '"',
                '"' + escape_field(amount) + '"'
            ])
            f.write(line + '\n')

"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print('Usage: python json_parser.py <path to json files>', file=sys.stderr)
        sys.exit(1)

    # Initialize global sets to collect all data
    all_users = set()
    all_items = set()
    all_categories = set()
    all_bids = set()

    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f, all_users, all_items, all_categories, all_bids)
            print("Success parsing " + f)

    # Write all data to .dat files
    print("Writing data to .dat files...")
    write_dat_files(all_users, all_items, all_categories, all_bids)
    print("Done! Generated files:")
    print("  - users.dat (%d records)" % len(all_users))
    print("  - items.dat (%d records)" % len(all_items))
    print("  - item_categories.dat (%d records)" % len(all_categories))
    print("  - bids.dat (%d records)" % len(all_bids))

if __name__ == '__main__':
    main(sys.argv)
