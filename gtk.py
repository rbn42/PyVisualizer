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
frames_delay = 0
m_samples = 44100 // fps
if stereo:
    m_samples *= 2

opacity = 0.1

wmclass = 'qmlterm_background'

SAMPLE_MAX = 32767
SAMPLE_RATE = 44100  # [Hz]
SAMPLE_MAX = SAMPLE_RATE

CHANNEL_COUNT = 2
BUFFER_SIZE = 5000
BUFFER_SIZE = m_samples


def record_mpd():
    fifo = open(FIFO, 'rb')
    queue = []
    for _ in range(frames_delay):
        queue.append([])

    while True:
        line = fifo.read(m_samples)
        queue.append(data)
        yield queue.pop(0)


def record_pyaudio():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNEL_COUNT,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=BUFFER_SIZE)

    while True:
        data = np.fromstring(stream.read(
            stream.get_read_available()), 'int16')
        if len(data):
            yield data


read_data = record_pyaudio()

kernel=list(range(1,20))+list(range(20,1,-1))
kernel=np.asarray(kernel)
kernel=kernel/sum(kernel)

class Squareset(Gtk.DrawingArea):
    def do_draw_cb(self, widget, cr):
        alloc = self.get_allocation()
        w, h = alloc.width, alloc.height
        data = next(read_data)
        fft = np.absolute(np.fft.rfft(data, n=len(data)))
        bins = np.convolve(fft, kernel,'valid')
        cr.set_source_rgba(1, 1, 1, opacity)

        reverse=True
        if reverse:
            cr.move_to(0, 0) 
            width = 2 * w / len(bins)
            for i, bin in enumerate(bins[:len(bins) // 2]):
                height = h * bin / float(SAMPLE_MAX) / 10
                cr.line_to(i * width, h / 2 - height / 2)
            cr.line_to(w,  0)
            cr.close_path()

            cr.move_to(w, h )
            for i, bin in enumerate(bins[len(bins) // 2:]):
                height = h * bin / float(SAMPLE_MAX) / 10
                cr.line_to(w - i * width, h / 2 + height / 2)
            cr.line_to(0,  h)
            cr.close_path()
        else:
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
    # win.stick()
    # win.set_keep_below(True)
    win.fullscreen()
    # win.set_accept_focus(False)

    app = Squareset()
    window.add(app)
    app.connect('draw', app.do_draw_cb)
    window.connect_after('destroy', destroy)
    window.show_all()

    GObject.timeout_add(fps, tick)

    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    Gtk.main()
