from simpy.events import AnyOf
from collections import deque
from states import ACTIVE, STATE_X
from logger import simlog, INFO, DEBUG, WARNING

class Scheduler(object):
    """BackFilling Scheduler"""

    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.pilots = []
        self.new_cus = deque() # efficient operation on the left of the queue
        self.active_cus = [] # Need a list as an argument to AnyOf

        simlog(INFO, "Intitializing scheduler %s." % self.name, self.env)

        # Start the run process every time an instance is created.
        self.action = env.process(self.run())

    # run() is a special method
    def run(self):
        simlog(INFO, "Scheduler %s starting." % self.name, self.env)

        while True:
            # TODO: check for running pilots

            for pilot in self.pilots:

                if pilot.state != ACTIVE:
                    #self.env.timeout(100)
                    continue

                try:
                    cu = self.new_cus.popleft()

                    simlog(DEBUG, "Trying to schedule CU %d onto Pilot %d ..." % (
                        cu.id, pilot.id), self.env)
                    if cu.cores <= pilot.level:
                        pilot.get(cu.cores)
                        simlog(INFO, "Found pilot %d to schedule CU %d onto." % (
                            pilot.id, cu.id), self.env)
                        cu.pilot = pilot
                        self.active_cus.append(self.env.process(cu.run()))
                    else:
                        simlog(WARNING, "Pilot %d has no capacity to schedule CU %d." % (
                            pilot.id, cu.id), self.env)
                        # Put it back in the queue
                        self.new_cus.appendleft(cu)

                except IndexError:
                    simlog(DEBUG, "No new CUs to process ...", self.env)
                    yield self.env.timeout(100)

            finished = yield AnyOf(self.env, self.active_cus)
            while finished:
                (fin_proc, fin_cu) = finished.popitem()
                self.active_cus.remove(fin_proc)
                fin_cu.pilot.put(fin_cu.cores)
                self.env.cu_state_history[fin_cu.id] = fin_cu.state_history

            yield self.env.timeout(100)


    def submit_cu(self, cu):
        self.new_cus.append(cu)
        cu.state = STATE_X

    def add_pilot(self, pilot):
        self.pilots.append(pilot)
