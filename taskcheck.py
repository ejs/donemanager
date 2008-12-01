#!/usr/bin/env python
import dmd


try:
    import rpyc
    server = rpyc.connect_by_service('LISTENER')
    actor = server.root
except:
    actor = dmd.ListenerService(None)
    actor.on_connect()


def summery(period):
    actions = {}
    keys = {}
    for day in range(period):
        flag = 0
        for ta, tm in dmd.groupeddisplay(actor.exposed_history(day)):
            flag = 1
            k = keys.setdefault(dmd.clean(ta), ta)
            actions[k] = actions.get(k, 0) + tm 
    return actions
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))


def agedfile(age):
    return actor.exposed_log_exists(age)


def aim(period, high):
    def convert(s):
        if s == '-':
            return 0
        else:
            a, b = s.split(':')
            return int(a)*60+int(b)

    active = sum(1 for i in range(period) if agedfile(i))
    active = min(active, high)
    source = actor.exposed_file('/caps.txt', 'r')
    caps = ((s.strip() for s in l.split('\t')) for l in source if l[0] != '#')
    caps = dict((a, [active*convert(b), active*convert(c)]) for a, b, c in caps)
    # add check that the low point is below the high point
    return caps


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2  or sys.argv[1] == '-d':
        log = summery(1)
        target = aim(1, 1)
    elif sys.argv[1] == '-w':
        log = summery(7)
        target = aim(7, 5)
    elif sys.argv[1] == '-m':
        log = summery(7*4)
        target = aim(7*4, 5*4)
    log = dict((dmd.clean(n), log[n]) for n in log)
    for l in target:
        cl = dmd.clean(l)
        if cl in log:
            if target[l][0] and log[cl] < target[l][0]:
                print "To little time spent on %s (%s should be at least %s)"%(l, dmd.long_time(log[cl]), dmd.long_time(target[l][0]))
            elif target[l][1] and log[cl] > target[l][1]:
                print "To  much  time spent on %s (%s should be at most %s)"%(l, dmd.long_time(log[cl]), dmd.long_time(target[l][1]))
        elif target[l][0]:
            print "You should spend some time on %s (aiming for at least %s)"%(l, dmd.long_time(target[l][0]))
