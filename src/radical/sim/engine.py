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

    for _ in range(10):
        pilot = ComputePilot(env, stampede, cores=4, walltime=300)
        sched.add_pilot(pilot)

    for _ in range(100):
        cu = ComputeUnit(env, cores=2)
        sched.submit_cu(cu)

    env.run(until=1000)

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
