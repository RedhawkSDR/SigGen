#!/usr/bin/env python
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
# AUTO-GENERATED
#
# Source: SigGen.spd.xml
from ossie.resource import Resource, start_component
import logging
import math
from bulkio.bulkioInterfaces import BULKIO, BULKIO__POA 
import Waveform
from omniORB import any
from array import array
import numpy as np

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
        
        keywords = []
        if self.chan_rf != -1:
            keywords.append(CF.DataType('CHAN_RF', any.to_any(self.chan_rf)))
        if self.col_rf != -1:
            keywords.append(CF.DataType('COL_RF', any.to_any(self.col_rf)))
        if self.sri_blocking == None:
            self.sri_blocking = False
        self.sri = BULKIO.StreamSRI(1, 0.0, 0.0, BULKIO.UNITS_TIME, 0, 0.0, 0.0, BULKIO.UNITS_NONE, 0, self.stream_id, self.sri_blocking, keywords)
        self.sriUpdate = True
        self.phase = 0
        self.chirp = 0
        self.sample_time_delta = 0.0
        self.delta_phase = 0.0
        self.delta_phase_offset = 0.0
        self.cached_stream_id=self.stream_id
        self.stream_created=False
        self.next_time = None
        
        self._waveform = Waveform.Waveform()

        # Separate listeners required. Bug fixed in CF 1.10.1
        self.addPropertyChangeListener("stream_id", self.prop_update_sri)
        self.addPropertyChangeListener("chan_rf", self.prop_update_sri2)
        self.addPropertyChangeListener("col_rf", self.prop_update_sri3)
        self.addPropertyChangeListener("sri_blocking", self.prop_update_sri_blocking)

    def start(self):
        if not self._get_started():
            self.next_time = bulkio.timestamp.now()
        SigGen_base.start(self)

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
            
        if self.sriUpdate or not self.port_dataFloat_out.sriDict.has_key(self.cached_stream_id) or not self.port_dataShort_out.sriDict.has_key(self.cached_stream_id):
            self.sriUpdate = False
            
            # Send EOS if necessary
            if self.stream_id != self.cached_stream_id and self.stream_created:
                self.port_dataFloat_out.pushPacket([], self.next_time, True, self.cached_stream_id)
                self.port_dataShort_out.pushPacket([], self.next_time, True, self.cached_stream_id)
            self.cached_stream_id = self.stream_id
        
            keywords = []
            if self.chan_rf != -1:
                keywords.append(CF.DataType('CHAN_RF', any.to_any(self.chan_rf)))
            if self.col_rf != -1:
                keywords.append(CF.DataType('COL_RF', any.to_any(self.col_rf)))
            self.sri.keywords = keywords
            self.stream_created = True
            self.port_dataFloat_out.pushSRI(self.sri)
            self.port_dataShort_out.pushSRI(self.sri)
            
        self.delta_phase = self.frequency * self.sample_time_delta
        self.delta_phase_offset = self.chirp * self.sample_time_delta * self.sample_time_delta
        if ((self.delta_phase < 0) and (not self.shape == "sine")):
            self.delta_phase = -self.delta_phase
            
        # Generate the Waveform
        data = []
        if self.shape == "sine":
            data = self._waveform.sincos(self.magnitude, self.phase, self.delta_phase, self.last_xfer_len, 1)
        elif self.shape == "square":
            data = self._waveform.square(self.magnitude, self.phase, self.delta_phase, self.last_xfer_len, 1)
        elif self.shape == "triangle":
            data = self._waveform.triangle(self.magnitude, self.phase, self.delta_phase, self.last_xfer_len, 1)
        elif self.shape == "sawtooth":
            data = self._waveform.sawtooth(self.magnitude, self.phase, self.delta_phase, self.last_xfer_len, 1)
        elif self.shape == "pulse":
            data = self._waveform.pulse(self.magnitude, self.phase, self.delta_phase, self.last_xfer_len, 1)
        elif self.shape == "constant":
            data = self._waveform.constant(self.magnitude, self.last_xfer_len, 1)
        elif self.shape == "whitenoise":
            data = self._waveform.whitenoise(self.magnitude, self.last_xfer_len, 1)
        elif self.shape == "lrs":
            data = self._waveform.lrs(self.magnitude, self.last_xfer_len, 1, 1)
        else:
            return NOOP
  
        self.phase += self.delta_phase*self.last_xfer_len # increment phase
        self.phase -= math.floor(self.phase) # module 1.0
        
        # Push the data
        self.port_dataFloat_out.pushPacket(data, self.next_time, False, self.cached_stream_id)
        
        # Only convert and push short data if the port is connected
        if self.port_dataShort_out._get_state() == BULKIO.ACTIVE:
            self.port_dataShort_out.pushPacket(self.convert_float_2_short(data), 
                                           self.next_time, False, self.cached_stream_id)
        
        # Advance time
        self.next_time.tfsec += self.last_xfer_len * self.sri.xdelta
        if self.next_time.tfsec > 1.0:
            self.next_time.tfsec -= 1.0
            self.next_time.twsec += 1.0
        
        # If we are throttling, wait...otherwise run at full speed
        if self.throttle:
            wait_amt = self.last_xfer_len * self.sample_time_delta
            try:
                time.sleep(wait_amt)
            finally:
                return NORMAL
            
        return NORMAL
    
    def convert_float_2_short(self, data):
        shortData = array("h")
        shortMin = np.iinfo(np.int16).min
        shortMax = np.iinfo(np.int16).max
                
        for i in range(len(data)):
            shortData.append(np.int16(min(shortMax, max(shortMin, np.float32(data[i])))))
             
        return shortData.tolist()
        
    def prop_update_sri(self, propid, oldval, newval):
        self.sri.streamID = self.stream_id
        self.sriUpdate = True

    def prop_update_sri2(self, propid, oldval, newval):
        self.sriUpdate = True

    def prop_update_sri3(self, propid, oldval, newval):
        self.sriUpdate = True

    # Check for changes to the SRI Blocking property
    def prop_update_sri_blocking(self, propid, oldval, newval):
        if newval != None:
            self.sri.blocking = newval
        elif oldval != None:
            self.sri.blocking = oldval
        else:
            self.sri.blocking = False
            
        self.sriUpdate = True
        
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.WARN)
    logging.debug("Starting Component")
    start_component(SigGen_i)

