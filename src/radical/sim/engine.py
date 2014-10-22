import json
from simpy import Environment
from compute_unit import ComputeUnit
from compute_pilot import ComputePilot
from dci import DCI
from scheduler import Scheduler
from logger import simlog, INFO, ERROR, DEBUG, WARNING, CRITICAL
from version import version, version_detail

def run():


    env = Environment()
    env.cu_stats = {}
    env.pilot_stats = {}
    env.cu_queue_history = []

    simlog(INFO, 'radical.sim version: %s (%s)' % (version, version_detail), env)

    stampede = DCI(env, "stampede", 1024)
    archer = DCI(env, "archer", 2048)
    sched = Scheduler(env, "BACK_FILLING")
    pilot1 = ComputePilot(env, stampede, cores=3, walltime=600)
    pilot2 = ComputePilot(env, archer, cores=4, walltime=600)

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

    env.run(until=2000)

    from pprint import pprint
    print("CU statistics:")
    pprint(env.cu_stats)
    print("Pilot statistics:")
    pprint(env.pilot_stats)
    print("CU queue history:")
    pprint(env.cu_queue_history)

    data = {}
    data['cus'] = env.cu_stats
    data['pilots'] = env.pilot_stats
    data['queue'] = env.cu_queue_history

    with open('/tmp/results.txt', 'w') as outfile:
        json.dump(data, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

if __name__ == '__main__':
    run()
