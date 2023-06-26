# The purpose of this program is to combine the statistics from the R model and the clustering model

r_model = open("statistics.csv", 'r')
k_means_model = open("all.csv", 'r')
all_statistics = open("all_statistics.csv", 'w')
all_statistics.write(
    "ADDRESS,pdq,MSE_EMA,MSE_ARIMA,MSE_GARCH,MSE_GJRGARCH,SHARE_ZERO,MAX_VALUE,AVG_VALUE,MEDIAN_VALUE,PERIODICITY,ENTRIES,CLUSTER\n")
r_lines = r_model.readlines()
k_lines = k_means_model.readlines()
r_lines = r_lines[1:]

for r_line in r_lines:
    r_line = r_line.strip()
    for k_line in k_lines:
        k_line = k_line.strip()
        if r_line.split(",")[0] == k_line.split(",")[0]:
            k_list = k_line.split(",")
            r_line += ","
            r_line += k_list[1] + "," + k_list[2] + "," + k_list[3] + "," + k_list[4] + "," + k_list[5] + "," + k_list[
                6] + "," + k_list[7]
            print(r_line)
            all_statistics.write(r_line + "\n")

all_statistics.close()
k_means_model.close()
r_model.close()
