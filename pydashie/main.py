import os
import logging
from flask import Flask, render_template, Response, send_from_directory, request, current_app

app = Flask(__name__)
logging.basicConfig()
log = logging.getLogger(__name__)

import sys
reload(sys)
sys.setdefaultencoding('UTF8')

@app.route("/")
def main():
    return render_template('main.html', title='pyDashie')

@app.route("/dashboard/<dashlayout>/")
def custom_layout(dashlayout):
    return render_template('%s.html'%dashlayout, title='pyDashie')

@app.route("/assets/application.js")
def javascripts():
    if not hasattr(current_app, 'javascripts'):
        import coffeescript
        scripts = [
            'assets/javascripts/jquery.js',
            'assets/javascripts/es5-shim.js',
            'assets/javascripts/d3.v2.min.js',

            'assets/javascripts/batman.js',
            'assets/javascripts/batman.jquery.js',

            'assets/javascripts/jquery.gridster.js',
            'assets/javascripts/jquery.leanModal.min.js',

            'assets/javascripts/dashing.coffee',
            'assets/javascripts/dashing.gridster.coffee',

            'assets/javascripts/jquery.knob.js',
            'assets/javascripts/rickshaw.min.js',

            'assets/javascripts/application.coffee',

            'widgets/clock/clock.coffee',
            'widgets/comments/comments.coffee',
            'widgets/graph/graph.coffee',
            'widgets/iframe/iframe.coffee',
            'widgets/image/image.coffee',
            'widgets/list/list.coffee',
            'widgets/meter/meter.coffee',
            'widgets/number/number.coffee',
            'widgets/text/text.coffee',
        ]

        output = []
        for path in scripts:
            output.append('// JS: %s\n' % path)
            if '.coffee' in path:
                log.info('Compiling Coffee for %s ' % path)
                contents = coffeescript.compile_file(path)
            else:
                f = open(path)
                contents = f.read()
                f.close()

            output.append(contents)

        current_app.javascripts = output

    return Response(current_app.javascripts, mimetype='application/javascript')

@app.route('/assets/application.css')
def application_css():
    if not hasattr(current_app, 'stylesheets'):
        from scss import Scss
        scripts = [
            'assets/stylesheets/font-awesome.css',
            'assets/stylesheets/jquery.gridster.css',
            'assets/stylesheets/application.scss',
            'widgets/clock/clock.scss',
            'widgets/comments/comments.scss',
            'widgets/graph/graph.scss',
            'widgets/iframe/iframe.scss',
            'widgets/image/image.scss',
            'widgets/list/list.scss',
            'widgets/meter/meter.scss',
            'widgets/number/number.scss',
            'widgets/text/text.scss',
        ]

        output = []
        for path in scripts:
            output.append('/* CSS: %s */\n' % path)
            if '.scss' in path:
                log.info('Compiling Scss for %s ' % path)
                css = Scss()
                contents = css.compile(open(path).read())
            else:
                f = open(path)
                contents = f.read()
                f.close()

            output.append(contents)

        current_app.stylesheets = output

    return Response(current_app.stylesheets, mimetype='text/css')

@app.route('/assets/images/<path:filename>')
def send_static_img(filename):
    directory = os.path.join('assets', 'images')
    return send_from_directory(directory, filename)

@app.route('/views/<widget_name>.html')
def widget_html(widget_name):
    html = '%s.html' % widget_name
    path = os.path.join('widgets', widget_name, html)
    if os.path.isfile(path):
        f = open(path)
        contents = f.read()
        f.close()
        return contents

import Queue

class Z:
    pass
xyzzy = Z()
xyzzy.events_queue = {}
xyzzy.last_events = {}
xyzzy.using_events = True
xyzzy.MAX_QUEUE_LENGTH = 20
xyzzy.stopped = False

@app.route('/events')
def events():
    if xyzzy.using_events:
        event_stream_port = request.environ['REMOTE_PORT']
        current_event_queue = Queue.Queue()
        xyzzy.events_queue[event_stream_port] = current_event_queue
        current_app.logger.info('New Client %s connected. Total Clients: %s' %
                                (event_stream_port, len(xyzzy.events_queue)))

        #Start the newly connected client off by pushing the current last events
        for event in xyzzy.last_events.values():
            current_event_queue.put(event)
        return Response(pop_queue(current_event_queue), mimetype='text/event-stream')

    return Response(xyzzy.last_events.values(), mimetype='text/event-stream')

def pop_queue(current_event_queue):
    while not xyzzy.stopped:
        try:
            data = current_event_queue.get(timeout=0.1)
            yield data
        except Queue.Empty:
            #this makes the server quit nicely - previously the queue threads would block and never exit. This makes it keep checking for dead application
            pass

def purge_streams():
    big_queues = [port for port, queue in xyzzy.events_queue if len(queue) > xyzzy.MAX_QUEUE_LENGTH]
    for big_queue in big_queues:
        current_app.logger.info('Client %s is stale. Disconnecting. Total Clients: %s' %
                                (big_queue, len(xyzzy.events_queue)))
        del queue[big_queue]

def close_stream(*args, **kwargs):
    event_stream_port = args[2][1]
    del xyzzy.events_queue[event_stream_port]
    log.info('Client %s disconnected. Total Clients: %s' % (event_stream_port, len(xyzzy.events_queue)))


def run_sample_app():
    import SocketServer
    SocketServer.BaseServer.handle_error = close_stream
    import example_app
    example_app.run(app, xyzzy)

def run_app():
    import SocketServer
    SocketServer.BaseServer.handle_error = close_stream
    import my_app
    my_app.run(app, xyzzy)

if __name__ == "__main__":
    run_app()
