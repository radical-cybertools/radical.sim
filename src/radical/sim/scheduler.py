from simpy.events import AnyOf
from collections import deque
from states import ACTIVE, STATE_X
from logger import simlog, INFO, DEBUG, WARNING

SHORT=1

class Scheduler(object):
    """BackFilling Scheduler"""

    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.pilots = []
        self.new_cus = [] # Want to iterate over it
        self.active_cus = [] # Need a list as an argument to AnyOf

        simlog(INFO, "Intitializing scheduler %s." % self.name, self.env)

        # Start the run process every time an instance is created.
        self.action = env.process(self.run())

    def run(self):
        simlog(INFO, "Scheduler %s starting." % self.name, self.env)

        while True:
            for pilot in self.pilots:
                if pilot.state != ACTIVE:
                    # Don't try to run on inactive pilots
                    yield self.env.timeout(SHORT) # Need this yield
                    continue

                # if not pilot.slots.items:
                #     simlog(WARNING, "Pilot %d has no free slots, skipping this iteration." % pilot.id, self.env)
                #     yield self.env.timeout(SHORT)
                #     continue

                activated_cus = []
                for cu in self.new_cus:
                    simlog(DEBUG, "Trying to schedule CU %d onto Pilot %d ..." % (cu.id, pilot.id), self.env)
                    if cu.cores <= len(pilot.slots.items):
                        simlog(INFO, "Found pilot %d to schedule CU %d onto." % (pilot.id, cu.id), self.env)
                        cu.pilot = pilot
                        cu.stats['pilot'] = pilot.id
                        cu.slots = yield pilot.get(cu.cores)
                        cu.stats['slots'] = cu.slots

                        activated_cus.append(cu)
                        self.active_cus.append(self.env.process(cu.run()))

                    elif cu.cores <= pilot.slots.capacity:
                        simlog(WARNING, "Pilot %d has not enough free slots to schedule CU %d." % (pilot.id, cu.id), self.env)
                    else:
                        simlog(WARNING, "Pilot %d has not enough capacity to (ever) schedule CU %d." % (pilot.id, cu.id), self.env)

                self.new_cus[:] = [cu for cu in self.new_cus if cu not in activated_cus]
                self.env.cu_queue_history.append({'time': self.env.now, 'length': len(self.new_cus)})

            # Check for finished after looped over all pilots
            #finished = yield AnyOf(self.env, self.active_cus)
            #finished = yield AnyOf(self.env, self.active_cus+[self.env.timeout(2, 'timeout')])
            #while finished:
            finished = [cu for cu in self.active_cus if cu.processed]
            for f in finished:
                #(fin_proc, fin_cu) = finished.popitem()
                fin_cu = yield f
                #if fin_proc in self.active_cus:
                self.active_cus.remove(f)
                fin_cu.pilot.put(fin_cu.slots)

        # This yield is good!
        yield self.env.timeout(SHORT)

    def submit_cu(self, cu):
        self.new_cus.append(cu)
        cu.state = STATE_X

    def add_pilot(self, pilot):
        self.pilots.append(pilot)
