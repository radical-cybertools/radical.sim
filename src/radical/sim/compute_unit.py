import simpy
from errors import ResourceException
from logger import simlog, INFO, WARNING, ERROR
from states import NEW, CANCELED, EXECUTING, DONE, FAILED, STAGING_INPUT, STAGING_OUTPUT
from constants import INITIAL_COMPUTE_UNIT_ID, DEFAULT_CORES_PER_CU

class ComputeUnit(object):

    # Class wide counter for CUs
    _id_counter = INITIAL_COMPUTE_UNIT_ID

    def __init__(self, env, cores=DEFAULT_CORES_PER_CU):
        self.id = self._id_counter
        ComputeUnit._id_counter += 1

        self.env = env
        self.cores = cores
        self.pilot = None

        self.stats = {}
        self.stats['cores'] = self.cores
        self.env.cu_stats[self.id] = self.stats

        self._state = None
        self.state = NEW

        simlog(INFO, "Creating ComputeUnit %d." % self.id, self.env)

        # Start the run process every time an instance is created.
        #self.action = env.process(self.run())

        self.cu_reactivate = env.event()

    @property
    def state(self):
        """I'm the 'state' property."""
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.stats[new_state] = self.env.now

    # run() is a special method
    def run(self):

        try:
            try:
                self.state = STAGING_INPUT
                simlog(INFO, 'Staging input for CU %d.' % self.id, self.env)
                yield self.env.timeout(10)

                self.state = EXECUTING
                simlog(INFO, 'Start executing CU %d.' % self.id, self.env)

                exec_duration = 15
                # We yield the process that process() returns
                # to wait for it to finish
                # TODO: Does this need to be a process / function?

                yield self.env.process(self.execute(exec_duration))

                self.state = STAGING_OUTPUT
                simlog(INFO, 'Staging output for CU %d.' % self.id, self.env)
                yield self.env.timeout(20)

                simlog(INFO, 'Execution of CU %d completed.' % self.id, self.env)

            except simpy.Interrupt as i:
                simlog(ERROR, 'Interrupted by %s' % i.cause, self.env)
                self.state = CANCELED

        except Exception as e:
            simlog(ERROR, "Exception in CU Run(): %s" % e.message, self.env)
            self.state = FAILED
            raise e
        else:
            # Release resources
            #req = self.pilot.put(self.cores)  # Return the resources
            self.state = DONE
            self.env.exit(self)

    def execute(self, duration):
        yield self.env.timeout(duration)
