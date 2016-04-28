# -*- coding: utf-8 -*-
"""The Raspberry GPIO components

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

import logging
logger = logging.getLogger(__name__)
import os, sys
import time
import datetime
import threading

from janitoo.thread import JNTBusThread, BaseThread
from janitoo.options import get_option_autostart
from janitoo.utils import HADD
from janitoo.node import JNTNode
from janitoo.value import JNTValue
from janitoo.component import JNTComponent
from janitoo.bus import JNTBus

from janitoo_raspberry_sound.thread_sound import OID
import alsaaudio

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_SWITCH_BINARY = 0x0025
COMMAND_WEB_RESOURCE = 0x1031
COMMAND_DOC_RESOURCE = 0x1032

assert(COMMAND_DESC[COMMAND_SWITCH_BINARY] == 'COMMAND_SWITCH_BINARY')
assert(COMMAND_DESC[COMMAND_WEB_RESOURCE] == 'COMMAND_WEB_RESOURCE')
assert(COMMAND_DESC[COMMAND_DOC_RESOURCE] == 'COMMAND_DOC_RESOURCE')
##############################################################

def make_input(**kwargs):
    return InputComponent(**kwargs)

class SoundBus(JNTBus):
    """A bus to manage GPIO
    """
    def __init__(self, **kwargs):
        """
        :param kwargs: parameters transmitted to :py:class:`smbus.SMBus` initializer
        """
        JNTBus.__init__(self, **kwargs)
        self._sound_lock = threading.Lock()
        self.load_extensions(OID)
        self.export_attrs('sound_acquire', self.sound_acquire)
        self.export_attrs('sound_release', self.sound_release)
        self.export_attrs('sound_locked', self.sound_locked)

    def check_heartbeat(self):
        """Check that the component is 'available'

        """
        return True

    def sound_acquire(self, blocking=True):
        """Get a lock on the bus"""
        if self._sound_lock.acquire(blocking):
            return True
        return False

    def sound_release(self):
        """Release a lock on the bus"""
        self._sound_lock.release()

    def sound_locked(self):
        """Get status of the lock"""
        return self._sound_lock.locked()

class InputComponent(JNTComponent):
    """ An input component for sound
        https://github.com/larsimmisch/pyalsaaudio/blob/master/recordtest.py
    """

    def __init__(self, **kwargs):
        """
        """
        oid = kwargs.pop('oid', 'rpisound.input')
        name = kwargs.pop('name', "Input")
        product_name = kwargs.pop('product_name', "Audio input")
        product_type = kwargs.pop('product_type', "Software")
        product_manufacturer = kwargs.pop('product_manufacturer', "Janitoo")
        JNTComponent.__init__(self, oid=oid, name=name, product_name=product_name, product_type=product_type, product_manufacturer=product_manufacturer, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
