import simpy
from errors import ResourceException
from logger import simlog

class ComputeUnit(object):

    _id_counter = 1

    def __init__(self, env, cores=1):
        self.id = self._id_counter
        ComputeUnit._id_counter += 1

        self.env = env
        self.cores = cores
        self.pilot = None

        simlog.info("Creating ComputeUnit %d." % self.id)

        # Start the run process every time an instance is created.
        #self.action = env.process(self.run())

        self.cu_reactivate = env.event()


    # run() is a special method
    def run(self):

        try:
            # Register the walltime interrupter
            #self.env.process(self.walltime(60))

            simlog.info('Start executing CU %d at %d' % (self.id, self.env.now))

            exec_duration = 15
            # We yield the process that process() returns
            # to wait for it to finish
            try:
                yield self.env.process(self.execute(exec_duration))
            except simpy.Interrupt as i:
                simlog.error('Interrupted at %d by %s' % (self.env.now, i.cause))
                return

            simlog.info('Execution of CU %d completed at %d' % (self.id, self.env.now))
        except ResourceException as e:
            simlog.warning("Couldn't get resource, ignoring ...")
        except Exception as e:
            simlog.error("Exception in CU Run(): %s" % e.message)
            raise e
        else:
            # Release resources
            #req = self.pilot.put(self.cores)  # Return the resources
            self.env.exit(self)

    def execute(self, duration):
        yield self.env.timeout(duration)

    # def walltime(self, duration):
    #     yield self.env.timeout(duration)
    #     try:
    #         self.action.interrupt('Walltime reached!')
    #     except Exception as e:
    #         # TODO: better exception handling
    #         print('Warning: %s' % e.message)
