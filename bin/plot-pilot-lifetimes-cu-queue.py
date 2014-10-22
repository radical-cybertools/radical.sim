#!/usr/bin/env python

# TODO: Use constants for colors

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator
from pprint import pprint
import json

def plot_pilotlifetime(data):

    # keep track of the finishing time of the last compute unit
    ltf = 0
    for cu in data['cus']:
        done = data['cus'][cu]['Done']
        ltf = max(ltf, done)

    # Pilot Life times
    pilot_start_times = []
    durations = []
    cum_cores = 0
    pilots = [] # TODO: should be a dict?
    for p_id in data['pilots']:
        pilot = data['pilots'][p_id]
        # cores, new, running, end
        if not 'Canceled' in pilot:
            end = ltf + 1
        else:
            end = pilot['Canceled']

        pilot_start_times.append(pilot['New']) # collect start coordinates
        durations.append(end-pilot['New']) # collect duration
        y = cum_cores + pilot['cores']/2.0 + 0.5
        pilots.append(y)
        cum_cores += pilot['cores']
    pilot_durations = [ [0] * len(pilots), durations ] # error = [(0, duration)]

    eb = plt.subplot(111)
    eb.yaxis.set_major_locator(MaxNLocator(integer=True))
    eb.set_ylabel('ComputePilot Instance')
    eb.set_xlabel('Time (s)')
    #eb.set_ylim(0,10)

    # Plot total lifetime
    #eb.errorbar(pilot_start_times, pilots, xerr=pilot_durations, fmt='None', ecolor='black', label='ComputePilot')

    # Pilot Queue times
    cum_cores = 0
    for p_id in data['pilots']:
        # cores, new, running, end in pilot_lifetimes:
        pilot = data['pilots'][p_id]
        bootstrapping = pilot['Bootstrapping']
        new = pilot['New']
        cores = pilot['cores']
        active = pilot['Active']
        end = pilot['Canceled']

        y = cum_cores + cores/2.0 + 0.5
        #y = cum_cores + cores
        #y = cum_cores + cores/2.0 + 0.5

        # plot red only for pilots that never started
        if not active:
            active = ltf + 1

        for offset in range(cores):
            eb.broken_barh([(new, end)], (cum_cores + offset + .6  , .8), edgecolor='black',
                           facecolor='LightGrey', label='Core Idle')

        eb.broken_barh([(new, bootstrapping-new), (bootstrapping, active-bootstrapping)], (y-cores/2.0+.1, cores-.2), edgecolor=['red','Blue'],
                facecolor=['red', 'Blue'], label='Pilot Queue')

        cum_cores += cores

    # CU Life Times
    #for pilot, slots, name, cores, state, errno, download, run, upload, end, site in cus:
    for cu_id in data['cus']:
        cu = data['cus'][cu_id]
        pilot = cu['pilot']
        slots = cu['slots']
        #name = cu['name']
        #state = cu['state']
        #errno = cu['errno']
        staging_in = cu['StagingInput']
        run = cu['Executing']
        staging_out = cu['StagingOutput']
        end = cu['Done']
        #site = cu['site']

        colors=['yellow', 'green', 'orange']
        hatch = None
        if run == 0:
            run = end
            upload = end
            #colors=['black', 'black', 'black']
            hatch='x'

        for slot in slots:
            print 'pilot: %d' % pilot
            y = pilots[pilot-1] - data['pilots'][str(pilot)]['cores']/2.0 + 0.5 + (slot - 1)
            print 'y: %d' % y

            # TODO: what if execution or upload fails?
            # eb.broken_barh([(download, run-download),
            #                  (run, upload-run),
            #                  (upload, end-upload)], (y-0.4, .8),
            #                  facecolor=colors,
            #                  hatch=hatch, label='CU')
            eb.broken_barh([(staging_in, run-staging_in),
                             (run, staging_out-run),
                             (staging_out, end-staging_out)], (y-.4, .8),
                             facecolor=colors, edgecolors=colors,
                             hatch=hatch, label='CU', color='None')

        #plt.fill(x,np.sin(x),color='blue',alpha=0.5)
        #plt.fill(x,np.sin(x),color='None',alpha=0.5,edgecolor='blue',hatch='/')

    # TaskQueue length
    q_t = []
    q_l = []

    #for t,l in tq:
    for tq in data['queue']:
        t = tq['time']
        l = tq['length']

        q_t.append(t)
        q_l.append(l)

    tq = plt.twinx()
    #ax2.step(q_t, q_l, '--', color='black')
    tq.plot(q_t, q_l, 'r--', color='blue', drawstyle='steps-post', linewidth=2.0, label='CU Queue Length')
    
    tq.ticklabel_format(style='plain')
    tq.set_ylabel('Waiting ComputeUnits')
    tq_y_ax = tq.axes.get_yaxis()
    tq_y_ax.set_major_locator(MaxNLocator(integer=True))

    # Get handles and labels for both eb and tq
    handles, labels = eb.get_legend_handles_labels()
    hl, lb = tq.get_legend_handles_labels()
    handles.extend(hl)
    labels.extend(lb)
    
    # custom proxy artists (for unsupported artists) 
    p = Rectangle((0, 0), 1, 1, fc='red')
    handles.append(p)
    labels.append('CP Queued')

    p = Rectangle((0, 0), 1, 1, fc='Blue')
    handles.append(p)
    labels.append('CP Bootstrapping')

    p = Rectangle((0, 0), 1, 1, fc='yellow')
    handles.append(p)
    labels.append('CU Staging-In')
     
    p = Rectangle((0, 0), 1, 1, fc='green')
    handles.append(p)
    labels.append('CU Execution') 
     
    p = Rectangle((0, 0), 1, 1, fc='orange')
    handles.append(p)
    labels.append('CU Staging-Out')

    p = Rectangle((0, 0), 1, 1, fc='white', hatch='xxx')
    #p = Rectangle((0, 0), 1, 1, fc='black')
    handles.append(p)
    labels.append("CU Failed")

    p = Rectangle((0, 0), 1, 1, fc='LightGrey')
    handles.append(p)
    labels.append('Core Idle')

    # draw the legend 
    eb.legend(handles, labels, loc=1)

    plt.title('ComputePilot Lifetimes with ComputeUnit Queue Length')

    plt.show()

    #fig2 = matplotlib.pyplot.figure(figsize=(8.0, 5.0)) # in inches!
    #plt.savefig('fig.pdf', format='pdf', bbox_inches=(10,5), dpi=600)


