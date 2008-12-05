#!/usr/bin/env python
import dmd
import time


try:
    import rpyc
    actor = rpyc.connect_by_service('LISTENER').root
except:
    print "Using local service"
    actor = dmd.ListenerService(None)


def long_time(t):
    h, m = t//60, t%60
    result = ''
    for number, singular, plural in ((t//60, 'hour ', 'hours'), (t%60, 'minute ', 'minutes')):
        if number:
            result += "%2i %s "%(number, singular if number == 1 else plural)
    return result or 'none'


def chrono_display(timeperiod, actor):
    for t, m in actor.exposed_history(range(timeperiod-1, -1, -1)):
        print "%40s %s %s"%(time.ctime(t), '*' if m.endswith('**') else ' ', m.rstrip('* '))


def grouped_display(timeperiod, source):
    tmp = dict(source.exposed_grouped(range(timeperiod)))
    for task in sorted(tmp, key=lambda t:tmp[t], reverse=True):
        tm = tmp[task]
        print "% 40s %s %s"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', long_time(tm))


def summary_display(timeperiod, days_aimed, hours_aimed, source):
    tmp = dict(source.exposed_grouped(range(timeperiod)))
    valid = len([i for i in range(timeperiod) if source.exposed_log_exists(i)])

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

    mostrecent = max(tm for tm, _ in source.exposed_history(range(timeperiod)))
    age = int(actor.exposed_now() - mostrecent)/60
    print
    print "Time since last action : %s"%long_time(age)


def task_display(timeperiod, high, source):
    log = dict(source.exposed_grouped(range(timeperiod)))
    target = source.exposed_aim(timeperiod, high)
    for l in target:
        cl = dmd.clean(l)
        if cl in log:
            if target[l][0] and log[cl] < target[l][0]:
                print "To little time spent on %s (%s should be at least %s)"%(l, long_time(log[cl]), long_time(target[l][0]))
            elif target[l][1] and log[cl] > target[l][1]:
                print "To  much  time spent on %s (%s should be at most %s)"%(l, long_time(log[cl]), long_time(target[l][1]))
        elif target[l][0]:
            print "You should spend some time on %s (aiming for at least %s)"%(l, long_time(target[l][0]))


if __name__ == '__main__':
    from optparse import OptionParser
    settings = actor.exposed_settings
    days = settings['days_per_week']

    parser = OptionParser()
    parser.add_option("-d", dest="timeframe", action="store_const", const=(1, 1), default=(1, 1))
    parser.add_option("-w", dest="timeframe", action="store_const", const=(7, days))
    parser.add_option("-m", dest="timeframe", action="store_const", const=(28, days*4))
    parser.add_option("-c", action="store_true", dest="chrono", default=False)
    parser.add_option("-g", action="store_true", dest="grouped", default=False)
    parser.add_option("-s", action="store_true", dest="summary", default=False)
    parser.add_option("-t", action="store_true", dest="tasks", default=False)

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
        summary_display(options.timeframe[0], options.timeframe[1], options.timeframe[1]*settings['hours_per_day'], actor)
        print
    if options.tasks:
        task_display(options.timeframe[0], options.timeframe[1], actor)
