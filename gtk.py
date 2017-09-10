import gi
gi.require_version('PangoCairo', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, cairo, Pango, PangoCairo, GObject
import math
import pyaudio
import numpy as np
import sys

FIFO = '/tmp/mpd.fifo'
stereo = True
fps = 60
frames_delay=0
queue=[]
for _ in range(frames_delay):
    queue.append([])
m_samples = 44100 // fps
if stereo:
    m_samples *= 2

opacity=0.1

wmclass = 'qmlterm_background'

SAMPLE_MAX = 32767
SAMPLE_RATE = 44100  # [Hz]
SAMPLE_MAX = SAMPLE_RATE

CHANNEL_COUNT = 2
BUFFER_SIZE = 5000 
BUFFER_SIZE = m_samples

def record_pyaudio():
    p = pyaudio.PyAudio()

    stream = p.open(format = pyaudio.paInt16,
                    channels = CHANNEL_COUNT,
                    rate = SAMPLE_RATE,
                    input = True,
                    frames_per_buffer = BUFFER_SIZE)

    def read_data():
        data = np.fromstring(stream.read(stream.get_read_available()), 'int16').astype(float)
        if len(data):
            return data
    return read_data
read_data=record_pyaudio()

class Squareset(Gtk.DrawingArea):
    def __init__(self, upper=9, text=''):
        Gtk.DrawingArea.__init__(self)
        #self.set_size_request(w, h)
        self.fifo = open(FIFO, 'rb')

    def getData(self):
        line = self.fifo.read(m_samples)
        #data = np.frombuffer(line, 'int16').astype(float)
        data = read_data()
        return data
        queue.append(data)
        return queue.pop(0)

    def do_draw_cb(self, widget, cr):
        allo = self.get_allocation()
        w, h = allo.width, allo.height
        data = self.getData()
        fft = np.absolute(np.fft.rfft(data, n=len(data)))
        bins = np.convolve(fft,[0.02]*50)
        cr.set_source_rgba(1, 1, 1, opacity)

        cr.move_to(0, h / 2)  # middle left
        width = 2 * w / len(bins)
        for i, bin in enumerate(bins[:len(bins) // 2]):
            height = h * bin / float(SAMPLE_MAX) / 10
            cr.line_to(i * width, h / 2 - height / 2)
        cr.line_to(w, h / 2)  # middle right
        for i, bin in enumerate(bins[len(bins) // 2:]):
            height = h * bin / float(SAMPLE_MAX) / 10
            cr.line_to(w - i * width, h / 2 + height / 2)
        cr.close_path()
        cr.fill()


def destroy(window):
    Gtk.main_quit()


def tick():
    app.queue_draw()
    return True  # Causes timeout to tick again.


from singleton import Singleton
from threading import Thread
import os
SOCKET_FILE = "/run/user/%s/gtk_visualizer.socket" % os.getuid()
sin = Singleton(SOCKET_FILE)
if sin.start():
    # Thread(target=sin.loop).start()
    window = Gtk.Window()

    win = window
    win.set_app_paintable(True)
    screen = win.get_screen()
    rgba = screen.get_rgba_visual()
    win.set_visual(rgba)
    win.set_wmclass(wmclass, wmclass)
    #win.stick()
    #win.set_keep_below(True)
    win.fullscreen()
    #win.set_accept_focus(False)

    app = Squareset()
    window.add(app)
    app.connect('draw', app.do_draw_cb)
    window.connect_after('destroy', destroy)
    window.show_all()

    GObject.timeout_add(fps, tick)

    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    Gtk.main()
