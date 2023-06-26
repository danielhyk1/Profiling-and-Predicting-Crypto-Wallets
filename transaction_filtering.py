import math
import statistics
import requests
import pandas as pd
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import os.path

path_of_transactions = '' #Path to folder that will hold all of the transactions

# Create statistics csv file for addresses
characteristics_file = open("characteristics.csv", "w")
characteristics_file.write("ADDRESS,SHARE_ZERO,MAX_VALUE,AVG_VALUE,MEDIAN_VALUE,PERIODICITY,ENTRIES\n")
characteristics_file.close()

# Open addresses
all_addresses = open("start.txt", 'r')
addresses = all_addresses.readlines()
API = "" #API key for Etherscan
for address in addresses:
    address_name = address.strip()
    print(address_name)
    characteristics_file = open("characteristics.csv", "a")
    file_name = os.path.join(path_of_transactions, "transaction_" + address_name + ".csv")
    file_address = open(file_name, "w")
    file_address.write(
        "ID,TIMESTAMP,VALUE,LOGVAL,GAS_PRICE,GAS_AMT\n")  # time/id, timestamp, value, logvalue, gas_price, gas_amount
    df = requests.get("https://api.etherscan.io/api" +
                      "?module=account" +
                      "&action=txlist" +
                      "&address=" + address_name +
                      "&startblock=" + "0" +  # str(startBlockID) +
                      "&endblock=" + "9999999999" +  # str(endBlockID) +
                      "&page=1" +
                      "&offset=10000" +
                      "&sort=asc" +
                      "&apikey=" + API).json()

    # Initialize variables
    value = []
    timeStamp = []
    time = []
    gas_price = []
    gas_amount = []
    periodicity = []
    prev_index = 0
    zero_counter = 0
    value_counter = 0
    size = len(df['result'])
    for i in range(size):
        if address_name.lower() == str(df['result'][i]['from']).lower():  # Check for sending addresses
            # Obtain values
            v = int(df['result'][i]['value']) / 1000000000000000000
            lV = math.log(v + 1)
            t = int(df['result'][i]['timeStamp'])
            gAmt = int(df['result'][i]['cumulativeGasUsed']) / 1000000000
            gPrc = int(df['result'][i]['gasPrice']) / 1000000000

            # Count zero for zero_share variable
            if v == 0:
                zero_counter += 1
            # Calculate Periodicity
            if v > 0 and i == 0:
                prev_index = 0  # Pass as to avoid miscounting first value
            elif v > 0:
                periodicity.append(i - prev_index - 1)
                prev_index = i
            if i == size - 1 and v == 0:  # check end case
                periodicity.append(i - prev_index)

            # Create Datastructures
            value.append(v)
            timeStamp.append(t)
            gas_amount.append(gAmt)
            time.append(i)
            gas_price.append(gPrc)

            # Add to CSV
            file_address.write(
                str(i) + "," + str(t) + "," + str(v) + "," + str(lV) + "," + str(gPrc) + "," + str(gAmt) + "\n")

    # close files
    file_address.close()
    # DATA TRANSFORMATION - Take top 100 valued observations
    # sort arrays
    valueCopy, timeCopy = zip(*sorted(zip(value, time), reverse=True))
    topValue = valueCopy[:100]
    topTime = timeCopy[:100]
    topTime, topValue = zip(*sorted(zip(topTime, topValue)))
    # store top value
    file_top_name = os.path.join(path_of_transactions, "top_" + address_name + ".csv")
    file_top = open(file_top_name, "w")
    file_top.write("ID,VALUE\n")
    for z in range(100):
        file_top.write(str(z) + "," + str(topValue[z]) + "\n")
    file_top.close()

    # add characteristics
    length = len(df['result'])
    share_zero = zero_counter / length
    mean_value = statistics.mean(value)
    max_value = max(value)
    median_value = statistics.median(value)
    mean_periodicity = statistics.mean(periodicity)
    max_entries = size

    characteristics_file.write(
        str(address_name) + "," + str(share_zero) + "," + str(max_value) + "," + str(mean_value) + "," + str(
            median_value) + "," + str(mean_periodicity) + "," + str(max_entries) + "\n")
    characteristics_file.close()

all_addresses.close()
