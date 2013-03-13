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

/**************************************************************************

    This is the component code. This file contains the child class where
    custom functionality can be added to the component. Custom
    functionality to the base class can be extended here. Access to
    the ports can also be done from this class

 	Source: SigGen.spd.xml
 	Generated on: Wed Feb 27 14:15:06 EST 2013
 	Redhawk IDE
 	Version:M.1.8.3
 	Build id: v201302191304

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

	if (sriUpdate || (out->currentSRIs.count(stream_id)==0)){
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
