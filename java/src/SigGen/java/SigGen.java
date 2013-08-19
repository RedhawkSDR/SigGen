/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
 * source distribution.
 * 
 * This file is part of REDHAWK Basic Components SigGen.
 * 
 * REDHAWK Basic Components SigGen is free software: you can redistribute it and/or modify it under the terms of 
 * the GNU Lesser General Public License as published by the Free Software Foundation, either 
 * version 3 of the License, or (at your option) any later version.
 * 
 * REDHAWK Basic Components SigGen is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
 * PURPOSE.  See the GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License along with this 
 * program.  If not, see http://www.gnu.org/licenses/.
 */
package SigGen.java;

import java.util.Arrays;
import java.util.Properties;

import org.ossie.properties.PropertyListener;

import BULKIO.PrecisionUTCTime;
import BULKIO.StreamSRI;
import CF.DataType;
import CF.PropertySetPackage.InvalidConfiguration;

/**
 * This is the component code. This file contains the derived class where custom
 * functionality can be added to the component. You may add methods and code to
 * this class to handle property changes, respond to incoming data, and perform
 * general component housekeeping
 *
 * Source: SigGen.spd.xml
 */
public class SigGen extends SigGen_base {
	double[] data = new double[this.xfer_len.getValue()];
	double phase = 0;
	double chirp = 0;
	double sample_time_delta;
	double delta_phase;
	double delta_phase_offset;
	
	private StreamSRI sri = new StreamSRI();
    private boolean sriUpdate;
    
	/**
     * This is the component constructor. In this method, you may add additional
     * functionality to properties, such as listening for changes and handling
     * allocation, and set up internal state for your component.
     *
     * A component may listen for external changes to properties (i.e., by a
     * call to configure) using the PropertyListener interface. Listeners are
     * registered by calling addPropertyListener() on the property instance
     * with an object that implements the PropertyListener interface for that
     * data type (e.g., "PropertyListener<Float>" for a float property). More
     * than one listener can be connected to a property.
     *
     *   Example:
     *       // This example makes use of the following properties:
     *       //  - A float value called scaleValue
     *       // The file must import "org.ossie.properties.PropertyListener"
     *
     *       this.scaleValue.addPropertyListener(new PropertyListener<Float>() {
     *           public void valueChanged(Float oldValue, Float newValue) {
     *               logger.debug("Changed scaleValue " + oldValue + " to " + newValue);
     *           }
     *       });
     *
     * The recommended practice is for the implementation of valueChanged() to
     * contain only glue code to dispatch the call to a private method on the
     * component class.
     */
    public SigGen() {
        super();
        data = new double[this.xfer_len.getValue()];
		phase = 0;
		chirp = 0;
        
        sri = new StreamSRI();
        sri.hversion = 1;
		sri.mode = 0;
		sri.xdelta = 0.0;
		sri.ydelta = 1.0;
		sri.subsize = 0;
		sri.xunits = 1; // TIME_S
		sri.streamID = (this.stream_id.getValue() != null) ? this.stream_id.getValue() : "";
		sriUpdate = true;
		this.stream_id.addChangeListener(new PropertyListener<String>() {
		                 public void valueChanged(String oldValue, String newValue) {
		                     if (newValue !=null)
		                	 stream_id.setValue(newValue);
		                	 sriUpdate = true;
		                 }
		            });
	
		this.sample_rate.addChangeListener(new PropertyListener<Double>() {
			public void valueChanged(Double newValue, Double oldValue) {
				if (newValue >0)
				{
					sample_rate.setValue(newValue);
					sriUpdate = true;
				}
				else
				{
					
				}
			}
		});
		
    }
    
    public boolean hasSri(String streamID)
	{
		return Arrays.asList(port_out.activeSRIs()).contains(streamID);
	}

