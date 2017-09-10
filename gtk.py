import gi
gi.require_version('PangoCairo', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, cairo, Pango, PangoCairo, GObject
import math
import numpy as np
import sys

FIFO = '/tmp/mpd.fifo'
stereo = True
fps = 25
w, h = 1920, 1080
m_samples = 44100 // fps
if stereo:
    m_samples *= 2

SAMPLE_MAX = 32767
SAMPLE_RATE = 44100  # [Hz]
SAMPLE_MAX = SAMPLE_RATE


class Squareset(Gtk.DrawingArea):
    def __init__(self, upper=9, text=''):
        Gtk.DrawingArea.__init__(self)
        self.set_size_request(w, h)
        self.fifo = open(FIFO, 'rb')

    def getData(self):
        line = self.fifo.read(m_samples)
        data = np.frombuffer(line, 'int16').astype(float)
        return data

    def do_draw_cb(self, widget, cr):
        data = self.getData()
        fft = np.absolute(np.fft.rfft(data, n=len(data)))
        bins = fft
        cr.set_source_rgba(1, 1, 1, 0.1)

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


window = Gtk.Window()

win = window
win.set_app_paintable(True)
screen = win.get_screen()
rgba = screen.get_rgba_visual()
win.set_visual(rgba)
wmclass = 'qmlterm_background'
win.set_wmclass(wmclass, wmclass)
win.stick()
win.set_keep_below(True)
win.fullscreen()
win.set_accept_focus(False)

app = Squareset()
window.add(app)
app.connect('draw', app.do_draw_cb)
window.connect_after('destroy', destroy)
window.show_all()

GObject.timeout_add(fps, tick)


import setproctitle
setproctitle.setproctitle("background-visualizer")
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

Gtk.main()
