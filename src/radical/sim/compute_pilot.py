from simpy import Container
from errors import ResourceException
from states import NEW, RUNNING, DONE
from logger import simlog, INFO, DEBUG
from constants import AGENT_STARTUP_DELAY

class ComputePilot(Container):

    _id_counter = 1

    def __init__(self, env, dci, cores=1):
        # Create a CP Container with requested capacity and initial level=0
        super(ComputePilot, self).__init__(env, capacity=cores, init=0)

        # ID
        self.id = self._id_counter
        ComputePilot._id_counter += 1

        self.dci = dci
        self.cores = cores
        self.env = env
        self.state = NEW

        env.process(self.launch_pilot())

    def launch_pilot(self):

        simlog(INFO, "Queuing pilot %d of %d cores on DCI '%s'." %
               (self.id, self.cores, self.dci.name), self.env)
        yield self.env.process(self.dci.submit_job(self, self.cores))

        simlog(DEBUG, "Pilot %d launching on '%s' at %d." %
               (self.id, self.dci.name, self.env.now), self.env)
        yield self.env.timeout(AGENT_STARTUP_DELAY)

        self.state = RUNNING
        simlog(INFO,"Pilot %d started running on '%s' at %d." %
               (self.id, self.dci.name, self.env.now), self.env)


    def put(self, amount):
        if amount + self.level > self.capacity:
            raise ResourceException("Can't add (%d) to level (%d) "
                "as it is more than capacity (%d) allows." %
                            (amount, self.level, self.capacity))

        simlog(DEBUG,"Adding %d cores to the capacity of Pilot %d on %s." %
               (amount, self.id, self.dci.name), self.env)
        return super(ComputePilot, self).put(amount)

    def get(self, amount):
        if amount > self.capacity:
            raise ResourceException("Can't get more than capacity allows.")

        simlog(INFO, "Requesting %d cores from the capacity of Pilot %d on %s." %
               (amount, self.id, self.dci.name), self.env)
        return super(ComputePilot, self).get(amount)
