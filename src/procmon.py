#!/usr/bin/env python
'''
Script to monitor the mem consumption of some python processes.
'''
#USER       PID  %CPU %MEM      VSZ    RSS   TT  STAT STARTED      TIME COMMAND
#brandonh 91871   0.0  0.0  2435120    536 s001  R+    2:21PM   0:00.00 grep pyth
from subprocess import Popen, call, PIPE
import time

PROCESS_STR = 'python ./generate.py'

# last PID seen matching string
lastpid = None
pids = set()
maxmem = 0.0

while True:
    output = Popen(["ps", "aux"], stdout=PIPE).communicate()[0]
    memtotal = 0.0
    pyprocs = 0.0
    newpids = set()
    for line in output.split('\n'):
        found = False
        pid = None
        mem = None
        if PROCESS_STR in line:
            split = line.split(" ")
            split = [s for s in split if s != '']
            pid = split[1]
            mem = split[3]
            if pid not in newpids:
                newpids.add(pid)
            try:
                memtotal += float(mem)
            except ValueError:
                print "couldn't convert float: %s" % mem
            found = True
        if 'python' in line:
            pyprocs += 1
    if memtotal > 0.0:
        print "%s %s" % (memtotal, pyprocs)
    if memtotal > maxmem:
        maxmem = memtotal

    if pids != newpids:
        pids = newpids
        print "**** maxmem: %s" % maxmem
        #print "****   pids: %s" % pids
        maxmem = 0.0

    time.sleep(1.0)
