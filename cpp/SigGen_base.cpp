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


#include "SigGen_base.h"

/*******************************************************************************************

    AUTO-GENERATED CODE. DO NOT MODIFY
    
 	Source: SigGen.spd.xml
 	Generated on: Fri Jul 05 15:49:52 EDT 2013
 	REDHAWK IDE
 	Version: 1.8.5
 	Build id: N201307031521

*******************************************************************************************/

/******************************************************************************************

    The following class functions are for the base class for the component class. To
    customize any of these functions, do not modify them here. Instead, overload them
    on the child class

******************************************************************************************/
 
SigGen_base::SigGen_base(const char *uuid, const char *label) :
                                     Resource_impl(uuid, label), serviceThread(0) {
    construct();
}

void SigGen_base::construct()
{
    Resource_impl::_started = false;
    loadProperties();
    serviceThread = 0;
    
    PortableServer::ObjectId_var oid;
    out = new BULKIO_dataDouble_Out_i("out", this);
    oid = ossie::corba::RootPOA()->activate_object(out);

    registerOutPort(out, out->_this());
}

/*******************************************************************************************
    Framework-level functions
    These functions are generally called by the framework to perform housekeeping.
*******************************************************************************************/
void SigGen_base::initialize() throw (CF::LifeCycle::InitializeError, CORBA::SystemException)
{
}

void SigGen_base::start() throw (CORBA::SystemException, CF::Resource::StartError)
{
    boost::mutex::scoped_lock lock(serviceThreadLock);
    if (serviceThread == 0) {
        serviceThread = new ProcessThread<SigGen_base>(this, 0.1);
        serviceThread->start();
    }
    
    if (!Resource_impl::started()) {
    	Resource_impl::start();
    }
}

void SigGen_base::stop() throw (CORBA::SystemException, CF::Resource::StopError)
{
    boost::mutex::scoped_lock lock(serviceThreadLock);
    // release the child thread (if it exists)
    if (serviceThread != 0) {
        if (!serviceThread->release(2)) {
            throw CF::Resource::StopError(CF::CF_NOTSET, "Processing thread did not die");
        }
        serviceThread = 0;
    }
    
    if (Resource_impl::started()) {
    	Resource_impl::stop();
    }
}

CORBA::Object_ptr SigGen_base::getPort(const char* _id) throw (CORBA::SystemException, CF::PortSupplier::UnknownPort)
{

    std::map<std::string, Port_Provides_base_impl *>::iterator p_in = inPorts.find(std::string(_id));
    if (p_in != inPorts.end()) {

    }

    std::map<std::string, CF::Port_var>::iterator p_out = outPorts_var.find(std::string(_id));
    if (p_out != outPorts_var.end()) {
        return CF::Port::_duplicate(p_out->second);
    }

    throw (CF::PortSupplier::UnknownPort());
}

void SigGen_base::releaseObject() throw (CORBA::SystemException, CF::LifeCycle::ReleaseError)
{
    // This function clears the component running condition so main shuts down everything
    try {
        stop();
    } catch (CF::Resource::StopError& ex) {
        // TODO - this should probably be logged instead of ignored
    }

    // deactivate ports
    releaseInPorts();
    releaseOutPorts();

    delete(out);
 
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

}
