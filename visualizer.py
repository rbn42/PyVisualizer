"""Module that contains visualizer classes."""

import sys
import random
import time

import numpy as np
from PySide import QtCore, QtGui

SAMPLE_MAX = 32767
SAMPLE_RATE = 44100  # [Hz]
SAMPLE_MAX = SAMPLE_RATE


class Visualizer(QtGui.QLabel):
    """The base class for visualizers.

    When initializing a visualizer, you must provide a get_data function which
    takes no arguments and returns a NumPy array of PCM samples that will be
    called exactly once each time a frame is drawn.

    Note: Although this is an abstract class, it cannot have a metaclass of
    abcmeta since it is a child of QObject.
    """

    def __init__(self, get_data, update_interval=33):
        super(Visualizer, self).__init__()
        self.setStyleSheet('background-color: black;');
        self.setWindowTitle('PyVisualizer')
        self.img = QtGui.QImage(1920, 1080,
                                QtGui.QImage.Format_ARGB32)

    def refresh(self, data):
        """Generate a frame, display it, and set queue the next frame"""
        if data is not None:
            self.setPixmap(QtGui.QPixmap.fromImage(self.generate(data)))


class Spectrogram(Visualizer):
    def getPath(self, data):
        fft = np.absolute(np.fft.rfft(data, n=len(data)))
        bins = fft
        polygonPath = QtGui.QPainterPath()
        polygonPath.moveTo(0, self.height() / 2)  # left middle
        width = 2 * self.width() / float(len(bins))
        for i, bin in enumerate(bins[:len(bins) // 2]):
            height = self.height() * bin / float(SAMPLE_MAX) / 10
            polygonPath.lineTo(i * width, self.height() / 2 - height / 2)
        polygonPath.lineTo(self.width(), self.height() / 2)  # right middle
        for i, bin in enumerate(bins[len(bins) // 2:]):
            height = self.height() * bin / float(SAMPLE_MAX) / 10
            polygonPath.lineTo(self.width() - i * width,
                               self.height() / 2 + height / 2)
        polygonPath.closeSubpath()
        return polygonPath

    def generate(self, data):
        img = self.img
        img.fill(0)
        painter = QtGui.QPainter(img)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 25)))
        path = self.getPath(data)
        painter.drawPath(path)
        del painter
        return img
