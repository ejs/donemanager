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


def chrono_display(timeperiod, actor):
    for day in range(timeperiod-1, -1, -1):
        for t, m in actor.exposed_history(day):
            print "%40s %s %s"%(time.ctime(t), '*' if m.endswith('**') else ' ', m.rstrip('* '))


def grouped_display(timeperiod, source):
    tmp = {}
    key = {}
    for day in range(timeperiod-1, -1, -1):
        for task, tm in groupeddisplay(source.exposed_history(day)):
            k = dmd.clean(task)
            if k not in key:
                key[k] = task
            tmp[k] = tm + tmp.get(k, 0)
    for t in sorted(tmp, key=lambda t:tmp[t], reverse=True):
        task = key[t]
        tm = tmp[t]
        print "% 40s %s %2i:%02i"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', tm/60, tm%60)


def summary_display(timeperiod, days_aimed, hours_aimed, source):
    tmp = {}
    valid = 0
    for day in range(timeperiod-1, -1, -1):
        flag = 0
        for task, tm in groupeddisplay(source.exposed_history(day)):
            flag = 1
            key = dmd.clean(task)
            tmp[key] = tm + tmp.get(key, 0)
        valid += flag

    print "In the last %i days you aimed to work %i days and actually managed %i days"%(timeperiod, days_aimed, valid)
    if days_aimed <= valid:
        print "Well done."
    else:
        print "Leaving you %i days short."%(days_aimed-valid)
    print

    validtime = sum(tmp[task] for task in tmp if not task.endswith('**'))
    wasted  = sum(tmp[task] for task in tmp if task.endswith('**'))
    togo = hours_aimed*60 - validtime
    print "Aimed time   %s"%long_time(hours_aimed*60)
    print "Usefull time %s"%long_time(validtime)
    print "Wasted time  %s"%long_time(wasted)
    if togo > 0:
        print "Only %s to go"%long_time(togo)
    else:
        print "Congratulations. have a rest."

    mostrecent = max(i[0] for day in range(0, timeperiod) for i in source.exposed_history(day))
    age = int(actor.exposed_now() - mostrecent)/60
    print "Time since last action %s ago"%long_time(age)

if __name__ == '__main__':
    from optparse import OptionParser
    settings = actor.exposed_settings
    days_per_week = settings['days_per_week']
    hours_per_day = settings['hours_per_day']
    parser = OptionParser()
    parser.add_option("-d", dest="timeframe", action="store_const", const=(1, 1), default=(1, 1))
    parser.add_option("-w", dest="timeframe", action="store_const", const=(7, days_per_week))
    parser.add_option("-m", dest="timeframe", action="store_const", const=(28, days_per_week*4))
    parser.add_option("-c", action="store_true", dest="chrono", default=False)
    parser.add_option("-g", action="store_true", dest="grouped", default=False)
    parser.add_option("-s", action="store_false", dest="summary", default=True)
    options, args = parser.parse_args()
    if args:
        actor.exposed_log(" ".join(args))
    if options.chrono:
        chrono_display(options.timeframe[0], actor)
        print
    if options.grouped:
        grouped_display(options.timeframe[0], actor)
        print
    if options.summary:
        summary_display(options.timeframe[0], options.timeframe[1], options.timeframe[1]*hours_per_day, actor)
    if args:
        actor.exposed_log(" ".join(args))
