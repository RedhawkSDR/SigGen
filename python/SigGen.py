#!/usr/bin/env python 
#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components.
# 
# REDHAWK Basic Components is free software: you can redistribute it and/or modify it under the terms of 
# the GNU Lesser General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#
#
# AUTO-GENERATED
#
# Source: SigGen.spd.xml
from ossie.resource import Resource, start_component
import logging
import math
from bulkio.bulkioInterfaces import BULKIO, BULKIO__POA 
import Waveform

from SigGen_base import *

class SigGen_i(SigGen_base):
    """<DESCRIPTION GOES HERE>"""
    def initialize(self):
        """
        This is called by the framework immediately after your component registers with the NameService.
        
        In general, you should add customization here and not in the __init__ constructor.  If you have 
        a custom port implementation you can override the specific implementation here with a statement
        similar to the following:
          self.some_port = MyPortImplementation()
        """
        SigGen_base.initialize(self)
        self.last_xfer_len = self.xfer_len
        
        self.sri = BULKIO.StreamSRI(1, 0.0, 0.0, BULKIO.UNITS_TIME, 0, 0.0, 0.0, BULKIO.UNITS_NONE, 0, self.stream_id, False, [])
        self.sriUpdate = True
        self.phase = 0
        self.chirp = 0
        self.sample_time_delta = 0.0
        self.delta_phase = 0.0
        self.delta_phase_offset = 0.0
        
        self._waveform = Waveform.Waveform()

    def process(self):
        """
        Basic functionality:
        
            The process method should process a single "chunk" of data and then return. This method
            will be called from the processing thread again, and again, and again until it returns
            FINISH or stop() is called on the component.  If no work is performed, then return NOOP.
        """

        if self.stream_id == None:
            self.stream_id = str(uuid.uuid4())
            self.sri.streamID = self.stream_id

        if self.xfer_len != self.last_xfer_len:
            self.last_xfer_len = self.xfer_len
            self.sriUpdate = True
            
        self.sample_time_delta = 1.0/self.sample_rate
        if self.sample_time_delta != self.sri.xdelta:
            self.sri.xdelta = self.sample_time_delta
            self.sriUpdate = True
            
        if self.sriUpdate or not self.port_out.sriDict.has_key(self.stream_id):
            self.port_out.pushSRI(self.sri)
            self.sriUpdate = False
            
        self.delta_phase = self.frequency * self.sample_time_delta
        self.delta_phase_offset = self.chirp * self.sample_time_delta * self.sample_time_delta
        if ((self.delta_phase < 0) and (not self.shape == "sine")):
            self.delta_phase = -self.delta_phase
            
        # Generate the Waveform
        data = []
        if self.shape == "sine":
            data = self._waveform.sincos(self.magnitude, self.phase, self.delta_phase, self.xfer_len, 1)
        elif self.shape == "square":
            data = self._waveform.square(self.magnitude, self.phase, self.delta_phase, self.xfer_len, 1)
        elif self.shape == "triangle":
            data = self._waveform.triangle(self.magnitude, self.phase, self.delta_phase, self.xfer_len, 1)
        elif self.shape == "sawtooth":
            data = self._waveform.sawtooth(self.magnitude, self.phase, self.delta_phase, self.xfer_len, 1)
        elif self.shape == "pulse":
            data = self._waveform.pulse(self.magnitude, self.phase, self.delta_phase, self.xfer_len, 1)
        elif self.shape == "constant":
            data = self._waveform.constant(self.magnitude, self.xfer_len, 1)
        elif self.shape == "whitenoise":
            data = self._waveform.whitenoise(self.magnitude, self.xfer_len, 1)
        elif self.shape == "lrs":
            data = self._waveform.lrs(self.magnitude, self.xfer_len, 1, 1)
        else:
            return NOOP
  
        self.phase += self.delta_phase*self.xfer_len # increment phase
        self.phase -= math.floor(self.phase) # module 1.0
        
        # Create a CPU time-stamp
        tmp_time = time.time()
        wsec = math.modf(tmp_time)[1]
        fsec = math.modf(tmp_time)[0]
        
        tstamp = BULKIO.PrecisionUTCTime(BULKIO.TCM_CPU, BULKIO.TCS_VALID, 0, wsec, fsec)
        
        # Push the data
        self.port_out.pushPacket(data, tstamp, False, self.stream_id)
        
        # If we are throttling, wait...otherwise run at full speed
        if self.throttle:
            wait_amt = self.xfer_len * self.sample_time_delta
            try:
                time.sleep(wait_amt)
            finally:
                return NORMAL
            
        return NORMAL
    
    def onconfigure_prop_stream_id(self, oldval, newval):
        self.stream_id = newval
        self.sri.streamID = self.stream_id
        self.sriUpdate = True        
  
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    logging.debug("Starting Component")
    start_component(SigGen_i)