def last_cu_done(cus):

    # keep track of the finishing time of the last compute unit
    last = 0

    for cu in cus:
        done = cu[7]
        #done = cu[4]
        last = max(last, done)

    return last

def json_parser(filename):

    with open(filename) as data_file:
        data = json.load(data_file)

    return data


if __name__ == '__main__':

    # Compute Pilots
    #  tuples of (0:cores, 1:new, 2:running, 3:end )
    my_pilot_lifetimes = [
        (1, 1, 2, None),
        (2, 2, 3, 8),
        (3, 3, 4, 8),
        (4, 4, 9, 10)
    ]

    # Compute Units
    # tuplics of (0:pilot, 1:slots, 2:name, 3:cores, 4:state, 5:errno, 6:download, 7:run, 8:upload, 9:end, 10:site)
    my_cus = [
        (0, [0], "cu0", 1, "Done", 0, 2, 4, 6, 7, "stampede"),
        (1, [1], "cu1", 1, "Done", 0, 4, 5, 7, 8, "stampede"),
        (2, [1,2], "cu2", 2, "Done", 0, 5, 6, 8, 9, "stampede"),
        (3, [0,1,2,3], "cu3", 4, "Done", 0, 12,13,16,18, "stampede")
    ]

    # TaskQueue
    # Tuples of (0:Time, 1:Length)
    my_tq = [(0,0), (1,4), (2,3), (3,2), (10,1), (15,0) ]

    data = json_parser('/tmp/results.txt')


    #print my_pilot_lifetimes
    #print my_cus
    #print my_tq

    plot_pilotlifetime(data)
