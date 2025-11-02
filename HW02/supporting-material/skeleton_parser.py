
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


def parse_item(item):
    USERS = set()
    ITEMS = set()
    CATEGORIES = set()
    BIDS = set()

    seller = item.get("Seller", {})
    seller_user_id = seller.get("UserID")
    seller_rating = int(seller.get("Rating")) if seller.get("Rating") else None
    seller_location = item.get("Location")
    seller_country = item.get("Country")

    if seller_user_id:
        USERS.add((seller_user_id, seller_rating, seller_location, seller_country))

    item_id = item.get("ItemID")
    item_name = item.get("Name")
    item_currently = transformDollar(item.get("Currently"))
    item_first_bid = transformDollar(item.get("First_Bid"))
    item_number_of_bids = int(item.get("Number_of_Bids")) if item.get("Number_of_Bids") else 0
    item_location = item.get("Location")
    item_country = item.get("Country")
    item_started = transformDttm(item.get("Started"))
    item_ends = transformDttm(item.get("Ends"))
    item_description = item.get("Description")

    ITEMS.add((
        item_id, item_name, item_currently, item_first_bid,
        item_number_of_bids, item_location, item_country,
        item_started, item_ends, seller_user_id, item_description
    ))

    for cat in item.get("Category", []):
        CATEGORIES.add((item_id, cat))

    for bid in item.get("Bids", []) or []:
        bid = bid.get("Bid", {})
        bidder = bid.get("Bidder", {})
        bidder_user_id = bidder.get("UserID")
        bidder_rating = int(bidder.get("Rating")) if bidder.get("Rating") else None
        bidder_location = bidder.get("Location")
        bidder_country = bidder.get("Country")

        if bidder_user_id:
            USERS.add((bidder_user_id, bidder_rating, bidder_location, bidder_country))

        bid_time = transformDttm(bid.get("Time"))
        bid_amount = transformDollar(bid.get("Amount"))
        if bidder_user_id and item_id:
            BIDS.add((item_id, bidder_user_id, bid_time, bid_amount))

    return (USERS, ITEMS, CATEGORIES, BIDS)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        for item in items:
            """
            TODO: traverse the items dictionary to extract information from the
            given `json_file' and generate the necessary .dat files to generate
            the SQL tables based on your relation design
            """
            (u, i, c, b) = parse_item(item)


"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python json_parser.py <path to json files>'
        sys.exit(1)
    # loops over all .json files in the argument
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print ("Success parsing " + f)

if __name__ == '__main__':
    main(sys.argv)
