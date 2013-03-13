/*
 * This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
 * source distribution.
 * 
 * This file is part of REDHAWK Basic Components.
 * 
 * REDHAWK Basic Components is free software: you can redistribute it and/or modify it under the terms of 
 * the GNU Lesser General Public License as published by the Free Software Foundation, either 
 * version 3 of the License, or (at your option) any later version.
 * 
 * REDHAWK Basic Components is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
 * PURPOSE.  See the GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License along with this 
 * program.  If not, see http://www.gnu.org/licenses/.
 */
package SigGen.java;


import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import org.omg.CORBA.ORB;
import org.omg.PortableServer.POA;
import org.omg.PortableServer.POAPackage.ServantNotActive;
import org.omg.PortableServer.POAPackage.WrongPolicy;
import org.omg.CosNaming.NamingContextPackage.CannotProceed;
import org.omg.CosNaming.NamingContextPackage.InvalidName;
import org.omg.CosNaming.NamingContextPackage.NotFound;
import CF.PropertiesHolder;
import CF.ResourceHelper;
import CF.UnknownProperties;
import CF.LifeCyclePackage.InitializeError;
import CF.LifeCyclePackage.ReleaseError;
import CF.InvalidObjectReference;
import CF.PropertySetPackage.InvalidConfiguration;
import CF.PropertySetPackage.PartialConfiguration;
import CF.ResourcePackage.StartError;
import CF.ResourcePackage.StopError;
import CF.DataType;

import org.omg.CORBA.UserException;
import org.omg.CosNaming.NameComponent;
import org.apache.log4j.Logger;
import org.ossie.component.*;
import org.ossie.properties.*;
import SigGen.java.ports.*;

import BULKIO.PrecisionUTCTime;
import BULKIO.StreamSRI;

/**
 * This is the component code. This file contains all the access points
 * you need to use to be able to access all input and output ports,
 * respond to incoming data, and perform general component housekeeping
 *
 * Source: SigGen.spd.xml
 * Generated on: Wed Feb 27 14:15:15 EST 2013
 * Redhawk IDE
 * Version:M.1.8.3
 * Build id: v201302191304 
 
 * @generated
 */
public class SigGen extends Resource implements Runnable {
    /**
     * @generated
     */
    public final static Logger logger = Logger.getLogger(SigGen.class.getName());
    
	/**
	 * The property frequency
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<Double> frequency =
		new SimpleProperty<Double>(
			"frequency", //id
			null, //name
			"double", //type
			1000.0, //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			);
    
	/**
	 * The property sample_rate
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<Double> sample_rate =
		new SimpleProperty<Double>(
			"sample_rate", //id
			null, //name
			"double", //type
			5000.0, //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			);
    
	/**
	 * The property magnitude
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<Double> magnitude =
		new SimpleProperty<Double>(
			"magnitude", //id
			null, //name
			"double", //type
			1.0, //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			);
    
	/**
	 * The property shape
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<String> shape =
		new SimpleProperty<String>(
			"shape", //id
			null, //name
			"string", //type
			"sine", //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			);
    
	/**
	 * The property xfer_len
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<Integer> xfer_len =
		new SimpleProperty<Integer>(
			"xfer_len", //id
			null, //name
			"long", //type
			1000, //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			);

	/**
	 * The property throttle
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<Boolean> throttle =
		new SimpleProperty<Boolean>(
			"throttle", //id
			null, //name
			"boolean", //type
			true, //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			);
    
	/**
	 * The property stream_id
	 * If the meaning of this property isn't clear, a description should be added.
	 * 
	 * <!-- begin-user-doc -->
	 * <!-- end-user-doc -->
	 * @generated
	 */
	public final SimpleProperty<String> stream_id =
		new SimpleProperty<String>(
			"stream_id", //id
			null, //name
			"string", //type
			"SigGen Stream", //default value
			"readwrite", //mode
			"external", //action
			new String[] {"configure"} //kind
			); 
    // Provides/inputs

    // Uses/outputs
    public class MyBULKIO_dataDoubleOutPort extends BULKIO_dataDoubleOutPort
    {
    	public MyBULKIO_dataDoubleOutPort(String portName) {
			super(portName);
		}

		public boolean hasSri(String streamID)
    	{
    		return this.currentSRIs.containsKey(streamID);
    	}
    };
	
	/**
     * @generated
     */
    public MyBULKIO_dataDoubleOutPort port_out;

    /**
     * @generated
     */
    public SigGen() 
    {
        super();                
        addProperty(frequency);
        addProperty(sample_rate);
        addProperty(magnitude);
        addProperty(shape);
        addProperty(xfer_len);
        addProperty(throttle);
        addProperty(stream_id);

        // Provides/input

        // Uses/output
        this.port_out = new MyBULKIO_dataDoubleOutPort("out");
        this.addPort("out", this.port_out);
    
       //begin-user-code
       //end-user-code
    }

