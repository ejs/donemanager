#!/usr/bin/env python
import dmd
import time


try:
    import rpyc
    server = rpyc.connect_by_service('LISTENER')
    actor = server.root
except:
    actor = dmd.ListenerService(None)
    actor.on_connect()


long_time = dmd.long_time
groupeddisplay = dmd.groupeddisplay


def basicdisplay(log, aim):
    """aim is the number of hours that should be worked over this time period."""
    for t, m in log:
        print "%40s %s %s"%(time.ctime(t), '*' if m.endswith('**') else ' ', m.rstrip('* '))
    print ''
    for task, tm in groupeddisplay(log):
        print "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', tm/60, tm%60)
    print ''
    daysummery(log, aim)


def daysummery(log, aim):
    """aim is the number of hours that should be worked over this time period."""
    actions = {}
    for ta, tm in groupeddisplay(log):
       actions[ta] = actions.get(ta, 0) + tm
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))
    wasted  = sum(actions[task] for task in actions if task.endswith('**'))
    mostrecent = max(i[0] for i in log)
    age = int(actor.exposed_now() - mostrecent)/60
    togo = aim*60 - validtime
    print "Usefull time today     %s"%long_time(validtime)
    print "Wasted time            %s"%long_time(wasted)
    if togo > 0:
        print "Only %s to go today"%long_time(togo)
    else:
        print "Congratulations. have a rest."
    print ""
    print "Time since last action %s ago"%long_time(age)


def longsummery(days, workingdays, aim):
    """
        days : the number of days to search back for existing files.
        workingdays : the aimed numner of days to work in this time.
    """
    valid = 0
    actions = {}
    keys = {}
    for day in range(days):
        flag = 0
        for ta, tm in groupeddisplay(actor.exposed_history(day)):
            flag = 1
            k = keys.setdefault(dmd.clean(ta), ta)
            actions[k] = actions.get(k, 0) + tm 
        valid += flag
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))
    wasted  = sum(actions[task] for task in actions if task.endswith('**'))
    togo = min(workingdays, valid)*aim*60 - validtime
    for task in sorted(actions, key=lambda t:actions[t], reverse=True):
        print "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', actions[task]/60, actions[task]%60)
    print "Over the last %i days you worked %i.You are aiming for %i."%(days, valid, workingdays)
    print "Welldone" if valid >= days else "Only %i short"%(workingdays-valid)
    print "Used   time     %s"%long_time(validtime)
    print "Wasted time     %s"%long_time(wasted)
    print "You should have worked %i hours."%(aim*valid, )
    if togo > 0:
        print "Only %s to go (today)."%long_time(togo)
    else:
        print "Congratulations. have a rest."


if __name__ == '__main__':
    import sys
    settings = actor.exposed_settings
    days_per_week = settings['days_per_week']
    hours_per_day = settings['hours_per_day']
    if len(sys.argv) < 2:
        log = [(t, m) for t, m in actor.exposed_history()]
        basicdisplay(log, hours_per_day)
    elif sys.argv[1].startswith('-'):
        if sys.argv[1] == '-s':
            log = [(t, m) for t, m in actor.exposed_history()]
            daysummery(log, hours_per_day)
        if sys.argv[1] == '-w':
            longsummery(7, days_per_week, hours_per_day)
        if sys.argv[1] == '-m':
            longsummery(7*4, days_per_week*4, hours_per_day)
    else:
        actor.exposed_log(" ".join(sys.argv[1:]))
