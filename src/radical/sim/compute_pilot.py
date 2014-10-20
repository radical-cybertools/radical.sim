from simpy import Container
from errors import ResourceException
from states import NEW, PENDING_LAUNCH, PENDING_ACTIVE, ACTIVE
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

        self.state_history = {}
        self._state = None
        self.state = NEW

        # TODO: This should probably be triggered by an external process
        self.state = PENDING_LAUNCH
        env.process(self.launch_pilot())

    @property
    def state(self):
        """I'm the 'state' property."""
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.state_history[new_state] = self.env.now

    def launch_pilot(self):

        self.state = PENDING_ACTIVE
        simlog(INFO, "Queuing pilot %d of %d cores on DCI '%s'." %
               (self.id, self.cores, self.dci.name), self.env)
        yield self.env.process(self.dci.submit_job(self, self.cores))

        # NOTE: I don't think RP has a state to denote the state between
        # the "job started and the agent becoming active.

        simlog(DEBUG, "Pilot %d launching on '%s' at %d." %
               (self.id, self.dci.name, self.env.now), self.env)
        yield self.env.timeout(AGENT_STARTUP_DELAY)

        self.state = ACTIVE
        simlog(INFO,"Pilot %d started running on '%s' at %d." %
               (self.id, self.dci.name, self.env.now), self.env)


        self.env.pilot_state_history[self.id] = self.state_history

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
