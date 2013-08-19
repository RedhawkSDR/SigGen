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
import unittest
import ossie.utils.testing
import os
from omniORB import any
import test_utils
from ossie.properties import props_from_dict
import time
import waveforms

class ComponentTests(ossie.utils.testing.ScaComponentTestCase):
    """Test for all component implementations in SigGen"""

    def testScaBasicBehavior(self):
        #######################################################################
        # Launch the component with the default execparams
        execparams = self.getPropertySet(kinds=("execparam",), modes=("readwrite", "writeonly"), includeNil=False)
        execparams = dict([(x.id, any.from_any(x.value)) for x in execparams])
        self.launch(execparams)
        
        #######################################################################
        # Verify the basic state of the component
        self.assertNotEqual(self.comp, None)
        self.assertEqual(self.comp.ref._non_existent(), False)
        self.assertEqual(self.comp.ref._is_a("IDL:CF/Resource:1.0"), True)
        
        #######################################################################
        # Simulate regular component startup
        # Verify that initialize nor configure throw errors
        self.comp.initialize()
        configureProps = self.getPropertySet(kinds=("configure",), modes=("readwrite", "writeonly"), includeNil=False)
        self.comp.configure(configureProps)
        
        #######################################################################
        # Validate that query returns all expected parameters
        # Query of '[]' should return the following set of properties
        expectedProps = []
        expectedProps.extend(self.getPropertySet(kinds=("configure", "execparam"), modes=("readwrite", "readonly"), includeNil=True))
        expectedProps.extend(self.getPropertySet(kinds=("allocate",), action="external", includeNil=True))
        props = self.comp.query([])
        props = dict((x.id, any.from_any(x.value)) for x in props)
        # Query may return more than expected, but not less
        for expectedProp in expectedProps:
            self.assertEquals(props.has_key(expectedProp.id), True)
        
        #######################################################################
        # Verify that all expected ports are available
        for port in self.scd.get_componentfeatures().get_ports().get_uses():
            port_obj = self.comp.getPort(str(port.get_usesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a("IDL:CF/Port:1.0"),  True)
            
        for port in self.scd.get_componentfeatures().get_ports().get_provides():
            port_obj = self.comp.getPort(str(port.get_providesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a(port.get_repid()),  True)
            
        #######################################################################
        # Make sure start and stop can be called without throwing exceptions
        self.comp.start()
        self.comp.stop()
        
#        ######################################################################
#         Simulate regular component shutdown
#        self.comp.releaseObject()
    
    def setUp(self):
        """Set up the unit test - this is run before every method that starts with test        """
        ossie.utils.testing.ScaComponentTestCase.setUp(self)
        self.sink = test_utils.MyDataSink()
        #start all components
        self.launch()
        self.comp.start()
        self.sink.start()
        #do the connections
        self.comp.connect(self.sink)
        self.waveforms = waveforms.Waveforms()
        

    def tearDown(self):
        """Finish the unit test - this is run after every method that starts with test        """
        self.comp.stop()
        #######################################################################
        # Simulate regular component shutdown
        self.comp.releaseObject()
        self.sink.stop()
        ossie.utils.testing.ScaComponentTestCase.tearDown(self)
    
    def _generate_config(self):
        self.config_params = {}
        self.config_params["frequency"] = 2000.
        self.config_params["sample_rate"] = 5000.
        self.config_params["magnitude"] = 10.
        self.config_params["xfer_len"] = 1000
        self.config_params["stream_id"] = "unit_test_stream"

    def _get_received_data(self, start_time, time_len):
        received_data1 = []
        eos_all = False
        count = 0
        done = False
        stop_time = start_time + time_len
        while not (eos_all or done):
            out = self.sink.getData()
            for p in out:
                if p.T.twsec + p.T.tfsec >= start_time:
                    received_data1.append(p)
                    if p.T.twsec + p.T.tfsec > stop_time:
                        done = True
                        break
            
            try:
                eos_all = out[-1].EOS
            except IndexError:
                pass
            time.sleep(.01)
            count += 1
            if count == 2000:
                break
        return received_data1
    
    def test_constant(self):
        print "\n... Starting Test Constant"
        self._generate_config()
        self.config_params["shape"] = "constant"
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        expected_value = self.config_params["magnitude"]
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            for value in p.data:
                self.assertEqual(value, expected_value)


    def test_throttle(self):
        print "\n... Starting Throttle Test"
        self._generate_config()
        self.config_params["shape"] = "constant"
        self.config_params["throttle"] = True
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)

        
        expected_num_packets = self.config_params["sample_rate"]/self.config_params["xfer_len"]
        n_packets = len(rx_data)
        
        print "Received %d Packets" % n_packets
        print "Expected %d Packets (tolerance is +/- 1)" % expected_num_packets
        self.assertTrue(n_packets >= expected_num_packets-1 and n_packets <= expected_num_packets+1) # Allow for +/- packet tolerance due to how we're getting the data

    def test_pulse(self):
        print "\n... Starting Test Pulse"
        self._generate_config()
        self.config_params["shape"] = "pulse"
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        expected_value = self.config_params["magnitude"]
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            for value in p.data:
                self.assertTrue(value == expected_value or value == 0)
    
    def test_stream_id(self):
        print "\n... Starting Test Stream ID"
        self._generate_config()
        self.config_params["shape"] = "constant"
        
        default_stream_id = "SigGen Stream"
        test_stream_id = "unit_test_stream_id"
        
        self.config_params.pop("stream_id") # Verify that default stream id value is used
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)
        print "\nReceived Data 1 Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(p.sri.streamID, default_stream_id)
        
        self.comp_obj.configure(props_from_dict({"stream_id":test_stream_id}))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)
        print "\nReceived Data 2 Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(p.sri.streamID, test_stream_id)
        
    def test_lrs(self):
        print "\n... Starting Test lrs"
        self._generate_config()
        self.config_params["shape"] = "lrs"
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        expected_values = self.waveforms.generate_lrs(self.config_params["magnitude"], self.config_params["xfer_len"])
        n_expected = len(expected_values)
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(len(p.data), n_expected)
            for rx_val, exp_val in zip(p.data, expected_values):
                self.assertEqual(rx_val, exp_val)
    
    def test_sine(self):
        print "\n... Starting Test sine"
        self._test_signal_with_phase("sine", self.waveforms.generate_sine)
    
    def test_sawtooth(self):
        print "\n... Starting Test sawtooth"
        self._test_signal_with_phase("sawtooth", self.waveforms.generate_sawtooth)
    
    def test_square(self):
        print "\n... Starting Test square"
        self._test_signal_with_phase("square", self.waveforms.generate_square)
        
    def test_triangle(self):
        print "\n... Starting Test triangle"
        self._test_signal_with_phase("triangle", self.waveforms.generate_triangle)
    
    def _test_signal_with_phase(self, shape, signal_function):
        self._generate_config()
        self.config_params["shape"] = shape
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        delta_phase = self.config_params["frequency"] / self.config_params["sample_rate"]
        expected_values = signal_function(self.config_params["magnitude"], self.config_params["xfer_len"], dp=delta_phase )
        n_expected = len(expected_values)
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(len(p.data), n_expected)
            for rx_val, exp_val in zip(p.data, expected_values):
                self.assertEqual(rx_val, exp_val)
    
if __name__ == "__main__":
    ossie.utils.testing.main("../SigGen.spd.xml") # By default tests all implementations
