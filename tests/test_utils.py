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
from ossie.utils import sb
from ossie.cf import CF as _CF
import ossie.utils.bulkio.bulkio_data_helpers as _bulkio_data_helpers
from bulkio.bulkioInterfaces import BULKIO as _BULKIO
from bulkio.bulkioInterfaces import BULKIO__POA as _BULKIO__POA
from omniORB import any
import copy

def display_return_packets(packet_list, count, source_name):
    ret_str = "%s Packets %d:" % (source_name, count)
    for packet in packet_list:
        ret_str += "%s\n\t\t" % format_packet_display(packet)
    if packet_list == []:
        ret_str += "%s\n\t\t" % '[]'
    print ret_str[:-3]

def format_packet_display(packet):
    ret_str = "{"
    ret_str += "Data=%s, " % packet.data[0]
    ret_str += "T.twsec=%s, " % packet.T.twsec
    ret_str += "T.tfsec=%s, " % packet.T.tfsec
    ret_str += "EOS=%s" % packet.EOS
    ret_str += "}"
    return ret_str

def update_read_eos(buffer1, buffer2):
    return buffer1[-1].EOS and buffer2[-1].EOS

def get_first_item(data_list):
    ret_value = None
    if len(data_list) > 0:
        ret_value = data_list.pop(0)
    return ret_value

def get_bulkio_packet_time(packet):
    return packet.T.twsec + packet.T.tfsec

class BufferedPacket(object):
    def __init__(self, data, T, EOS, streamID, sri):
        self.data = data
        self.T = T
        self.EOS = EOS
        self.streamID = streamID
        self.sri = sri
    
    def pushPacket_data(self):
        return (self.data, self.T, self.EOS, self.streamID)
    
    def __str__(self):
        ret_str =  "{"
        ret_str += "Data=%s, " % self.data
        ret_str += "T=%s, " % self.T
        ret_str += "streamID=%s" % self.streamID
        ret_str += "}"
        return ret_str
    
    def __repr__(self):
        return self.__str__()

class MyDataSource(sb.DataSource):
    def __init__(self, **args):
        sb.DataSource.__init__(self, **args)
    
    # overriding DataSource push() and pushThread() to allow for custom timestamps on each packet pushed out
    def push(self,
             data,
             EOS         = False,
             streamID    = "defaultStreamID",
             sampleRate  = 1.0,
             complexData = False,
             SRIKeywords = {},
             loop        = None,
             time        = None):
        self._dataQueue.put((data,
                             EOS,
                             streamID,
                             sampleRate,
                             complexData,
                             SRIKeywords,
                             loop,
                             time))
    
    # Also modified pushThread() so that SRIKeywords is a dictionary of sri keywords
    def pushThread(self):
        self.settingsAcquired = False
        self.threadExited = False
        # Make sure data passed in is within min/max bounds on port type
        # and is a valid type
        currentSampleTime = self._startTime
        while not self._exitThread:
            exitInputLoop = False
            while not exitInputLoop:
                try:
                    dataset = self._dataQueue.get(timeout=0.1)
                    exitInputLoop = True
                    settingsAcquired = True
                except:
                    if self._exitThread:
                        exitInputLoop = True
            if self._exitThread:
                if self.settingsAcquired:
                    self._pushPacketAllConnectedPorts([],
                                                      currentSampleTime,
                                                      EOS,
                                                      streamID)
                self.threadExited = True
                return

            data                = dataset[0]
            EOS                 = dataset[1]
            streamID            = dataset[2]
            sampleRate          = dataset[3]
            complexData         = dataset[4]
            SRIKeywords         = dataset[5]
            loop                = dataset[6]
            currentSampleTime   = dataset[7] or currentSampleTime
            
            # If loop is set in method call, override class attribute
            if loop != None:
                self._loop = loop
            try:
                self._sampleRate  = sampleRate
                self._complexData = complexData
                self._SRIKeywords = SRIKeywords
                self._streamID    = streamID
                candidateSri      = None
                # If any SRI info is set, call pushSRI
                if streamID != None or \
                  sampleRate != None or \
                  complexData != None or \
                  len(SRIKeywords) > 0:
                    keywords = []
                    for key, value in self._SRIKeywords.items():
                        keywords.append(_CF.DataType(id=key, value=any.to_any(value)))
                    candidateSri = _BULKIO.StreamSRI(1, 0.0, 1, 0, 0, 0.0, 0, 0, 0,
                                                streamID, True, keywords)
                    
                    if sampleRate > 0.0:
                        candidateSri.xdelta = 1.0/float(sampleRate)
    
                    if complexData == True:
                        candidateSri.mode = 1
                    else:
                        candidateSri.mode = 0

                    if self._startTime >= 0.0:
                        candidateSri.xstart = self._startTime
                else:
                    candidateSri = _BULKIO.StreamSRI(1, 0.0, 1, 0, 0, 0.0, 0, 0, 0,
                                                "defaultStreamID", True, [])

                if self._sri==None or not sb.io_helpers.compareSRI(candidateSri, self._sri):
                    self._sri = candidateSri
                    self._pushSRIAllConnectedPorts(sri = self._sri)
    
                # Call pushPacket
                # If necessary, break data into chunks of pktSize for each
                # pushPacket
                if len(data) > 0:
                    self._pushPacketsAllConnectedPorts(data,
                                                       currentSampleTime,
                                                       EOS,
                                                       streamID)
                    # If loop is set to True, continue pushing data until loop
                    # is set to False or stop() is called
                    while self._loop:
                        self._pushPacketsAllConnectedPorts(data,
                                                           currentSampleTime,
                                                           EOS,
                                                           streamID)
                else:
                    self.pushPacket([])
            except Exception, e:
                print self.className + ":pushData() failed " + str(e)
        self.threadExited = True



class MyDataSink(sb.DataSink):
    def __init__(self):
        sb.DataSink.__init__(self)

    def getPort(self, portName):
        try:
            self._sinkPortType = self.getPortType(portName)
            # Set up output array sink
            if str(portName) == "xmlIn":
                self._sink = _bulkio_data_helpers.XmlArraySink(eval(self._sinkPortType))
            else:
                self._sink = MyArraySink(eval(self._sinkPortType))
            
            if self._sink != None:
                self._sinkPortObject = self._sink.getPort()
                return self._sinkPortObject
            else:
                return None
        except Exception, e:
            print self.className + ":getPort(): failed " + str(e)
            return None

class MyArraySink(_bulkio_data_helpers.ArraySink):
    def __init__(self, porttype):
        _bulkio_data_helpers.ArraySink.__init__(self, porttype)
        
    def pushPacket(self, data, ts, EOS, stream_id):
        self.port_lock.acquire()
        if EOS:
            self.gotEOS = True
        else:
            self.gotEOS = False
        try:
            packet = BufferedPacket(data, ts, EOS, stream_id, copy.deepcopy(self.sri))
            self.data.append(packet)
        finally:
            self.port_lock.release()

class ExpectedData(object):
    def __init__(self, faux_data=None):
        self.data1 = []
        self.data2 = []
        self.faux_data= faux_data or [0]
        
    def add_matched(self, d1, d2, time):
        self.data1.append((d1, time))
        self.data2.append((d2, time))
    
    def add_data1_faux_data2(self, d1, time):
        self.data1.append((d1, time))
        self.data2.append((self.faux_data, time))
    
    def add_data2_faux_data1(self, d2, time):
        self.data2.append((d2, time))
        self.data1.append((self.faux_data, time))
    
    def extend(self, additional_expected_data):
        self.data1.extend(additional_expected_data.data1)
        self.data2.extend(additional_expected_data.data2)
