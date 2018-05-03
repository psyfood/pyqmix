#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import OrderedDict
from ruamel.yaml import YAML

yaml = YAML()
yaml.default_flow_style = False


PYQMIX_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.pyqmix')
PYQMIX_CONFIG_FILE = os.path.join(PYQMIX_CONFIG_DIR, 'config.yaml')


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

        cfg = OrderedDict(qmix_dll_dir='', qmix_config_dir='', pumps=dict())

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


def add_pump(name, index,
             volume_prefix='milli', volume_unit='litres',
             flow_prefix='milli', flow_volume_unit='litres',
             flow_time_unit='per_second',
             syringe_inner_diameter_mm=32.5735,
             syringe_max_piston_stroke_mm=60):
    """
    Add a new pump (and syringe) to the pyqmix configuration.

    Parameters
    ----------
    name : string
        A unique specifier of the pump.

    index : int
        The index of the pump. Indexing is zero-based, i.e. `index=0`
        refers to the first pump in the system.

    volume_prefix : string
        The prefix of the SI unit:
        ``centi``, ``deci``, ``milli``, ``micro``.

    volume_unit : string
        The volume unit: ``litres``.

    flow_prefix : string
        Similar to `volume_prefix`, but for the flow rate.

    flow_volume_unit : string
        Similar to `volume_unit`, but for the flow rate.

    flow_time_unit : string
        The time unit (denominator) of the velocity unit:
        ``per_hour``, ``per_minute``, ``per_second``.

    syringe_inner_diameter_mm : float
        The inner diameter of the installed syringe.

    syringe_max_piston_stroke_mm : float
        Maximum piston stroke of the installed syringe.

    """
    p = OrderedDict(index=index,
                    volume_prefix=volume_prefix, volume_unit=volume_unit,
                    flow_prefix=flow_prefix, flow_volume_unit=flow_volume_unit,
                    flow_time_unit=flow_time_unit,
                    syringe_inner_diameter_mm=syringe_inner_diameter_mm,
                    syringe_max_piston_stroke_mm=syringe_max_piston_stroke_mm)

    cfg = read_config()
    pumps = cfg.get('pumps', dict())

    # pumps[name] = dict()
    # for param in p:
    #     pumps[name][param] = p[param]

    pumps[name] = p
    cfg['pumps'] = pumps

    with open(PYQMIX_CONFIG_FILE, 'w') as f:
        yaml.dump(cfg, f)


def remove_pump(name):
    """
    Remove a pump and syringe configuration.

    Parameters
    ----------
    name : string
        A unique specifier of the pump.

    Raises
    ------
    NameError
        If the specified pump name could not be found in the configuration
        file.

    """
    cfg = read_config()

    try:
        del cfg['pumps'][name]
        with open(PYQMIX_CONFIG_FILE, 'w') as f:
            yaml.dump(cfg, f)
    except KeyError:
        msg = ('Specified pump name could not be found in the configuration '
               'file.')
        raise NameError(msg)
