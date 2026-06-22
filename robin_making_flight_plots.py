from pybfsw.gse.gsequery import GSEQuery # to make a query from the database
import matplotlib.pyplot as plt
import time 
import numpy as np
from tqdm import tqdm

plt.style.use("GAPS_figure.mplstyle")

# time window
start_time = 1765844700 # Dec 15 2025, 19:25 EST, when Kazu said that HV can be turned on in Slack
stop_time = 1767979860 # Jan 09 2026, 12:31 EST, when Field posted that the safe shutdown process had begun in Slack
#tfmt = time.strftime("%y/%m/%d-%H:%M:%S", time.gmtime(start_time))
#print(f"{start_time} in a pretty format is {tfmt}.")


# setting up a figure
fig, axs = plt.subplots(3, 1, figsize=(20, 13), layout="constrained")
fig.suptitle("Full GAPS flight, times in GMT", fontsize="x-large")
axs[0].set_title("Total trigger rates")
axs[0].set_ylabel("Averaged Rate (Hz)")
axs[1].set_title("Total + individual trigger rates")
axs[1].set_ylabel("Averaged Rate (Hz)")
axs[2].set_title("(90 + 190), 191 rates")
axs[2].set_ylabel("Averaged Rate (Hz)")
axs[2].set_xlabel("Flight time")

# querying + storing info
query_obj = GSEQuery()

size_of_one_bin = 3600 # in seconds
partitioned_times = [t for t in range(start_time, stop_time+size_of_one_bin, size_of_one_bin)]
pretty_times = [time.strftime("%m/%d-%H:%M", time.gmtime(t)) for t in partitioned_times] # reformatting the times to be pretty

ds_pt_times = [] # downsampled partitioned times for plotting 
ds_pretty_times = [] # downsampled pretty times for plotting

for ind in range(0, len(partitioned_times), len(partitioned_times)//15): # pick a point every 12 hours
    ds_pt_times.append(partitioned_times[ind])
    ds_pretty_times.append(pretty_times[ind])

print(len(ds_pt_times))
print(len(partitioned_times))

data_90_array = np.zeros(shape=len(partitioned_times)-1)
data_190_array = np.zeros(shape=len(partitioned_times)-1)
data_191_array = np.zeros(shape=len(partitioned_times)-1)
data_192_array = np.zeros(shape=len(partitioned_times)-1)


data_points_gsedb = 0
for ind in tqdm(range(len(partitioned_times))):
    try: # should create an error on the last iteration and we should skip it.
        data_90 = query_obj.time_query3("@mev_stats_count_rate_90", partitioned_times[ind], partitioned_times[ind+1])
        data_90_array[ind] = np.mean(data_90[1])
        data_190 = query_obj.time_query3("@mev_stats_count_rate_190", partitioned_times[ind], partitioned_times[ind+1])
        data_190_array[ind] = np.mean(data_190[1])
        data_191 = query_obj.time_query3("@mev_stats_count_rate_191", partitioned_times[ind], partitioned_times[ind+1])
        data_191_array[ind] = np.mean(data_191[1])
        data_192 = query_obj.time_query3("@mev_stats_count_rate_192", partitioned_times[ind], partitioned_times[ind+1])
        data_192_array[ind] = np.mean(data_192[1])
        data_points_gsedb+=1

    except IndexError:
        print("Done getting info for full time period.")

print(f"The time array has {len(partitioned_times)} entries and we got {data_points_gsedb} entries from GSE DB.")
axs[0].plot(partitioned_times[:-1], data_90_array+data_190_array+data_191_array+data_192_array, color="#000000")
axs[0].set_xticks(ticks=ds_pt_times, labels=ds_pretty_times)

axs[1].plot(partitioned_times[:-1], data_90_array+data_190_array+data_191_array+data_192_array, color="#000000", label="Total rate")
axs[1].plot(partitioned_times[:-1], data_90_array, color="#42f551", label="90")
axs[1].plot(partitioned_times[:-1], data_190_array, color="#f5da42", label="190")
axs[1].plot(partitioned_times[:-1], data_191_array, color="#399ef7", label="191")
axs[1].plot(partitioned_times[:-1], data_192_array, color="#b839f7", label="192")
axs[1].set_xticks(ticks=ds_pt_times, labels=ds_pretty_times)
axs[1].legend()

axs[2].plot(partitioned_times[:-1], data_90_array+data_190_array, color="#f79e39", label="90+190")
axs[2].plot(partitioned_times[:-1], data_191_array, color="#399ef7", label="191")
axs[2].set_xticks(ticks=ds_pt_times, labels=ds_pretty_times)
axs[2].legend()

# include calibration times as a range
cal_times = [(1767900569, 1767914260), (1767843587, 1767864234), (1766780112, 1766786735), (1767833468, 1767834335), (1766355721, 1766366586), (1765933116, 1765936273), (1765857182, 1765861750), (1765871321, 1765876372), (1767643122, 1767643981), (1767646740, 1767647340), (1765858182, 1765858782), (1765932792, 1765933392), (1765939457, 1765940057), (1765935857, 1765936457), (1766364480, 1766365080), (1766365511, 1766366111), (1766780686, 1766781286), (1767474323, 1767474923), (1767474772, 1767475372), (1767900172, 1767900772), (1767900546, 1767901146)]
# first tuple - final tracker cal
# 2nd tuple - tracker in NZS mode
# 3rd tuple - more tracker cal
# 4 - single module NZS deadtime test
# 5 - wastie enable
# 6 - more tracker calibration
# 7 - tracker ops post full-power LOS
# 8 - NZS data
# 9 - RAT 4/5 power cycle
# 10 - power cycle RATs 4&5
# 11 - 14 - tof calibrations from elog

for item in cal_times:
    for axis in axs: # to plot on all three graphs
        axis.axvspan(item[0], item[1], ls="--", color="#e6a5a5")


#fig.savefig("/home/gaps/bfsw/pybfsw/tests/images/full_flight_GAPS_format.png")

"""
cal_times = [(1767900569, 1767914260), (1767843587, 1767864234), (1766780112, 1766786735), (1767833468, 1767834335), (1766355721, 1766366586), (1765933116, 1765936273), (1765857182, 1765861750), (1765871321, 1765876372), (1767643122, 1767643981), (1767646740, 1767647340), (1765237683, 1765238283), (1765238054, 1765238654), (1765788446, 1765789046), (1765861782, 1765862382), (1765936392, 1765936992), (1765939457, 1765940057), (1765861782, 1765862382)]
# first tuple - final tracker cal
# 2nd tuple - tracker in NZS mode
# 3rd tuple - more tracker cal
# 4 - single module NZS deadtime test
# 5 - wastie enable
# 6 - more tracker calibration
# 7 - tracker ops post full-power LOS
# 8 - NZS data
# 9 - RAT 4/5 power cycle
# 10 - power cycle RATs 4&5
# 11 - 16 - tof calibrations from elog
"""