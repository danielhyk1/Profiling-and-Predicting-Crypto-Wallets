import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("characteristics.csv")
#del data['ADDRESS']

# Statistics of data
print(data.describe()) #large differences in magnitude

# Standardizing data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data.loc[:, data.columns != 'ADDRESS'])

# Statistics of scaled data
print(pd.DataFrame(data_scaled).describe())

# defining the kmeans function with initialization as k-means++
kmeans = KMeans(n_clusters=2, init='k-means++')

# fitting the k means algorithm on scaled data
kmeans.fit(data_scaled)
print(kmeans.inertia_)

# fitting multiple k-means algorithms and storing the values in an empty list
SSE = []
for cluster in range(1,20):
    kmeans = KMeans(n_clusters = cluster, init='k-means++')
    kmeans.fit(data_scaled)
    SSE.append(kmeans.inertia_)

# converting the results into a dataframe and plotting them
frame = pd.DataFrame({'Cluster':range(1,20), 'SSE':SSE})
plt.figure(figsize=(12,6))
plt.plot(frame['Cluster'], frame['SSE'], marker='o')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')

# k means using 5 clusters and k-means++ initialization
kmeans = KMeans(n_clusters = 7, init='k-means++')
kmeans.fit(data_scaled)
pred = kmeans.predict(data_scaled)

frame = pd.DataFrame(data_scaled)
frame['cluster'] = pred
frame['cluster'].value_counts()
print(frame['cluster'])
print(frame['cluster'].value_counts())
####Show elbow graph####
plt.show()

###assign cluster ids to the data####
read_file = open('characteristics.csv', 'r')
out_file = open('all1.csv', 'w')
out_file.write("ADDRESS,SHARE_ZERO,MAX_VALUE,AVG_VALUE,MEDIAN_VALUE,PERIODICITY,ENTRIES,CLUSTER\n")
lines = read_file.readlines()
lines = lines[1:]
c = 0
for line in lines:
    line = line.strip()
    line += ","
    line += str(frame['cluster'][c])
    out_file.write(line + "\n")
    c += 1

read_file.close()
out_file.close()