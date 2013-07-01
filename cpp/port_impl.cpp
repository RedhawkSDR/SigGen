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

/*******************************************************************************************

    AUTO-GENERATED CODE. DO NOT MODIFY

 	Source: SigGen.spd.xml
 	Generated on: Fri Jul 05 15:49:52 EDT 2013
 	REDHAWK IDE
 	Version: 1.8.5
 	Build id: N201307031521

*******************************************************************************************/

#include "SigGen.h"
// ----------------------------------------------------------------------------------------
// BULKIO_dataDouble_Out_i definition
// ----------------------------------------------------------------------------------------
BULKIO_dataDouble_Out_i::BULKIO_dataDouble_Out_i(std::string port_name, SigGen_base *_parent) :
Port_Uses_base_impl(port_name)
{
    parent = static_cast<SigGen_i *> (_parent);
    recConnectionsRefresh = false;
    recConnections.length(0);
}

BULKIO_dataDouble_Out_i::~BULKIO_dataDouble_Out_i()
{
}

/*
 * pushSRI
 *     description: send out SRI describing the data payload
 *
 *  H: structure of type BULKIO::StreamSRI with the SRI for this stream
 *    hversion
 *    xstart: start time of the stream
 *    xdelta: delta between two samples
 *    xunits: unit types from Platinum specification
 *    subsize: 0 if the data is one-dimensional
 *    ystart
 *    ydelta
 *    yunits: unit types from Platinum specification
 *    mode: 0-scalar, 1-complex
 *    streamID: stream identifier
 *    sequence<CF::DataType> keywords: unconstrained sequence of key-value pairs for additional description
 */
void BULKIO_dataDouble_Out_i::pushSRI(const BULKIO::StreamSRI& H)
{
    std::vector < std::pair < BULKIO::dataDouble_var, std::string > >::iterator i;

    boost::mutex::scoped_lock lock(updatingPortsLock);   // don't want to process while command information is coming in

    if (active) {
        for (i = outConnections.begin(); i != outConnections.end(); ++i) {
            try {
                ((*i).first)->pushSRI(H);
            } catch(...) {
                std::cout << "Call to pushSRI by BULKIO_dataDouble_Out_i failed" << std::endl;
            }
        }
    }

    currentSRIs[std::string(H.streamID)] = H;
    refreshSRI = false;

    return;
}



