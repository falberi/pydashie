from samplers.github import *

def run(app, xyzzy):
    samplers = [
        ContributorsSampler(xyzzy, 60),
        ParticipationSampler(xyzzy, 60),
        CommentsSampler(xyzzy, 60),
    ]

    print "Triggering initial sampling for %d samplers" % len(samplers)
    for (i, sampler) in enumerate(samplers):
        sampler._sample()

    try:
        app.run(debug=True,
                host="0.0.0.0",
                port=5000,
                threaded=True,
                use_reloader=False,
                use_debugger=True
                )
    finally:
        print "Disconnecting clients"
        xyzzy.stopped = True

        print "Stopping %d timers" % len(samplers)
        for (i, sampler) in enumerate(samplers):
            sampler.stop()

    print "Done"
