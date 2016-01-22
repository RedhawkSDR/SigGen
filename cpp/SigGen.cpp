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
	phase = 0;
	delta_phase = 0.0;

	sri = BULKIO::StreamSRI();
	sri.hversion = 1;
	sri.xstart = 0.0;
	sri.xdelta = 1.0/sample_rate;;
	sri.xunits = BULKIO::UNITS_TIME;
	sri.subsize = 0;
	sri.ystart = 0.0;
	sri.ydelta = 0.0;
	sri.yunits = BULKIO::UNITS_NONE;
	sri.mode = 0;
	sri.blocking = sri_blocking;
	sri.streamID = stream_id.c_str();
	keywordUpdate(NULL, NULL);
	sriUpdate = true;
	stream_created = false;
	eos_stream_id.clear();

	addPropertyChangeListener("stream_id", this, &SigGen_i::stream_idChanged);
	addPropertyChangeListener("chan_rf", this, &SigGen_i::keywordUpdate);
	addPropertyChangeListener("col_rf", this, &SigGen_i::keywordUpdate);
	addPropertyChangeListener("sri_blocking", this, &SigGen_i::sri_blockingChanged);
	addPropertyChangeListener("sample_rate", this, &SigGen_i::samplerateChanged);

}


SigGen_i::~SigGen_i()
{
}

void SigGen_i::start() throw (CF::Resource::StartError, CORBA::SystemException) {
	if (!started()){
		nextTime = bulkio::time::utils::now();
	}
	SigGen_base::start();
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
	{
		// Cache/update from props and class vars that we do not want changing during execution
		boost::mutex::scoped_lock lock(sigGenLock_);

		if (sriUpdate) {
			sriUpdate = false;
			cache.sriUpdate = true;

			if (stream_id.empty()){
				stream_id = uuidGenerator();
				sri.streamID = stream_id.c_str();
			}

			if (cache.stream_id != stream_id && stream_created){
				// We need to send an EOS for cache.stream_id,
				// but wait until we release the mutex
				eos_stream_id = cache.stream_id;
			}

			cache.sri = sri;
			cache.stream_id = stream_id;
		}

		cache.xfer_len = xfer_len;
		cache.shape = shape;
		delta_phase = frequency * cache.sri.xdelta;
	}

	if (!eos_stream_id.empty()) {
		dataFloat_out->pushPacket(std::vector<float>(), nextTime, true, eos_stream_id);
		dataShort_out->pushPacket(std::vector<short>(), nextTime, true, eos_stream_id);
		eos_stream_id.clear();
	}

	if (((size_t) cache.xfer_len != floatData.size()) || ((size_t) cache.xfer_len != shortData.size())) {
		floatData.resize(cache.xfer_len);
		shortData.resize(cache.xfer_len);
	}

	if (cache.sriUpdate) {
		cache.sriUpdate = false;
		stream_created = true;
		dataFloat_out->pushSRI(cache.sri);
		dataShort_out->pushSRI(cache.sri);
	} else {
		if (!dataFloat_out->getCurrentSRI().count(cache.stream_id))
			dataFloat_out->pushSRI(cache.sri);
		if (!dataShort_out->getCurrentSRI().count(cache.stream_id))
			dataShort_out->pushSRI(cache.sri);
	}

	if ((delta_phase < 0) && (cache.shape != "sine")) {
		delta_phase = -delta_phase;
	}

	// Generate the Waveform
	if (cache.shape == "sine"){
		Waveform::sincos(floatData, magnitude, phase, delta_phase, cache.xfer_len, 1);
	} else if (cache.shape == "square"){
		Waveform::square(floatData, magnitude, phase, delta_phase, cache.xfer_len, 1);
	} else if (cache.shape == "triangle") {
		Waveform::triangle(floatData, magnitude, phase, delta_phase, cache.xfer_len, 1);
	} else if (cache.shape == "sawtooth") {
		Waveform::sawtooth(floatData, magnitude, phase, delta_phase, cache.xfer_len, 1);
	} else if (cache.shape == "pulse") {
		Waveform::pulse(floatData, magnitude, phase, delta_phase, cache.xfer_len, 1);
	} else if (cache.shape == "constant") {
		Waveform::constant(floatData, magnitude, cache.xfer_len, 1);
	} else if (cache.shape == "whitenoise") {
		Waveform::whitenoise(floatData, magnitude, cache.xfer_len, 1);
	} else if (cache.shape == "lrs") {
		Waveform::lrs(floatData, magnitude, cache.xfer_len, 1, 1);
	}

	phase += delta_phase * cache.xfer_len; // increment phase
	phase -= floor(phase); // modulo 1.0

	// Push the data
	dataFloat_out->pushPacket(floatData, nextTime, false, cache.stream_id);
	convertFloat2short(floatData, shortData);
	dataShort_out->pushPacket(shortData, nextTime, false, cache.stream_id);

	// Advance time
	nextTime.tfsec += cache.xfer_len * cache.sri.xdelta;
	if (nextTime.tfsec > 1.0) {
		nextTime.tfsec -= 1.0;
		nextTime.twsec += 1.0;
	}

	// If we are throttling, wait...otherwise run at full speed
	if (throttle == true) {
		long wait_amt_usec = (long)(cache.xfer_len * cache.sri.xdelta * 1000000.0);
		try {
			usleep(wait_amt_usec);
		} catch (...) {
			return NORMAL;
		}
	}

	return NORMAL;
}

// Convert the float vector of data to a scaled short vector
void SigGen_i::convertFloat2short(std::vector<float>& src, std::vector<short>& dst) {
	int minShort = std::numeric_limits<short>::min();
	int maxShort = std::numeric_limits<short>::max();

	for (size_t i = 0; i < dst.size(); i++ ) {
		dst[i] = (short)std::min(maxShort, std::max(minShort, (int)src[i]));
	}
}

// Property Change Listeners

void SigGen_i::stream_idChanged(const std::string *oldValue, const std::string *newValue)
{
	if (*oldValue == *newValue) {
		std::cerr << "This can happen!?!";
		return;
	}

	boost::mutex::scoped_lock lock(sigGenLock_);
	sri.streamID = stream_id.c_str();
	sriUpdate = true;
}

void SigGen_i::keywordUpdate(const double *oldValue, const double *newValue)
{
	boost::mutex::scoped_lock lock(sigGenLock_);

	sri.keywords.length(0);
	int index = 0;

	if (this->chan_rf != -1.0) {
		sri.keywords.length(index + 1);
		sri.keywords[index].id = "CHAN_RF";
		sri.keywords[index].value <<= this->chan_rf;
		index++;
	}
	if (this->col_rf != -1.0) {
		sri.keywords.length(index + 1);
		sri.keywords[index].id = "COL_RF";
		sri.keywords[index].value <<= this->col_rf;
		index++;
	}

	sriUpdate = true;
}

// Update the sri_blocking property
void SigGen_i::sri_blockingChanged(const bool *oldValue, const bool *newValue)
{
	boost::mutex::scoped_lock lock(sigGenLock_);
	sri.blocking = sri_blocking;
	sriUpdate = true;
}

// Update sri.xdelta
void SigGen_i::samplerateChanged(const double *oldValue, const double *newValue)
{
	boost::mutex::scoped_lock lock(sigGenLock_);
	sri.xdelta = 1.0/sample_rate;
	sriUpdate = true;
}
