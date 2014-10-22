from simpy import Interrupt
from errors import ResourceException
from states import NEW, PENDING_LAUNCH, PENDING_ACTIVE, ACTIVE, DONE, CANCELED
from logger import simlog, INFO, DEBUG, WARNING
from constants import AGENT_STARTUP_DELAY, INITIAL_COMPUTE_PILOT_ID, \
    DEFAULT_CORES_PER_PILOT, DEFAULT_WALLTIME, INITIAL_SLOT_ID
from slots import Slot


class ComputePilot(object):

    _id_counter = INITIAL_COMPUTE_PILOT_ID

    def __init__(self, env, dci,
                 cores=DEFAULT_CORES_PER_PILOT, walltime=None):

        # Create a CP Container with requested capacity
        super(ComputePilot, self).__init__(env, capacity=cores)

        # Set unique ID
        self.id = self._id_counter
        ComputePilot._id_counter += 1

        # Link to other entities
        self.dci = dci
        self.env = env

        # Fill the store
        #env.process(self.create_slots(cores))
        self.init = env.process(self.myput(
            range(INITIAL_SLOT_ID, cores+INITIAL_SLOT_ID)))
        #self.create_slots(cores)

        # Some properties
        self.cores = cores
        self.walltime = walltime

        # Record keeping
        self.stats = {}
        self.stats['cores'] = self.cores
        self.stats['walltime'] = self.walltime
        self.env.pilot_stats[self.id] = self.stats

        # Pilot state
        self._state = None
        self.state = NEW

        # TODO: This should probably be triggered by an external process?
        self.state = PENDING_LAUNCH
        self.submission = env.process(self.submit_pilot())
        self.agent = env.process(self.run_pilot())

    @property
    def state(self):
        """I'm the 'state' property."""
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.stats[new_state] = self.env.now

    def submit_pilot(self):

        self.state = PENDING_ACTIVE
        simlog(INFO, "Queuing pilot %d of %d cores on DCI '%s'." %
               (self.id, self.cores, self.dci.name), self.env)
        self.job_id = yield self.env.process(
            self.dci.submit_job(self, self.cores, self.walltime))
        simlog(DEBUG, "Pilot %d launching on '%s' as job %d." %
               (self.id, self.dci.name, self.job_id), self.env)

        # Record the dci for the pilot
        self.stats['dci'] = self.dci.name

    def run_pilot(self):

        # Wait until the submission completed
        yield self.submission

        # NOTE: I don't think RP has a state to denote the state between
        # the "job started and the agent becoming active.

        try:
            yield self.env.timeout(AGENT_STARTUP_DELAY)

            self.state = ACTIVE
            simlog(INFO,"Pilot %d started running on '%s'." %
                (self.id, self.dci.name), self.env)

            if self.walltime:
                yield self.env.timeout(self.walltime)
                self.state = DONE
            else:
                yield self.env.event()
        except Interrupt as i:
            self.state = CANCELED
            simlog(WARNING, "Pilot %d interrupted with '%s'." %
                   (self.id, i.cause), self.env)

    def myput(self, slots):

        # Deal with single entry slots
        if not isinstance(slots, list):
            slots = [slots]

        if len(slots) + len(self.items) > self.capacity:
            raise ResourceException("Can't add (%d) to level (%d) "
                "as it is more than capacity (%d) allows." %
                            (len(slots), len(self.items), self.capacity))

        simlog(DEBUG,"Adding %d cores to the capacity of Pilot %d on %s." %
               (len(slots), self.id, self.dci.name), self.env)

        for slot in slots:
            yield self.put(slot)
            print "after yield put"

        event.succeed()

    def myget(self, amount):

        #simlog(INFO, "Requesting %d cores from the capacity of Pilot %d on %s." %
        #       (amount, self.id, self.dci.name), self.env)

        slots = []
        for _ in range(amount):
            #slot = self.get()
            slot = yield self.get()
            print 'Slot: %s' % slot
            slots.append(slot)

        self.env.exit(slots)
        #return slots
        #TODO: better override this class!
