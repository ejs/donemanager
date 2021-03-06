#!/usr/bin/env python
import dmd
import time


try:
    import rpyc
    tmp = rpyc.connect_by_service('LISTENER')
    actor = tmp.root
except:
    print "Using local service"
    actor = dmd.ListenerService(None)


def long_time(t):
    result = ''
    for number, singular, plural in ((t//60, 'hour ', 'hours'), (t%60, 'minute ', 'minutes')):
        if number:
            result += "%2i %s "%(number, singular if number == 1 else plural)
    return result or 'none'


def chrono_display((timeperiod, _, __), actor):
    for t, m in actor.exposed_history(range(timeperiod-1, -1, -1)):
        print "%40s %s %s"%(time.ctime(t), '*' if m.endswith('**') else ' ', m.rstrip('* '))


def grouped_display((timeperiod, _, __), source):
    data = list(source.exposed_grouped(range(timeperiod)))
    for task, tm in sorted(data, key=lambda t:t[1], reverse=True):
        print "% 40s %s %s"%(task.rstrip('* '), '*' if task.endswith('**') else ' ', long_time(tm))


def summary_display((timeperiod, high, hours_aimed), source):
    valid = len([i for i in range(timeperiod) if source.exposed_log_exists(i)])
    print "In the last %i days you aimed to work %i days and managed %i days"%(timeperiod, high, valid)
    if high <= valid:
        print "Well done."
    else:
        print "Leaving you %i days short."%(high-valid)
    print

    tmp = list(source.exposed_grouped(range(timeperiod)))
    validtime = sum(tm for task, tm in tmp if not task.endswith('**'))
    wasted  = sum(tm for task, tm in tmp if task.endswith('**'))
    togo = hours_aimed*60 - validtime
    print "Aimed time   %s"%long_time(hours_aimed*60)
    print "Usefull time %s"%long_time(validtime)
    print "Wasted time  %s"%long_time(wasted)
    if togo > 0:
        print "Only %s to go"%long_time(togo)
    else:
        print "Congratulations. have a rest."

    mostrecent = max(tm for tm, _ in source.exposed_history(range(timeperiod)))
    age = (actor.exposed_now() - mostrecent)//60
    print
    print "Time since last action : %s"%long_time(age)


def task_display((timeperiod, high, _), source):
    log = dict((dmd.clean(n), t) for n, t in source.exposed_grouped(range(timeperiod)))
    target = source.exposed_aim(timeperiod, high)
    for l in target:
        cl = dmd.clean(l)
        if cl in log:
            if target[l][0] and log[cl] < target[l][0]:
                print "To little time spent on %s (%s should be at least %s)"%(l, long_time(log[cl]), long_time(target[l][0]))
            elif target[l][1] and log[cl] > target[l][1]:
                print "To  much  time spent on %s (%s should be at most  %s)"%(l, long_time(log[cl]), long_time(target[l][1]))
        elif target[l][0]:
            print "You should spend some time on %s (aiming for at least %s)"%(l, long_time(target[l][0]))


if __name__ == '__main__':
    from optparse import OptionParser
    settings = actor.exposed_settings
    days = settings['days_per_week']
    hours = settings['hours_per_day']

    parser = OptionParser()
    parser.add_option("-d", action="store_const", dest="timeframe", const=(1, 1, hours), default=(1, 1, hours))
    parser.add_option("-w", action="store_const", dest="timeframe", const=(7, days, hours*days))
    parser.add_option("-m", action="store_const", dest="timeframe", const=(28, days*4, hours*days*4))
    parser.add_option("-b", action="store_true", dest="slack", default=False)
    parser.add_option("-c", action="append_const", dest="actions", const=chrono_display, default=[])
    parser.add_option("-g", action="append_const", dest="actions", const=grouped_display)
    parser.add_option("-s", action="append_const", dest="actions", const=summary_display)
    parser.add_option("-t", action="append_const", dest="actions", const=task_display)

    options, args = parser.parse_args()
    if args:
        actor.exposed_log("%s %s"%(" ".join(args), "**" if options.slack else ""))
    elif options.slack:
        actor.exposed_log("break **")

    for method in options.actions:
        print
        method(options.timeframe, actor)
