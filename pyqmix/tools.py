#!/usr/bin/env python
# -*- coding: utf-8 -*-


from .error import QmixError


def CHK(return_code, *args):
    """
    Check if the return value of the invoked function returned an error.

    The Qmix DLL makes this pretty easy: All errors are indicated by
    negative return values.

    Parameters
    ----------
    return_code : int
        The code returned from a Qmix DLL function.
    args
        All arguments passed to the function ``funcname``.

    Returns
    -------
    return_code : int
        If no error occurred, the originally passed return value is
        returned.

    Raises
    ------
    RuntimeError
        If the DLL function returned an error code.

    """
    if return_code >= 0:
        return return_code
    else:
        e = QmixError(return_code)
        error_string = e.error_string
        msg = (error_string + ", Error number: " + str(e.error_number) +
               ", Error code: " + str(e.error_code))
        raise RuntimeError(msg)
