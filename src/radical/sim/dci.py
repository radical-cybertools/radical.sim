from simpy import Container
from errors import ResourceException
from random import gauss
from logger import simlog, INFO
from constants import QUEUEING_MEAN, QUEUING_STD, INITIAL_JOB_ID, \
    DEFAULT_WALLTIME

class DCI(Container):

    _id_counter = INITIAL_JOB_ID

    def __init__(self, env, name, cores):
        self.id = self._id_counter
        DCI._id_counter += 1

        self.name = name
        self.env = env
        super(DCI, self).__init__(env, cores, init=0)
        simlog(INFO, "Initializing DCI '%s' with %d cores." % (
            name, cores), self.env)

    def submit_job(self, job, cores, walltime):

        # Reference to the caller
        self.job = job

        if cores > self.capacity:
            raise ResourceException("Can't get more than capacity allows.")

        if not walltime:
            walltime = DEFAULT_WALLTIME

        queuing_delay = int(gauss(QUEUEING_MEAN, QUEUING_STD))
        if queuing_delay < 0:
            queuing_delay = 0

        simlog(INFO, "Waiting for %d seconds on job request of size %d." % (
            queuing_delay, cores), self.env)
        yield self.env.timeout(queuing_delay)

        simlog(INFO, "Job %d launching on %s with %d cores." % (
            self.id, self.name, cores), self.env)
        yield job.put(cores)

        simlog(INFO, "Job %d will run for %d seconds ..." % (
            self.id, walltime), self.env)
        job = self.env.process(self.run_job(walltime))

        self.env.exit(self.id)

    def run_job(self, walltime):
        yield self.env.timeout(walltime)
        simlog(INFO, "Job %d reached maximum walltime of %d seconds." % (
            self.id, walltime), self.env)
        self.job.agent.interrupt('Walltime')