    /**
     *
     * Main processing function
     *
     * General functionality:
     *
     * The serviceFunction() is called repeatedly by the component's processing
     * thread, which runs independently of the main thread. Each invocation
     * should perform a single unit of work, such as reading and processing one
     * data packet.
     *
     * The return status of serviceFunction() determines how soon the next
     * invocation occurs:
     *   - NORMAL: the next call happens immediately
     *   - NOOP:   the next call happens after a pre-defined delay (100 ms)
     *   - FINISH: no more calls occur
     *
     * StreamSRI:
     *    To create a StreamSRI object, use the following code:
     *            String stream_id = "testStream";
     *            BULKIO.StreamSRI sri = new BULKIO.StreamSRI();
     *            sri.mode = 0;
     *            sri.xdelta = 0.0;
     *            sri.ydelta = 1.0;
     *            sri.subsize = 0;
     *            sri.xunits = 1; // TIME_S
     *            sri.streamID = (stream_id != null) ? stream_id : "";
     *
     * PrecisionUTCTime:
     *    To create a PrecisionUTCTime object, use the following code:
     *            BULKIO.PrecisionUTCTime tstamp = bulkio.time.utils.now();
     *
     * Ports:
     *
     *    Each port instance is accessed through members of the following form:
     *
     *        this.port_<PORT NAME>
     *
     *    Input BULKIO data is obtained by calling getPacket on the provides
     *    port. The getPacket method takes one argument: the time to wait for
     *    data to arrive, in milliseconds. A timeout of 0 causes getPacket to
     *    return immediately, while a negative timeout indicates an indefinite
     *    wait. If no data is queued and no packet arrives during the waiting
     *    period, getPacket returns null.
     *
     *    Output BULKIO data is sent by calling pushPacket on the uses port. In
     *    the case of numeric data, the pushPacket method takes a primitive
     *    array (e.g., "float[]"), a timestamp, an end-of-stream flag and a
     *    stream ID. You must make at least one call to pushSRI to associate a
     *    StreamSRI with the stream ID before calling pushPacket, or receivers
     *    may drop the data.
     *
     *    When all processing on a stream is complete, a call should be made to
     *    pushPacket with the end-of-stream flag set to "true".
     *
     *    Interactions with non-BULKIO ports are left up to the discretion of
     *    the component developer.
     *
     * Properties:
     *
     *    Properties are accessed through members of the same name; characters
     *    that are invalid for a Java identifier are replaced with "_". The
     *    current value of the property is read with getValue and written with
     *    setValue:
     *
     *        float val = this.float_prop.getValue();
     *        ...
     *        this.float_prop.setValue(1.5f);
     *
     *    Primitive data types are stored using the corresponding Java object
     *    wrapper class. For example, a property of type "float" is stored as a
     *    Float. Java will automatically box and unbox primitive types where
     *    appropriate.
     *
     *    Numeric properties support assignment via setValue from any numeric
     *    type. The standard Java type coercion rules apply (e.g., truncation
     *    of floating point values when converting to integer types).
     *
     * Example:
     *
     *    This example assumes that the component has two ports:
     *        - A bulkio.InShortPort provides (input) port called dataShort_in
     *        - A bulkio.InFloatPort uses (output) port called dataFloat_out
     *    The mapping between the port and the class is found in the component
     *    base class file.
     *    This example also makes use of the following Properties:
     *        - A float value called amplitude with a default value of 2.0
     *        - A boolean called increaseAmplitude with a default value of true
     *
     *    InShortPort.Packet data = this.port_dataShort_in.getPacket(125);
     *
     *    if (data != null) {
     *        float[] outData = new float[data.getData().length];
     *        for (int i = 0; i < data.getData().length; i++) {
     *            if (this.increaseAmplitude.getValue()) {
     *                outData[i] = (float)data.getData()[i] * this.amplitude.getValue();
     *            } else {
     *                outData[i] = (float)data.getData()[i];
     *            }
     *        }
     *
     *        // NOTE: You must make at least one valid pushSRI call
     *        if (data.sriChanged()) {
     *            this.port_dataFloat_out.pushSRI(data.getSRI());
     *        }
     *        this.port_dataFloat_out.pushPacket(outData, data.getTime(), data.getEndOfStream(), data.getStreamID());
     *    }
     *
     */
    
    protected int serviceFunction() {
			/// If the transfer length has changed, reallocate the buffer
			if (this.xfer_len.getValue() != data.length) {
				data = new double[this.xfer_len.getValue()];
				sriUpdate = true;
			}

			if (sriUpdate || (!hasSri(stream_id.getValue()))) {
				sri.streamID=stream_id.getValue();
				double xdelta = 1.0/this.sample_rate.getValue();				
				if (xdelta!= sri.xdelta)
				{
					sri.xdelta = sample_time_delta;
					sample_time_delta = (1.0/this.sample_rate.getValue());
				}
				this.port_out.pushSRI(sri);
				sriUpdate = false;
			}

			delta_phase = this.frequency.getValue() * sample_time_delta;
			delta_phase_offset = chirp * sample_time_delta * sample_time_delta;
			if ((delta_phase < 0) && (!this.shape.getValue().equals("sine"))) {
				delta_phase = -delta_phase;
			}

			// Generate the Waveform
			if (this.shape.getValue().equals("sine")) {
				Waveform.sincos(data, this.magnitude.getValue(), phase, delta_phase, data.length, 1);
			} else if (this.shape.getValue().equals("square")) {
				Waveform.square(data, this.magnitude.getValue(), phase, delta_phase, data.length, 1);
			} else if (this.shape.getValue().equals("triangle")) {
				Waveform.triangle(data, this.magnitude.getValue(), phase, delta_phase, data.length, 1);
			} else if (this.shape.getValue().equals("sawtooth")) {
				Waveform.sawtooth(data, this.magnitude.getValue(), phase, delta_phase, data.length, 1);
			} else if (this.shape.getValue().equals("pulse")) {
				Waveform.pulse(data, this.magnitude.getValue(), phase, delta_phase, data.length, 1);
			} else if (this.shape.getValue().equals("constant")) {
				Waveform.constant(data, this.magnitude.getValue(), data.length, 1);
			} else if (this.shape.getValue().equals("whitenoise")) {
				Waveform.whitenoise(data, this.magnitude.getValue(), data.length, 1);
			} else if (this.shape.getValue().equals("lrs")) {
				Waveform.lrs(data, this.magnitude.getValue(), data.length, 1, 1);
			}

			phase += delta_phase*this.xfer_len.getValue(); // increment phase
			phase -= Math.floor(phase); // modulo 1.0

			// Create a CPU time-stamp
			long tmp_time = System.currentTimeMillis();
			double wsec = tmp_time / 1000;
			double fsec = (tmp_time % 1000) / 1000.;
			PrecisionUTCTime tstamp = new PrecisionUTCTime(BULKIO.TCM_CPU.value, (short)1, (short)0, wsec, fsec);

			// Push the data
			this.port_out.pushPacket(data, 
					tstamp, 
					false, 
					sri.streamID);

			// If we are throttling, wait...otherwise run at full speed
			if (this.throttle.getValue() == true) {
				long wait_amt = (long)(this.xfer_len.getValue() * sample_time_delta * 1000);
				try {
					Thread.sleep(wait_amt);
				} catch (InterruptedException e) {
				}
			}
			return NOOP;
    }

    /**
     * Set additional options for ORB startup. For example:
     *
     *   orbProps.put("com.sun.CORBA.giop.ORBFragmentSize", Integer.toString(fragSize));
     *
     * @param orbProps
     */
    public static void configureOrb(final Properties orbProps) {
    }
}
