from simpy.events import AnyOf
from collections import deque
from states import RUNNING
from logger import simlog

class Scheduler(object):
    """BackFilling Scheduler"""

    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.pilots = []
        self.new_cus = deque() # efficient operation on the left of the queue
        self.active_cus = [] # Need a list as an argument to AnyOf

        # Start the run process every time an instance is created.
        self.action = env.process(self.run())

    # run() is a special method
    def run(self):
        simlog.info("Scheduler %s starting." % self.name)

        while True:
            # TODO: check for running pilots

            for pilot in self.pilots:

                if pilot.state != RUNNING:
                    #self.env.timeout(100)
                    continue

                try:
                    cu = self.new_cus.popleft()

                    simlog.debug("Trying to schedule CU %d onto Pilot %d at %d ..." % (cu.id, pilot.id, self.env.now))
                    if cu.cores <= pilot.level:
                        pilot.get(cu.cores)
                        simlog.info("Found pilot %d to schedule CU %d onto at %d." % (pilot.id, cu.id, self.env.now))
                        cu.pilot = pilot
                        self.active_cus.append(self.env.process(cu.run()))
                    else:
                        simlog.warning("Pilot %d has no capacity to schedule CU %d at %d." % (pilot.id, cu.id, self.env.now))
                        # Put it back in the queue
                        self.new_cus.appendleft(cu)

                except IndexError:
                    simlog.debug("No new CUs to process at %d ..." % self.env.now)
                    yield self.env.timeout(100)

            finished = yield AnyOf(self.env, self.active_cus)
            while finished:
                (fin_proc, fin_cu) = finished.popitem()
                self.active_cus.remove(fin_proc)
                fin_cu.pilot.put(fin_cu.cores)

            yield self.env.timeout(100)


    def submit_cu(self, cu):
        self.new_cus.append(cu)

    def add_pilot(self, pilot):
        self.pilots.append(pilot)
