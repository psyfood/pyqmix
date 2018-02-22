#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
from cffi import FFI

if sys.version_info[0] < 3:
    # Python 2 compatibility; requires `future` package.
    from builtins import bytes

from . import config
from .tools import CHK
from .headers import BUS_HEADER


class QmixBus(object):
    """
    Qmix bus interface.

    This interface establishes a connection with the labbCAN bus used for
    communication with all attached devices. Accordingly, has to be
    initialized before any hardware can be accessed.

    Parameters
    ----------
    config_dir : str
        Absolute path to the folder that contains the device configuration files
        (XML config files).

    dll_dir : str
        Absolute path to the folder that contains Qmix .dll files.

    auto_open : bool
        Whether to open the labbCAN bus automatically on object instantiation.

     auto_start : bool
        Whether to start the CAN bus communication automatically on object
        instantiation. Since the bus needs to be opened before communication
        can commence, setting `auto_start=True` will always open the bus,
        regardless of the `auto_open` parameter specified.

    """

    def __init__(self, config_dir=None, dll_dir=None, auto_open=True,
                 auto_start=True):
        if config.DLL_DIR is None:
            if dll_dir is None:
                raise ValueError('No DLL directory specified.')
            else:
                config.DLL_DIR = dll_dir

        self.dll_dir = config.DLL_DIR
        self.dll_file = os.path.join(self.dll_dir, 'labbCAN_Bus_API.dll')

        if config.CONFIG_DIR is None:
            if config_dir is None:
                raise ValueError('No Qmix configuration directory specified.')
            else:
                config.CONFIG_DIR = config_dir

        self.config_dir = config.CONFIG_DIR

        self.auto_open = auto_open
        self.auto_start = auto_start

        self._ffi = FFI()
        self._ffi.cdef(BUS_HEADER)
        self._dll = self._ffi.dlopen(self.dll_file)
        self.is_open = False
        self.is_started = False

        if self.auto_open:
            self.open()

        if self.auto_start:
            if not self.is_open:
                self.open()
            self.start()

    def __del__(self):
        self.stop()
        self.close()

    def _call(self, func_name, *args):
        func = getattr(self._dll, func_name)
        r = func(*args)
        r = CHK(r, func_name, *args)
        return r

    def open(self):
        """
        Initialize labbCAN bus.

        Initializes resources for a labbCAN bus instance, opens the bus and
        scans for connected devices.

        """
        self._call('LCB_Open', bytes(self.config_dir, 'utf8'))
        time.sleep(1)
        self.is_open = True

    def close(self):
        """
        Close labbCAN bus.

        """
        self._call('LCB_Close')
        self.is_open = False

    def start(self):
        """
        Start bus network communication.

        Sets all connected devices operational and enables them.
        Connected devices can be accessed only after this method has been
        invoked.

        """
        if not self.is_open:
            msg = ('Bus needs to be opened before communication can start.'
                   'Call `QmixBus.open()` first.')
            raise RuntimeError(msg)

        self._call('LCB_Start')
        time.sleep(1)
        self.is_started = True

    def stop(self):
        """
        Stop bus network communication.

        Stops network communication and closes the labbCAN device.
        The method should be called before calling
        :func:`qmix.QmixBus.close``.

        """
        self._call('LCB_Stop')
        self.is_started = False
