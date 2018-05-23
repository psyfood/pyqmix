#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import OrderedDict
from ruamel.yaml import YAML

yaml = YAML()
yaml.default_flow_style = False


PYQMIX_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.pyqmix')
PYQMIX_CONFIG_FILE = os.path.join(PYQMIX_CONFIG_DIR, 'config.yaml')


# Python 2 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


def read_config():
    """
    Read the currently stored pyqmix confuration from disk.

    Returns
    -------
    cfg : dict
        The loaded configuration.

    """
    try:
        with open(PYQMIX_CONFIG_FILE, 'r') as f:
            cfg = yaml.load(f)
    except FileNotFoundError:
        try:
            os.makedirs(PYQMIX_CONFIG_DIR)
        except OSError:
            if not os.path.isdir(PYQMIX_CONFIG_DIR):
                raise

        cfg = OrderedDict(qmix_dll_dir='', qmix_config_dir='',
                          pumps=OrderedDict())

    return cfg


def set_qmix_config_dir(d):
    """
    Specify the location of the directory containing the Qmix configurations.

    Parameters
    ----------
    d : string
        The Qmix configuration directory. Must be an absolute path.

    """
    cfg = read_config()
    cfg['qmix_config_dir'] = d

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def set_qmix_dll_dir(d):
    """
    Specify the location of the directory containing the Qmix DLL files.

    Parameters
    ----------
    d : string
        Th Qmix DLL directory. Must be an absolute path.

    """
    cfg = read_config()
    cfg['qmix_dll_dir'] = d

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def add_pump(index):
    """
    Add a new pump to the pyqmix configuration. Overwrites existing entries
    for a pump with the same index.

    Parameters
    ----------
    index : int
        The unique index of the pump. Indexing is zero-based, i.e. `index=0`
        refers to the first pump in the system.

    """
    if not isinstance(index, int):
        raise TypeError('Pump index must be an integer!')

    cfg = read_config()
    cfg['pumps'][index] = OrderedDict(name=None, volume_unit=None,
                                      flow_unit=None, syringe_params=None,
                                      drive_pos_counter=None)

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def set_pump_name(index, name):
    cfg = read_config()
    pump = cfg['pumps'][index]
    pump['name'] = name

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def set_pump_drive_pos_counter(index, value):
    cfg = read_config()
    pump = cfg['pumps'][index]
    pump['drive_pos_counter'] = value

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def set_pump_volume_unit(index, prefix, unit):
    cfg = read_config()
    pump = cfg['pumps'][index]
    pump['volume_unit'] = OrderedDict(prefix=prefix, unit=unit)

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def set_pump_flow_unit(index, prefix, volume_unit, time_unit):
    cfg = read_config()
    pump = cfg['pumps'][index]
    pump['flow_unit'] = OrderedDict(prefix=prefix, volume_unit=volume_unit,
                                    time_unit=time_unit)

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def set_pump_syringe_params(index, inner_diameter_mm, max_piston_stroke_mm):
    cfg = read_config()
    pump = cfg['pumps'][index]
    pump['syringe_params'] = OrderedDict(
        inner_diameter_mm=inner_diameter_mm,
        max_piston_stroke_mm=max_piston_stroke_mm)

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def remove_pump(index):
    """
    Remove a pump and syringe configuration.

    Parameters
    ----------
    index : int
        The unique index of the pump.

    Raises
    ------
    KeyError
        If the specified pump index could not be found in the configuration
        file.

    """
    cfg = read_config()

    try:
        del cfg['pumps'][index]
        with open(PYQMIX_CONFIG_FILE, 'w') as f:
            yaml.dump(cfg, f)
    except KeyError:
        msg = ('Specified pump index could not be found in the configuration '
               'file.')
        raise KeyError(msg)
