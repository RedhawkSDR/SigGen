#!/usr/bin/env python
#
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components SigGen.
# 
# REDHAWK Basic Components SigGen is free software: you can redistribute it and/or modify it under the terms of 
# the GNU Lesser General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components SigGen is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#
#
# AUTO-GENERATED CODE.  DO NOT MODIFY!
#
# Source: SigGen.spd.xml
from ossie.cf import CF
from ossie.cf import CF__POA
from ossie.utils import uuid

from ossie.resource import Resource
from ossie.threadedcomponent import *
from ossie.properties import simple_property

import Queue, copy, time, threading
from ossie.resource import usesport, providesport
import bulkio

class SigGen_base(CF__POA.Resource, Resource, ThreadedComponent):
        # These values can be altered in the __init__ of your derived class

        PAUSE = 0.0125 # The amount of time to sleep if process return NOOP
        TIMEOUT = 5.0 # The amount of time to wait for the process thread to die when stop() is called
        DEFAULT_QUEUE_SIZE = 100 # The number of BulkIO packets that can be in the queue before pushPacket will block

        def __init__(self, identifier, execparams):
            loggerName = (execparams['NAME_BINDING'].replace('/', '.')).rsplit("_", 1)[0]
            Resource.__init__(self, identifier, execparams, loggerName=loggerName)
            ThreadedComponent.__init__(self)

            # self.auto_start is deprecated and is only kept for API compatibility
            # with 1.7.X and 1.8.0 components.  This variable may be removed
            # in future releases
            self.auto_start = False
            # Instantiate the default implementations for all ports on this component
            self.port_out = bulkio.OutDoublePort("out")

        def start(self):
            Resource.start(self)
            ThreadedComponent.startThread(self, pause=self.PAUSE)

        def stop(self):
            if not ThreadedComponent.stopThread(self, self.TIMEOUT):
                raise CF.Resource.StopError(CF.CF_NOTSET, "Processing thread did not die")
            Resource.stop(self)

        def releaseObject(self):
            try:
                self.stop()
            except Exception:
                self._log.exception("Error stopping")
            Resource.releaseObject(self)

        ######################################################################
        # PORTS
        # 
        # DO NOT ADD NEW PORTS HERE.  You can add ports in your derived class, in the SCD xml file, 
        # or via the IDE.

        port_out = usesport(name="out",
                            repid="IDL:BULKIO/dataDouble:1.0",
                            type_="data")

        ######################################################################
        # PROPERTIES
        # 
        # DO NOT ADD NEW PROPERTIES HERE.  You can add properties in your derived class, in the PRF xml file
        # or by using the IDE.
        frequency = simple_property(id_="frequency",
                                    type_="double",
                                    defvalue=1000.0,
                                    mode="readwrite",
                                    action="external",
                                    kinds=("configure",),
                                    description="""rate at which the periodic output waveforms repeat.  This value is ignored for aperiodic waveforms.""")
        
        sample_rate = simple_property(id_="sample_rate",
                                      type_="double",
                                      defvalue=5000.0,
                                      mode="readwrite",
                                      action="external",
                                      kinds=("configure",),
                                      description="""sampling rate for output data.""")
        
        magnitude = simple_property(id_="magnitude",
                                    type_="double",
                                    defvalue=1.0,
                                    mode="readwrite",
                                    action="external",
                                    kinds=("configure",),
                                    description="""amplitude of output data""")
        
        shape = simple_property(id_="shape",
                                type_="string",
                                defvalue="sine",
                                mode="readwrite",
                                action="external",
                                kinds=("configure",),
                                description="""determine output data type""")
        
        xfer_len = simple_property(id_="xfer_len",
                                   type_="long",
                                   defvalue=1000,
                                   mode="readwrite",
                                   action="external",
                                   kinds=("configure",),
                                   description="""number of samples of output data per output packet""")
        
        throttle = simple_property(id_="throttle",
                                   type_="boolean",
                                   defvalue=True,
                                   mode="readwrite",
                                   action="external",
                                   kinds=("configure",),
                                   description="""Throttles the output data rate to approximately sample_rate""")
        
        stream_id = simple_property(id_="stream_id",
                                    type_="string",
                                    defvalue="SigGen Stream",
                                    mode="readwrite",
                                    action="external",
                                    kinds=("configure",),
                                    description="""bulkio sri streamID for this data source.""")
        
        chan_rf = simple_property(id_="chan_rf",
                                  type_="double",
                                  defvalue=-1.0,
                                  mode="readwrite",
                                  action="external",
                                  kinds=("configure",),
                                  description="""Sets the CHAN_RF SRI keyword. Set to -1 if not desired.""")
        
        col_rf = simple_property(id_="col_rf",
                                 type_="double",
                                 defvalue=-1.0,
                                 mode="readwrite",
                                 action="external",
                                 kinds=("configure",),
                                 description="""Sets the COL_RF SRI keyword. Set to -1 if not desired.""")
        
        sri_blocking = simple_property(id_="sri_blocking",
                                       type_="boolean",
                                       defvalue=False,
                                       mode="readwrite",
                                       action="external",
                                       kinds=("configure",))
        

