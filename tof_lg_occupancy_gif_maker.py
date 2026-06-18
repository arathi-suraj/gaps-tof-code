import gondola as go
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib
from PIL import Image
import time 
import os, sys # to suppress the output from the gondola function
import glob # to locate .png files from other directories easily

total_start_time = 1765844700 # Dec 15 2025, 19:25 EST, when Kazu said that HV can be turned on in Slack
total_end_time = 1767979860 #1767979860 # Jan 09 2026, 12:31 EST, when Field posted that the safe shutdown process had begun in Slack
step_size = 3600 # in seconds

event_counter = 0
panic_error = 0 # how many times the pyo3_runtime.PanicException was raised
error_log = [] # keeps track of what errors were raised

ltb_to_paddle_map = go.db.get_dsi_j_ch_pid_map() # tells us which paddle has triggered (by paddle ID) for a given LTB hit, might be a slow line

class HidePrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

for times in tqdm(range(total_start_time, total_end_time, step_size)):

    #print(times)
    # Fetch files for just that one hour

    with HidePrints(): # to suppress output of this function. We don't need to see it
        files = go.io.grace_get_telemetry_binaries(times, times+step_size, "/data1/nextcloud/cra_data/data/binaries_berkeley/starlink/")

    occupancy_dict = {} # creating an occupancy dict
    for rep in range(1, 161): # filling it with zeroes. If I only include active paddles, then the colormap will throw a key error for paddles that did not participate at all
        occupancy_dict[rep] = 0

    # Iterating over all files within the time period
    for file in files:
        reader = go.io.TelemetryPacketReader(str(file))
        #print(reader)

        for packet in reader:
            if not packet.is_event_packet:
                #print("skipped") # these could be some packets that have to do with HK data or GPS info etc.
                continue

            event_counter += 1
            
            event = go.events.TelemetryEvent.from_telemetrypacket(packet) # not sure what this intermediate object does

            tof_event = event.tof # need this to extract tof specific info from the full packet, which prob. containes header+tracker info
            try:
                trig_paddles = [int(i) for i in tof_event.get_triggered_paddles(ltb_to_paddle_map)]
            except (GeneratorExit, KeyboardInterrupt, SystemExit):
                raise
            except BaseException as e:
                trig_paddles = []
                panic_error += 1
                error_log.append(str(e))
                print(tof_event)
                raise e

            for paddle_id in trig_paddles:
                occupancy_dict[paddle_id] += 1 # not sure if a single paddle can be here twice
            
            """for hit in tof_event.hits: # this has hit info according to my investigation
                paddle_id = hit.paddle_id
                #print(paddle_id)
                try: # if key with a particular paddle id exists
                    occupancy_dict[paddle_id] += 1
                except KeyError: # which means there is no key for a particular paddle id yet # should not reach this part anymore with my filling the dict earlier
                    occupancy_dict[paddle_id] = 1"""

    cm = matplotlib.colormaps['Purples']

    fig1, ax1 = go.visual.tof.grace_tof_projection_xy(paddle_occupancy=occupancy_dict, cmap=cm)
    fig2, ax2 = go.visual.tof.grace_unroll_cbe_sides(paddle_occupancy=occupancy_dict, cmap=cm)
    fig3, ax3 = go.visual.tof.grace_unroll_cor(paddle_occupancy=occupancy_dict, cmap=cm)

    tfmt1 = time.strftime("%y/%m/%d-%H:%M", time.gmtime(times))
    tfmt2 = time.strftime("%y/%m/%d-%H:%M", time.gmtime(times+step_size))

    fig1.suptitle(f"Range: {tfmt1} to {tfmt2} (GMT), low gain")
    fig2.suptitle(f"Range: {tfmt1} to {tfmt2} (GMT), low gain")
    fig3.suptitle(f"Range: {tfmt1} to {tfmt2} (GMT), low gain")

    fig1.savefig(f"/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/xy/tof_xy_{times}_{event_counter}.png")
    fig2.savefig(f"/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/cube_sides/tof_cube_sides_{times}_{event_counter}.png")
    fig3.savefig(f"/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/cortina/tof_cortina_{times}_{event_counter}.png")

    plt.close(fig1)
    plt.close(fig2)
    plt.close(fig3)


print("all figures made")
cor_images = []
print("making cortina gif")
# all the plotting should be finished by this point
for filename in sorted(glob.glob("/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/cortina/*.png")):
    im = Image.open(filename)
    cor_images.append(im)

cor_images[0].save("/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/cor.gif", save_all=True, append_images=cor_images[1:], duration=500, loop=0) # duration - duration of each frame in GIF in ms, loop - 0 means loop forever

xy_images = []
print("making xy gif")
for filename in sorted(glob.glob("/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/xy/*.png")):
    im = Image.open(filename)
    xy_images.append(im)

xy_images[0].save("/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/xy.gif", save_all=True, append_images=xy_images[1:], duration=500, loop=0) # duration - duration of each frame in GIF in ms, loop - 0 means loop forever

cube_images = []
print("making cube sides gif")
for filename in sorted(glob.glob("/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/cube_sides/*.png")):
    im = Image.open(filename)
    cube_images.append(im)

cube_images[0].save("/home/suraj.a/gaps_tof/images/full_flight_TOF_LG_occupancy_hourly/cube_sides.gif", save_all=True, append_images=cube_images[1:], duration=500, loop=0) # duration - duration of each frame in GIF in ms, loop - 0 means loop forever