    //begin-user-code
    private StreamSRI sri = new StreamSRI();
    private boolean sriUpdate;
    //end-user-code
    /**
     *
     * Main processing thread
     *
     * General functionality:
     *    This function is running as a separate thread from the component's main thread. 
     * 
     * @generated
     */
    public void run() 
    {
        //begin-user-code
    	double[] data = new double[this.xfer_len.getValue()];
		double phase = 0;
		double chirp = 0;
		double sample_time_delta;
		double delta_phase;
		double delta_phase_offset;

		sri = new StreamSRI();
		sri.hversion = 1;
		sri.mode = 0;
		sri.xdelta = 0.0;
		sri.ydelta = 1.0;
		sri.subsize = 0;
		sri.xunits = 1; // TIME_S
		sri.streamID = (this.stream_id.getValue() != null) ? this.stream_id.getValue() : "";
		sriUpdate = true;
        //end-user-code
        
        while(this.started())
        {
            //begin-user-code
        	try {
				/// If the transfer length has changed, reallocate the buffer
				if (this.xfer_len.getValue() != data.length) {
					data = new double[this.xfer_len.getValue()];
					sriUpdate = true;
				}

				sample_time_delta = (1.0/this.sample_rate.getValue());
				if (sample_time_delta != sri.xdelta) {
					sri.xdelta = sample_time_delta;
					sriUpdate = true;
				}

				if (sriUpdate || (!this.port_out.hasSri(sri.streamID))) {
					this.port_out.pushSRI(sri);
				}
				sriUpdate = false;

				delta_phase = this.frequency.getValue() * sample_time_delta;
				delta_phase_offset = chirp * sample_time_delta * sample_time_delta;
				if ((delta_phase < 0) && (!this.shape.getValue().equals("sine"))) {
					delta_phase = -delta_phase;
				}

				// Generate the Waveform
				if (this.shape.getValue().equals("sine")) {
					Waveform.sincos(data, this.magnitude.getValue(), phase, delta_phase, this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("square")) {
					Waveform.square(data, this.magnitude.getValue(), phase, delta_phase, this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("triangle")) {
					Waveform.triangle(data, this.magnitude.getValue(), phase, delta_phase, this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("sawtooth")) {
					Waveform.sawtooth(data, this.magnitude.getValue(), phase, delta_phase, this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("pulse")) {
					Waveform.pulse(data, this.magnitude.getValue(), phase, delta_phase, this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("constant")) {
					Waveform.constant(data, this.magnitude.getValue(), this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("whitenoise")) {
					Waveform.whitenoise(data, this.magnitude.getValue(), this.xfer_len.getValue(), 1);
				} else if (this.shape.getValue().equals("lrs")) {
					Waveform.lrs(data, this.magnitude.getValue(), this.xfer_len.getValue(), 1, 1);
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
						(this.stream_id.getValue() != null) ? this.stream_id.getValue() : "");

				// If we are throttling, wait...otherwise run at full speed
				if (this.throttle.getValue() == true) {
					long wait_amt = (long)(this.xfer_len.getValue() * sample_time_delta * 1000);
					try {
						Thread.sleep(wait_amt);
					} catch (InterruptedException e) {
						break;
					}
				}
			} catch (Throwable t) {
				logger.error("Error in processing loop", t);
			}
            //end-user-code
        }
        
        //begin-user-code
        //end-user-code
    }
        
    /**
     * The main function of your component.  If no args are provided, then the
     * CORBA object is not bound to an SCA Domain or NamingService and can
     * be run as a standard Java application.
     * 
     * @param args
     * @generated
     */
    public static void main(String[] args) 
    {
        final Properties orbProps = new Properties();

        //begin-user-code
        // TODO You may add extra startup code here, for example:
        // orbProps.put("com.sun.CORBA.giop.ORBFragmentSize", Integer.toString(fragSize));
        //end-user-code

        try {
            Resource.start_component(SigGen.class, args, orbProps);
        } catch (InvalidObjectReference e) {
            e.printStackTrace();
        } catch (NotFound e) {
            e.printStackTrace();
        } catch (CannotProceed e) {
            e.printStackTrace();
        } catch (InvalidName e) {
            e.printStackTrace();
        } catch (ServantNotActive e) {
            e.printStackTrace();
        } catch (WrongPolicy e) {
            e.printStackTrace();
        } catch (InstantiationException e) {
            e.printStackTrace();
        } catch (IllegalAccessException e) {
            e.printStackTrace();
        }

        //begin-user-code
        // TODO You may add extra shutdown code here
        //end-user-code
    }
    

    //begin-user-code
    @Override
    public void configure(DataType[] configProperties)
    		throws InvalidConfiguration, PartialConfiguration {
    	super.configure(configProperties);
    	
    	for (int i=0; i < configProperties.length; i++) {
    		if (configProperties[i].id.equals("stream_id")) {
    			sri.streamID = stream_id.getValue();
    			sriUpdate = true;
    		}
    	}
    }
    //end-user-code
}