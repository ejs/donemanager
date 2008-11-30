#!/usr/bin/env python
import time


try:
    import rpyc
    server = rpyc.connect_by_service('LISTENER')
    actor = server.root
except:
    import dmd
    actor = dmd.ListenerService(None)
    actor.on_connect()


def clean(s):
    return ''.join(c for c in s.lower() if c.isalnum())


def long_time(t):
    if t < 60:
        return '%i minutes'%t
    elif not t%60:
        return '%i hours'%(t/60)
    else:
        return '%i hours %i minutes'%(t/60, t%60)


def groupeddisplay(log):
    totals = {}
    keys = {}
    last = None
    for t, m in log:
        if last:
            k = keys.setdefault(clean(m), m)
            totals[k] = totals.get(k, 0) + t - last
        last = t
    for task in sorted(totals, key=(lambda k:totals[k]), reverse=True):
        tt = int(totals[task]/60)
        yield task, tt


def basicdisplay(log, aim):
    """aim is the number of hours that should be worked over this time period."""
    for t, m in log:
        yield "%40s %s %s"%(time.ctime(t), '*' if m.endswith('**') else ' ', m.rstrip('* '))
    yield ''
    for task, tm in groupeddisplay(log):
        yield "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', tm/60, tm%60)
    yield ''
    for line in daysummery(log, aim):
        yield line


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
    yield "Usefull time today     %s"%long_time(validtime)
    yield "Wasted time            %s"%long_time(wasted)
    if togo > 0:
        yield "Only %s to go today"%long_time(togo)
    else:
        yield "Congratulations. have a rest."
    yield ''
    yield "Time since last action %s ago"%long_time(age)


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
            k = keys.setdefault(clean(ta), ta)
            actions[k] = actions.get(k, 0) + tm 
        valid += flag
    validtime = sum(actions[task] for task in actions if not task.endswith('**'))
    wasted  = sum(actions[task] for task in actions if task.endswith('**'))
    togo = min(workingdays, valid)*aim*60 - validtime
    for task in sorted(actions, key=lambda t:actions[t], reverse=True):
        yield "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', actions[task]/60, actions[task]%60)
    yield "Over the last %i days you worked %i.You are aiming for %i."%(days, valid, workingdays)
    yield "Welldone" if valid >= days else "Only %i short"%(workingdays-valid)
    yield "Used   time     %s"%long_time(validtime)
    yield "Wasted time     %s"%long_time(wasted)
    yield "You should have worked %i hours."%(aim*valid, )
    if togo > 0:
        yield "Only %s to go (today)."%long_time(togo)
    else:
        yield "Congratulations. have a rest."


if __name__ == '__main__':
    import sys
    settings = actor.exposed_settings
    if len(sys.argv) < 2:
        log = [(t, m) for t, m in actor.exposed_history()]
        for line in basicdisplay(log, settings['hours_per_day']):
            print line
    elif sys.argv[1].startswith('-'):
        if sys.argv[1] == '-s':
            log = [(t, m) for t, m in actor.exposed_history()]
            for line in daysummery(log, settings['hours_per_day']):
                print line
        if sys.argv[1] == '-w':
            for line in longsummery(7, settings['days_per_week'], settings['hours_per_day']):
                print line
        if sys.argv[1] == '-m':
            for line in longsummery(7*4, settings['days_per_week']*4, settings['hours_per_day']):
                print line
    else:
        actor.exposed_log(" ".join(sys.argv[1:]))
