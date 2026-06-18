import gondola as go
from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib

start_time = 1765876784
end_time = 1765898029
files = go.io.grace_get_telemetry_binaries(start_time, end_time, "/data1/nextcloud/cra_data/data/binaries_berkeley/starlink/") # don't know what a PosixPath object is but these are that type

occupancy_dict = {}
for times in range(1, 161): # filling it with zeroes. If I only include active paddles, then the colormap will throw a key error for paddles that did not participate at all
    occupancy_dict[times] = 0

event_counter = 0
packet_types = {"InterestingEvent":0, "NoGapsTriggerEvent":0, "BoringEvent":0, "NoTofDataEvent":0}
tof_event_type = {"AnyDataMangling":0, "CRC32Wrong":0, "CellAndChnSyncErrors":0, "CellSyncErrors":0, "ChannelIDWrong":0, "ChnSyncErrors":0, "EventTimeOut":0, "GoodNoCRCCheck":0, "GoodNoCRCOrErrBitCheck":0, "GoodNoErrBitCheck":0, "IncompatibleData":0, "IncompleteReadout":0, "KnownDeadRB":0, "NoChannel9":0, "Perfect":0, "RBEventWacky":0, "TailWrong":0, "Unknown":0}
for file in tqdm(files):
    reader = go.io.TelemetryPacketReader(str(file))
    #print(reader)

    for packet in reader:
        if not packet.is_event_packet:
            #print("skipped") # these could be some packets that have to do with HK data or GPS info etc.
            continue

        event_counter += 1
        
        event = go.events.TelemetryEvent.from_telemetrypacket(packet) # not sure what this intermediate object does

        packet_types[str(packet.header.packet_type).split(".")[1]] += 1
        #print(str(packet.header.packet_type))

        tof_event = event.tof # need this to extract tof specific info from the full packet, which prob. containes header+tracker info
        #print(str(tof_event.event_status).split(".")[1])
        tof_event_type[str(tof_event.event_status).split(".")[1]] += 1

        tracker_event = event.tracker
        print(f"Length of tracker event: {len(tracker_event)}")

        #rb_events_list = tof_event.rb_events # Grace says that this is where hits are stored. It needs to be unpacked
        #print(rb_events_list)
        for hit in tof_event.hits: # this has hit info according to my investigation
            paddle_id = hit.paddle_id
            #print(paddle_id)
            try: # if key with a particular paddle id exists
                occupancy_dict[paddle_id] += 1
            except KeyError: # which means there is no key for a particular paddle id yet # should not reach this part anymore with my filling the dict earlier
                occupancy_dict[paddle_id] = 1

        #print(tof_event.hits)

        #event_status = tof_event.event_status
        #print(event_status)

        """ 
        for rb_event in rb_events_list:
            hits = rb_event.hits # has all hit info?
            #print(hits)
            #print(counter)
            #counter+=1

            for hit in hits: # this is the individual hit level.
                paddle_id = hit.paddle_id
                print(paddle_id)
                try: # if key with a particular paddle id exists
                    occupancy_dict[paddle_id] += 1
                except KeyError: # which means there is no key for a particular paddle id yet
                    occupancy_dict[paddle_id] = 1
        """

print(occupancy_dict)
print(f"The total number of events was {event_counter}.")
#print(packet_types)
print(tof_event_type)

cm = matplotlib.colormaps['viridis']

fig1, ax1 = go.visual.tof.grace_tof_projection_xy(paddle_occupancy=occupancy_dict, cmap=cm)
fig2, ax2 = go.visual.tof.grace_unroll_cbe_sides(paddle_occupancy=occupancy_dict, cmap=cm)
fig3, ax3 = go.visual.tof.grace_unroll_cor(paddle_occupancy=occupancy_dict, cmap=cm)

fig1.savefig("/home/suraj.a/gaps_tof/images/Run_10046/tof_xy.png")
fig2.savefig("/home/suraj.a/gaps_tof/images/Run_10046/tof_cube_sides.png")
fig3.savefig("/home/suraj.a/gaps_tof/images/Run_10046/tof_cortina.png")

print("Finished drawing figures")
# plotting
#for key in packet_types:
#    packet_types[key] = packet_types[key]/event_counter * 100

#for key in tof_event_type:
#    tof_event_type[key] = tof_event_type[key]/event_counter * 100

#fig, axs = plt.subplots(1, 2)
#fig.suptitle("Packet and TOF event info for Run 10075")