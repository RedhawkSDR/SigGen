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
#include "SigGen_base.h"

/*******************************************************************************************

    AUTO-GENERATED CODE. DO NOT MODIFY

    The following class functions are for the base class for the component class. To
    customize any of these functions, do not modify them here. Instead, overload them
    on the child class

******************************************************************************************/

SigGen_base::SigGen_base(const char *uuid, const char *label) :
    Resource_impl(uuid, label),
    ThreadedComponent()
{
    loadProperties();

    out = new bulkio::OutDoublePort("out");
    addPort("out", out);
}

SigGen_base::~SigGen_base()
{
    delete out;
    out = 0;
}

/*******************************************************************************************
    Framework-level functions
    These functions are generally called by the framework to perform housekeeping.
*******************************************************************************************/
void SigGen_base::start() throw (CORBA::SystemException, CF::Resource::StartError)
{
    Resource_impl::start();
    ThreadedComponent::startThread();
}

void SigGen_base::stop() throw (CORBA::SystemException, CF::Resource::StopError)
{
    Resource_impl::stop();
    if (!ThreadedComponent::stopThread()) {
        throw CF::Resource::StopError(CF::CF_NOTSET, "Processing thread did not die");
    }
}

void SigGen_base::releaseObject() throw (CORBA::SystemException, CF::LifeCycle::ReleaseError)
{
    // This function clears the component running condition so main shuts down everything
    try {
        stop();
    } catch (CF::Resource::StopError& ex) {
        // TODO - this should probably be logged instead of ignored
    }

    Resource_impl::releaseObject();
}

void SigGen_base::loadProperties()
{
    addProperty(frequency,
                1000,
                "frequency",
                "",
                "readwrite",
                "Hz",
                "external",
                "configure");

    addProperty(sample_rate,
                5000,
                "sample_rate",
                "",
                "readwrite",
                "Hz",
                "external",
                "configure");

    addProperty(magnitude,
                1.0,
                "magnitude",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(shape,
                "sine",
                "shape",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(xfer_len,
                1000,
                "xfer_len",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(throttle,
                true,
                "throttle",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(stream_id,
                "SigGen Stream",
                "stream_id",
                "",
                "readwrite",
                "",
                "external",
                "configure");

    addProperty(chan_rf,
                -1,
                "chan_rf",
                "",
                "readwrite",
                "Hz",
                "external",
                "configure");

    addProperty(col_rf,
                -1,
                "col_rf",
                "",
                "readwrite",
                "Hz",
                "external",
                "configure");

}


