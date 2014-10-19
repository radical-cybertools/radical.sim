from simpy import Environment
from compute_unit import ComputeUnit
from compute_pilot import ComputePilot
from dci import DCI
from scheduler import Scheduler
from logger import simlog, INFO, ERROR, DEBUG, WARNING, CRITICAL
from version import version, version_detail

def run():


    env = Environment()
    env.cu_state_history = {}

    simlog(INFO, 'radical.sim version: %s (%s)' % (version, version_detail), env)

    stampede = DCI(env, "stampede", 1024)
    archer = DCI(env, "archer", 2048)
    sched = Scheduler(env, "BACK_FILLING")
    pilot1 = ComputePilot(env, stampede, cores=3)
    pilot2 = ComputePilot(env, archer, cores=4)

    sched.add_pilot(pilot1)
    sched.add_pilot(pilot2)

    cu1 = ComputeUnit(env, cores=1)
    sched.submit_cu(cu1)

    cu2 = ComputeUnit(env, cores=2)
    sched.submit_cu(cu2)

    cu3 = ComputeUnit(env, cores=3)
    sched.submit_cu(cu3)

    cu4 = ComputeUnit(env, cores=4)
    sched.submit_cu(cu4)

    env.run(until=1000)

    print("CU state history: %s" % env.cu_state_history)

if __name__ == '__main__':
    run()
