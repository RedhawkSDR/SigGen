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
/**************************************************************************

    This is the component code. This file contains the child class where
    custom functionality can be added to the component. Custom
    functionality to the base class can be extended here. Access to
    the ports can also be done from this class

**************************************************************************/

#include "SigGen.h"
#include "Waveform.h"
#include <cmath>
#include <sys/time.h>

PREPARE_LOGGING(SigGen_i)

SigGen_i::SigGen_i(const char *uuid, const char *label) :
    SigGen_base(uuid, label)
{
	last_xfer_len = xfer_len;
	data.resize(xfer_len);
	phase = 0;
	chirp = 0;

	sri = BULKIO::StreamSRI();
	sri.hversion = 1;
	sri.xstart = 0.0;
	sri.xdelta = 0.0;
	sri.xunits = BULKIO::UNITS_TIME;
	sri.subsize = 0;
	sri.ystart = 0.0;
	sri.ydelta = 0.0;
	sri.yunits = BULKIO::UNITS_NONE;
	sri.mode = 0;
	sri.streamID = this->stream_id.c_str();
	sriUpdate = true;

	setPropertyChangeListener("stream_id", this, &SigGen_i::streamIdChanged);
}


SigGen_i::~SigGen_i()
{
}

/***********************************************************************************************

    Basic functionality:

        The service function is called by the serviceThread object (of type ProcessThread).
        This call happens immediately after the previous call if the return value for
        the previous call was NORMAL.
        If the return value for the previous call was NOOP, then the serviceThread waits
        an amount of time defined in the serviceThread's constructor.
        
    SRI:
        To create a StreamSRI object, use the following code:
                std::string stream_id = "testStream";
                BULKIO::StreamSRI sri = bulkio::sri::create(stream_id);

	Time:
	    To create a PrecisionUTCTime object, use the following code:
                BULKIO::PrecisionUTCTime tstamp = bulkio::time::utils::now();

        
    Ports:

        Data is passed to the serviceFunction through the getPacket call (BULKIO only).
        The dataTransfer class is a port-specific class, so each port implementing the
        BULKIO interface will have its own type-specific dataTransfer.

        The argument to the getPacket function is a floating point number that specifies
        the time to wait in seconds. A zero value is non-blocking. A negative value
        is blocking.  Constants have been defined for these values, bulkio::Const::BLOCKING and
        bulkio::Const::NON_BLOCKING.

        Each received dataTransfer is owned by serviceFunction and *MUST* be
        explicitly deallocated.

        To send data using a BULKIO interface, a convenience interface has been added 
        that takes a std::vector as the data input

        NOTE: If you have a BULKIO dataSDDS port, you must manually call 
              "port->updateStats()" to update the port statistics when appropriate.

        Example:
            // this example assumes that the component has two ports:
            //  A provides (input) port of type bulkio::InShortPort called short_in
            //  A uses (output) port of type bulkio::OutFloatPort called float_out
            // The mapping between the port and the class is found
            // in the component base class header file

            bulkio::InShortPort::dataTransfer *tmp = short_in->getPacket(bulkio::Const::BLOCKING);
            if (not tmp) { // No data is available
                return NOOP;
            }

            std::vector<float> outputData;
            outputData.resize(tmp->dataBuffer.size());
            for (unsigned int i=0; i<tmp->dataBuffer.size(); i++) {
                outputData[i] = (float)tmp->dataBuffer[i];
            }

            // NOTE: You must make at least one valid pushSRI call
            if (tmp->sriChanged) {
                float_out->pushSRI(tmp->SRI);
            }
            float_out->pushPacket(outputData, tmp->T, tmp->EOS, tmp->streamID);

            delete tmp; // IMPORTANT: MUST RELEASE THE RECEIVED DATA BLOCK
            return NORMAL;

        If working with complex data (i.e., the "mode" on the SRI is set to
        true), the std::vector passed from/to BulkIO can be typecast to/from
        std::vector< std::complex<dataType> >.  For example, for short data:

            bulkio::InShortPort::dataTransfer *tmp = myInput->getPacket(bulkio::Const::BLOCKING);
            std::vector<std::complex<short> >* intermediate = (std::vector<std::complex<short> >*) &(tmp->dataBuffer);
            // do work here
            std::vector<short>* output = (std::vector<short>*) intermediate;
            myOutput->pushPacket(*output, tmp->T, tmp->EOS, tmp->streamID);

        Interactions with non-BULKIO ports are left up to the component developer's discretion

    Properties:
        
        Properties are accessed directly as member variables. For example, if the
        property name is "baudRate", it may be accessed within member functions as
        "baudRate". Unnamed properties are given a generated name of the form
        "prop_n", where "n" is the ordinal number of the property in the PRF file.
        Property types are mapped to the nearest C++ type, (e.g. "string" becomes
        "std::string"). All generated properties are declared in the base class
        (SigGen_base).
    
        Simple sequence properties are mapped to "std::vector" of the simple type.
        Struct properties, if used, are mapped to C++ structs defined in the
        generated file "struct_props.h". Field names are taken from the name in
        the properties file; if no name is given, a generated name of the form
        "field_n" is used, where "n" is the ordinal number of the field.
        
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            //  - A boolean called scaleInput
              
            if (scaleInput) {
                dataOut[i] = dataIn[i] * scaleValue;
            } else {
                dataOut[i] = dataIn[i];
            }
            
        A callback method can be associated with a property so that the method is
        called each time the property value changes.  This is done by calling 
        setPropertyChangeListener(<property name>, this, &SigGen_i::<callback method>)
        in the constructor.
            
        Example:
            // This example makes use of the following Properties:
            //  - A float value called scaleValue
            
        //Add to SigGen.cpp
        SigGen_i::SigGen_i(const char *uuid, const char *label) :
            SigGen_base(uuid, label)
        {
            setPropertyChangeListener("scaleValue", this, &SigGen_i::scaleChanged);
        }

        void SigGen_i::scaleChanged(const std::string& id){
            std::cout << "scaleChanged scaleValue " << scaleValue << std::endl;
        }
            
        //Add to SigGen.h
        void scaleChanged(const std::string&);
        
        
************************************************************************************************/
int SigGen_i::serviceFunction()
{
	if (stream_id.empty()){
		stream_id = "";
		sri.streamID = stream_id.c_str();
	}

	if ((xfer_len != last_xfer_len) || ((size_t) xfer_len != data.size())) {
		last_xfer_len = xfer_len;
		data.resize(xfer_len);
		sriUpdate = true;
	}

	sample_time_delta = 1.0/sample_rate;
	if ((sample_time_delta > (sri.xdelta*1.0000001))||(sample_time_delta < (sri.xdelta*0.999999))){
		sri.xdelta = sample_time_delta;
		sriUpdate = true;
	}

	if (sriUpdate) {
		out->pushSRI(sri);
		sriUpdate = false;
	}

	delta_phase = frequency * sample_time_delta;
	delta_phase_offset = chirp * sample_time_delta * sample_time_delta;
	if ((delta_phase < 0) && (!shape.compare("sine"))) {
		delta_phase = -delta_phase;
	}

	// Generate the Waveform
	if (shape == "sine"){
		Waveform::sincos(data, magnitude, phase, delta_phase, xfer_len, 1);
	} else if (shape == "square"){
		Waveform::square(data, magnitude, phase, delta_phase, xfer_len, 1);
	} else if (shape == "triangle") {
		Waveform::triangle(data, magnitude, phase, delta_phase, xfer_len, 1);
	} else if (shape == "sawtooth") {
		Waveform::sawtooth(data, magnitude, phase, delta_phase, xfer_len, 1);
	} else if (shape == "pulse") {
		Waveform::pulse(data, magnitude, phase, delta_phase, xfer_len, 1);
	} else if (shape == "constant") {
		Waveform::constant(data, magnitude, xfer_len, 1);
	} else if (shape == "whitenoise") {
		Waveform::whitenoise(data, magnitude, xfer_len, 1);
	} else if (shape == "lrs") {
		Waveform::lrs(data, magnitude, xfer_len, 1, 1);
	}

	phase += delta_phase*xfer_len; // increment phase
	phase -= floor(phase); // modulo 1.0

	struct timeval tmp_time;
	struct timezone tmp_tz;
	gettimeofday(&tmp_time, &tmp_tz);
	double wsec = tmp_time.tv_sec;
	double fsec = tmp_time.tv_usec / 1e6;;
	//std::cout << "time: " << wsec << " microseconds: " << fsec << std::endl;

	BULKIO::PrecisionUTCTime tstamp = BULKIO::PrecisionUTCTime();
	tstamp.tcmode = BULKIO::TCM_CPU;
	tstamp.tcstatus = (short)1;
	tstamp.toff = 0.0;
	tstamp.twsec = wsec;
	tstamp.tfsec = fsec;

	// Push the data
	out->pushPacket(data, tstamp, false, stream_id);

	// If we are throttling, wait...otherwise run at full speed
	if (throttle == true) {
		long wait_amt_usec = (long)(xfer_len * sample_time_delta * 1000000.0);
		try {
			usleep(wait_amt_usec);
		} catch (...) {
			return NORMAL;
		}
	}

	return NORMAL;
}

void SigGen_i::streamIdChanged(const std::string& id){
	sri.streamID = stream_id.c_str();
	sriUpdate = true;
}

