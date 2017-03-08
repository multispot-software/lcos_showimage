"""
Display a b/w image without frame on the main screen or on one of the two LCOS,
with an optional monitor window on the main screen.
"""

from PyQt4 import QtCore, QtGui
import numpy as np
import matplotlib.pyplot as plt


class LCOSImg:
    """Display pattern on LCOS or main screen with optional monitor window.

    On initialization it shows a pattern (with no frame) on the main screen
    and a monitor window. Use methods .to_*_lcos() to move pattern to an LCOS
    screen. Assign the `pattern` property to change pattern and the `monitor`
    property to enable/disable the monitor window.
    """
    mainscreen_resolution = (1920, 1200)
    lcos_shape = 600, 800  # rows, cols

    def __init__(self, pattern=None, monitor=True):
        """
        Arguments:
            patterns (array): array of uint8 containing the pattern.
            monitor (bool): if True show the monitor window.
        """
        self.label = QtGui.QLabel()
        self.label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.label.resize(*self.lcos_shape[::-1])
        self._pattern = np.zeros(self.lcos_shape, dtype='uint8')
        self._position_msg = ''
        self.monitor = monitor
        if pattern is not None:
            self.pattern = pattern
        self.to_main_screen()
        self.show()

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        assert value.shape == self.lcos_shape
        assert value.dtype == np.uint8
        self._pattern = value
        # Update image on screen
        i = QtGui.QImage(self._pattern.tostring(), self.lcos_shape[1],
                         self.lcos_shape[0], QtGui.QImage.Format_Indexed8)
        p = QtGui.QPixmap.fromImage(i)
        self.label.setPixmap(p)
        # Update image on monitor window
        self._update_monitor()

    @property
    def monitor(self):
        return self._monitor

    @monitor.setter
    def monitor(self, value):
        assert value or not value
        self._monitor = value
        self._update_monitor()

    def _update_monitor(self):
        if not self._monitor:
            # Close figure
            if hasattr(self, 'fig'):
                plt.close(self.fig)
                delattr(self, 'fig')
                delattr(self, 'im')
        else:
            if (not hasattr(self, 'fig') or
                    not plt.fignum_exists(self.fig.number)):
                # Create new figure
                self.fig = plt.figure()
                self.im = plt.imshow(self.pattern, vmin=0, vmax=255)
            else:
                # Update old figure
                self.im.set_data(self._pattern)
                self.fig.canvas.draw()
            self.fig.axes[0].set_title(self._position_msg)

    def show(self):
        """Show pattern. Reverse method is `hide`."""
        self.label.show()
        self._position_msg = self._position_msg.replace('(hidden)', '').strip()
        self._update_monitor()

    def hide(self):
        """Hide pattern. Reverse method is `show`. Note that if there is
        no other window on the LCOS screen, the LCOS will show the desktop
        background (e.g. the windows logo).
        """
        self.label.hide()
        self._position_msg = '%s (hidden)' % self._position_msg
        self._update_monitor()

    def to_green_lcos(self):
        self.label.move(0, self.mainscreen_resolution[1])
        self._position_msg = 'Displayed on GREEN LCOS'
        self._update_monitor()

    def to_red_lcos(self):
        self.label.move(self.mainscreen_resolution[0], 0)
        self._position_msg = 'Displayed on RED LCOS'
        self._update_monitor()

    def to_main_screen(self):
        self.label.move(0, 0)
        self._position_msg = 'Displayed on main screen'
        self._update_monitor()

    def blank(self):
        """Show a flat/black pattern (all zeros)."""
        self.pattern = np.zeros(self.lcos_shape, dtype='uint8')
