import os

import requests

API = "" #API KEY

# Use loop below if you want tens/hundreds of thousands of addresses
''' 
for i in range(20):
    time_increment = 70000
    start_time = 1681198400
    end_time = 1681200400
'''

for time in range(10000):
    # Start time and end time of block dates (epoch unix seconds)
    start_time = 1680480000  # 1680393600
    end_time = 1680566400
    time_increment = 10800

    # Grab the start and end block ids by unix time
    startBlockID = requests.get("https://api.etherscan.io/api" +
                                "?module=block" +
                                "&action=getblocknobytime" +
                                "&timestamp=" + str(start_time + (time_increment * time)) +
                                "&closest=before" +
                                "&apikey=" + API).json()
    startBlockID = startBlockID['result']
    endBlockID = requests.get("https://api.etherscan.io/api" +
                              "?module=block" +
                              "&action=getblocknobytime" +
                              "&timestamp=" + str(end_time + (time_increment * time)) +
                              "&closest=before" +
                              "&apikey=" + API).json()
    endBlockID = endBlockID['result']

    # Get list of internal transactions by block range
    addresses = requests.get("https://api.etherscan.io/api" +
                             "?module=account" +
                             "&action=txlistinternal" +
                             "&startblock=" + str(startBlockID) +
                             "&endblock=" + str(endBlockID) +
                             "&page=1" +
                             "&offset=10000" +
                             "&sort=desc" +
                             "&apikey=" + API).json()

    # Record all addresses found into "temporary_addresses.txt", regardless of type, including duplicates
    length = len(addresses['result'])
    f = open("temporary_addresses.txt", "w")
    for i in range(length):
        address = addresses['result'][i]['to']
        f.write(address + "\n")
    f.close()

    # Create file "addresses.txt" which holds all addresses, regardless of type
    lines_seen = set()  # holds lines already seen
    outfile = open("addresses.txt", "w")
    for line in open("temporary_addresses.txt", "r"):
        if line not in lines_seen:  # not a duplicate
            outfile.write(line)
            lines_seen.add(line)
    outfile.close()
    os.remove("temporary_addresses.txt") # Remove temp file

    # For every address, strip new line characters
    f = open("addresses.txt", "r")
    filtered_addresses = f.readlines()
    formatted_addresses = [item.rstrip('\r\n') for item in filtered_addresses]
    f.close()

    # For every address, filter based on the one-to-many characterization
    for address in formatted_addresses:
        record = open("record.txt", "a")
        errors = open("errors.txt", "a")
        # API Call
        response = requests.get("https://api.etherscan.io/api" +
                                "?module=account" +
                                "&action=txlist" +
                                "&address=" + address +
                                "&startblock=0" +  # str(startBlockID) +
                                "&endblock=9999999999" +  # str(endBlockID) +
                                "&page=1" +
                                "&offset=10000" +
                                "&sort=asc" +
                                "&apikey=" + API).json()

        if response['status'] == '0':
            errors.write(str(address) + "\n")
        else:
            record.write(address)
            record.write(str(len(response['result'])) + "\n")

            # Filter the transaction lists by matching address from (ie. one to many filter)
            list_of_indices = []
            count = 0
            # Check through transactions to see if it is one to many
            for entry in response['result']:
                if address == entry['to']:
                    list_of_indices.append(count)
                    count += 1

            list_of_indices.reverse()
            if len(response['result']) < 100:
                print("Not enough transactions" + str(len(response['result'])) + "\n")
            else:
                print("Count of receiving addresses: " + str(count) + " total addresses: " + str(len(response['result'])) + "\n")
                # Find and Record all addresses with at least 100 one-to-many transactions
                if len(response['result']) - count > 100:
                    for i in list_of_indices:
                        del response['result'][i]
                    # Add address
                    if len(response['result']) != 0:
                        print("added\n")
                        file = open("one_to_many.txt", "a")
                        file.write(address + "\n")
                        file.close()

        record.close()
        errors.close()
