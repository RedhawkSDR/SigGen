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
import numpy as np
from array import array

PRECISION=7
NUM_PLACES=7

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0,debug=False):
    ''' Return True if the values a and b are close to each other and False otherwise.

	Whether or not two values are considered close is determined according to given absolute and relative tolerances.

	rel_tol is the relative tolerance - it is the maximum allowed difference between a and b, relative to the larger
        absolute value of a or b. For example, to set a tolerance of 5%, pass rel_tol=0.05. The default tolerance is 1e-09,
        which assures that the two values are the same within about 9 decimal digits. rel_tol must be greater than zero.

	abs_tol is the minimum absolute tolerance - useful for comparisons near zero. abs_tol must be at least zero.
        
        Note: take from math module in newer versions of Python (>= 3.5)
    '''
    retval = abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    if debug:
        _abs=abs(a-b)
        _tol=max(rel_tol * max(abs(a), abs(b)), abs_tol)
        _rel=rel_tol * max(abs(a), abs(b))
        print '.' if retval else 'F', repr(a), repr(b), repr(_abs), repr(_tol), repr(_rel), repr(abs_tol)

    return retval
    #return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
        

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
        self.floatSink = test_utils.MyDataSink()
        self.shortSink = test_utils.MyDataSink()

        #start all components
        self.launch(initialize=True)
        self.comp.start()
        self.floatSink.start()
        self.shortSink.start()
        #do the connections
        self.comp.connect(self.floatSink, usesPortName='dataFloat_out')
        self.comp.connect(self.shortSink, usesPortName="dataShort_out")
        self.waveforms = waveforms.Waveforms()
        

    def tearDown(self):
        """Finish the unit test - this is run after every method that starts with test        """
        self.comp.stop()
        #######################################################################
        # Simulate regular component shutdown
        self.comp.releaseObject()
        self.floatSink.stop()
        self.shortSink.stop()
        ossie.utils.testing.ScaComponentTestCase.tearDown(self)
        
    ##################
    # TEST FUNCTIONS #
    ##################

    def test_constant_float(self):
        print "\n... Starting Test Constant with dataFloat_out"
        self._test_constant(self.floatSink, np.float32)

    def test_constant_short(self):
        print "\n... Starting Test Constant with dataShort_out"
        self._test_constant(self.shortSink, np.int16)

    def test_throttle_float(self):
        print "\n... Starting Throttle Test for dataFloat_out"
        self._test_throttle(self.floatSink)

    def test_throttle_short(self):
        print "\n... Starting Throttle Test for dataShort_out"
        self._test_throttle(self.shortSink)

    def test_pulse_float(self):
        print "\n... Starting Test Pulse with dataFloat_out"
        self._test_pulse(self.floatSink, np.float32)

    def test_pulse_short(self):
        print "\n... Starting Test Pulse with dataShort_out"
        self._test_pulse(self.shortSink, np.int16)
    
    def test_stream_id_float(self):
        print "\n... Starting Test Stream ID for dataFloat_out"
        self._test_stream_id(self.floatSink)
    
    def test_stream_id_short(self):
        print "\n... Starting Test Stream ID for dataShort_out"
        self._test_stream_id(self.shortSink)
        
    def test_lrs_float(self):
        print "\n... Starting Test lrs with dataFloat_out"
        self._test_lrs(self.floatSink, self._convert_float_2_float32)
        
    def test_lrs_short(self):
        print "\n... Starting Test lrs with dataShort_out"
        self._test_lrs(self.shortSink, self._convert_float_2_short)
    
    def test_sine_float(self):
        print "\n... Starting Test sine with dataFloat_out"
        self._test_signal_with_phase("sine", self.floatSink, self.waveforms.generate_sine, self._convert_float_2_float32)
    
    def test_sine_short(self):
        print "\n... Starting Test sine with dataShort_out"
        self._test_signal_with_phase("sine", self.shortSink, self.waveforms.generate_sine, self._convert_float_2_short)
    
    def test_sawtooth_float(self):
        print "\n... Starting Test sawtooth with dataFloat_out"
        self._test_signal_with_phase("sawtooth", self.floatSink, self.waveforms.generate_sawtooth, self._convert_float_2_float32)
    
    def test_sawtooth_short(self):
        print "\n... Starting Test sawtooth with dataShort_out"
        self._test_signal_with_phase("sawtooth", self.shortSink, self.waveforms.generate_sawtooth, self._convert_float_2_short)
    
    def test_square_float(self):
        print "\n... Starting Test square with dataFloat_out"
        self._test_signal_with_phase("square", self.floatSink, self.waveforms.generate_square, self._convert_float_2_float32)
    
    def test_square_short(self):
        print "\n... Starting Test square with dataShort_out"
        self._test_signal_with_phase("square", self.shortSink, self.waveforms.generate_square, self._convert_float_2_short)
        
    def test_triangle_float(self):
        print "\n... Starting Test triangle with dataFloat_out"
        self._test_signal_with_phase("triangle", self.floatSink, self.waveforms.generate_triangle, self._convert_float_2_float32)
        
    def test_triangle_short(self):
        print "\n... Starting Test triangle with dataShort_out"
        self._test_signal_with_phase("triangle", self.shortSink, self.waveforms.generate_triangle, self._convert_float_2_short)
        
    def test_push_sri_float(self):
        print "\n...Starting Test push sri with dataFloat_out"
        self._test_push_sri(self.floatSink)
        
    def test_push_sri_short(self):
        print "\n...Starting Test push sri with dataShort_out"
        self._test_push_sri(self.shortSink)

    def test_no_configure_float(self):
        print "\n...Starting Test no configure with dataFloat_out"
        self._test_no_configure(self.floatSink, self._convert_float_2_float32)

    def test_no_configure_short(self):
        print "\n...Starting Test no configure with dataShort_out"
        self._test_no_configure(self.shortSink, self._convert_float_2_short)
                
    def test_frequency_float(self):
        print "\n...Starting Test frequency for dataFloat_out"
        self._test_frequency(self.floatSink)
                
    def test_frequency_short(self):
        print "\n...Starting Test frequency for dataShort_out"
        self._test_frequency(self.shortSink)
        
    ####################
    # HELPER FUNCTIONS #
    ####################
    
    def _generate_config(self):
        self.config_params = {}
        self.config_params["frequency"] = 2000.
        self.config_params["sample_rate"] = 5000.
        self.config_params["magnitude"] = 1000.
        self.config_params["xfer_len"] = 1000
        self.config_params["stream_id"] = "unit_test_stream"

    def _get_received_data(self, start_time, time_len, sink):
        received_data1 = []
        eos_all = False
        count = 0
        done = False
        stop_time = start_time + time_len
        while not (eos_all or done):
            out = sink.getData()
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

    def _convert_float_2_short(self, data):
        shortData = array("h")
        shortMin = np.iinfo(np.int16).min
        shortMax = np.iinfo(np.int16).max
                
        for i in range(len(data)):
            shortData.append(np.int16(min(shortMax, max(shortMin, np.float32(data[i])))))
             
        return shortData.tolist()

    def _convert_float_2_float32(self, data):
        floatData = array("f")
                
        for i in range(len(data)):
            floatData.append(np.float32(data[i]))
             
        return floatData.tolist()

    def _no_convert(self, data):
        return data

    def assert_isclose(self,a,b,precision=7,places=7):
        ''' Similar to assertAlmostEqual, but based on digits of precision rather than decimal places
            For 32-bit systems (float), the greatest precision possible is 7 digits.
            For 64-bit systems (double), the greatest precision possible is 15 digits.
            Set places for numbers near 0, where relative precision may fail.
        '''
        rel_tol=10**(-1*precision)
        abs_tol=10**(-1*places)
        # Rather than reimplement assert, call assertAlmostEqual which will fail
        isclose(a,b,rel_tol,abs_tol) or self.assertAlmostEqual(a,b,places)

    def _test_constant(self, sink, type_cast):
        self._generate_config()
        self.config_params["shape"] = "constant"
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        expected_value = type_cast(self.config_params["magnitude"])
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            for value in p.data:
                #self.assertAlmostEqual(value, expected_value)
                self.assert_isclose(value, expected_value, PRECISION, NUM_PLACES)

    def _test_throttle(self, sink):
        self._generate_config()
        self.config_params["shape"] = "constant"
        self.config_params["throttle"] = True
        
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        expected_num_packets = self.config_params["sample_rate"]/self.config_params["xfer_len"]
        
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        n_packets = len(rx_data)
        
        
        print "Received %d Packets" % n_packets
        print "Expected %d Packets (tolerance is +/- 1)" % expected_num_packets

        # Allow for +/- packet tolerance due to how we're getting the data
        self.assertTrue(n_packets >= expected_num_packets-1)
        self.assertTrue(n_packets <= expected_num_packets+1)

    def _test_pulse(self, sink, type_cast):
        self._generate_config()
        self.config_params["shape"] = "pulse"
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        expected_value = type_cast(self.config_params["magnitude"])
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            for value in p.data:
                self.assertTrue(value == expected_value or value == 0)
    
    def _test_stream_id(self, sink):
        self._generate_config()
        self.config_params["shape"] = "constant"
        
        default_stream_id = "SigGen Stream"
        test_stream_id = "unit_test_stream_id"
        
        self.config_params.pop("stream_id") # Verify that default stream id value is used
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
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
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data 2 Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(p.sri.streamID, test_stream_id)
        
    def _test_lrs(self, sink, convert_function):
        self._generate_config()
        self.config_params["shape"] = "lrs"
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        expected_values = convert_function(self.waveforms.generate_lrs(self.config_params["magnitude"], self.config_params["xfer_len"]))
        n_expected = len(expected_values)
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(len(p.data), n_expected)
            for rx_val, exp_val in zip(p.data, expected_values):
                #self.assertAlmostEqual(rx_val, exp_val, 5)
                self.assert_isclose(rx_val, exp_val, PRECISION, NUM_PLACES)
    
    def _test_signal_with_phase(self, shape, sink, signal_function, convert_function):
        self._generate_config()
        self.config_params["shape"] = shape
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec = 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        delta_phase = self.config_params["frequency"] / self.config_params["sample_rate"]
        expected_values = convert_function(signal_function(self.config_params["magnitude"], self.config_params["xfer_len"], dp=delta_phase ))
        n_expected = len(expected_values)
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(len(p.data), n_expected)
            for rx_val, exp_val in zip(p.data, expected_values):
                #self.assertAlmostEqual(rx_val, exp_val, 5)
                self.assert_isclose(rx_val, exp_val, PRECISION, NUM_PLACES)

    def _test_push_sri(self, sink):
        self._generate_config()
        self.config_params.pop("stream_id")
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.) # Ensure SigGen is sending out the desired signal before continuing
        start_time = time.time()
        rx_len_sec= 1. # Get 1s worth of data
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        for p in rx_data:
            #self.assertAlmostEqual(self.config_params["sample_rate"], 1 / p.sri.xdelta)
            self.assert_isclose(self.config_params["sample_rate"], 1 / p.sri.xdelta, PRECISION, NUM_PLACES)

    def _test_no_configure(self, sink, convert_function):
        time.sleep(1.)
        start_time = time.time()
        rx_len_sec = 1. 
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        delta_phase = self.comp.frequency / self.comp.sample_rate
        expected_values = convert_function(self.waveforms.generate_sine(self.comp.magnitude, self.comp.xfer_len, dp=delta_phase ))
        n_expected = len(expected_values)
        for p in rx_data:
            # Data returned is list of test_utils.BufferedPacket
            self.assertEqual(len(p.data), n_expected)
            for rx_val, exp_val in zip(p.data, expected_values):
                #self.assertAlmostEqual(rx_val, exp_val, 5)
                self.assert_isclose(rx_val, exp_val, PRECISION, NUM_PLACES)
                
    def _test_frequency(self, sink):
        self._generate_config()
        self.comp_obj.configure(props_from_dict(self.config_params))
        time.sleep(1.)
        start_time = time.time()
        rx_len_sec = 1. 
        rx_data = self._get_received_data(start_time, rx_len_sec, sink)
        print "\nReceived Data Time Range:"
        print rx_data[0].T
        print rx_data[-1].T
        
        zero_crossings = 0
        expected_zero_crossings = 2 * self.config_params["frequency"] * self.config_params["xfer_len"] / self.config_params["sample_rate"] # 2 * (zc/s /2) * (S/packet) / (S/s) = zc
        
        data = rx_data[0].data
        if abs(data[0]) <= 10**(-1*NUM_PLACES): data[0]=0.0 #same as (but less math): if isclose(data[0], 0, PRECISION, NUM_PLACES): data[0]=0.0
        for i in xrange(len(data)-1):
            if abs(data[i+1]) <= 10**(-1*NUM_PLACES): data[i+1]=0.0
            if (data[i] <= 0 and data[i+1] > 0) or (data[i] >= 0 and data[i+1] < 0):
                zero_crossings += 1
        self.assertEqual(zero_crossings, expected_zero_crossings)
    
if __name__ == "__main__":
    ossie.utils.testing.main("../SigGen.spd.xml") # By default tests all implementations
