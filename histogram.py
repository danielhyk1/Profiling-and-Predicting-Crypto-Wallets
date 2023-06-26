import csv
import matplotlib.pyplot as plt

''' Creates the one to many csv files
file = open('all_addresses.csv')
csv = csv.reader(file)

file2 = open("one_to_many.json", "r")
filtered_addresses = file2.readlines()
formatted_addresses = [item.rstrip('\r\n') for item in filtered_addresses]
file3 = open("one_to_many.csv", "a")
header = []
header = next(csv)
rows = []
for row in csv:
    for entry in formatted_addresses:
        if row[0] == entry:
            rows.append(row)
            file3.write(str(row[0]) + "," + str(row[1]) + "\n")
            break
file.close()
file2.close()
file3.close()
print(rows)
'''
#plot histograms
file3 = open("one_to_many.csv")
csv_one_many = csv.reader(file3)
header = []
header = next(csv_one_many)
#one to many addresses
transactions_one = []
for row in csv_one_many:
    transactions_one.append(row[1])
file3.close()

plt.hist(transactions_one, 30, label = 'bins = 30')
plt.ylabel('Number of transactions')
plt.title('Histogram of one-to-many addresses')
plt.show()

file2 = open("all_addresses.csv")
csv_all_addresses = csv.reader(file2)
header = []
header = next(csv_all_addresses)
transactions_all = []
#all addresses
for row in csv_all_addresses:
    transactions_all.append(row[1])
file2.close()

plt.hist(transactions_all, 30, label = 'bins = 30')
plt.ylabel('Number of transactions')
plt.title('Histogram of all addresses')

plt.show()