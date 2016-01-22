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

#ifndef SIGGEN_IMPL_H
#define SIGGEN_IMPL_H

#include "SigGen_base.h"
#include <uuid/uuid.h>

class SigGen_i;

/* Struct used to cache props and class members that are used in the ServiceFunction
 * And updated outside of the ServiceFunction
 * Note: not all props/member vars are cached. Those that are used (read) once and are
 * not inter-dependent on other vars are not cached.
 */
struct SigGenCache {
	SigGenCache(){
		xfer_len=0;
		shape="sine";
		sriUpdate=true;
	};

	long xfer_len;
	std::string shape;
	std::string stream_id;
	BULKIO::StreamSRI sri;
	bool sriUpdate;
};

inline std::string uuidGenerator() {
    uuid_t new_random_uuid;
    uuid_generate_random(new_random_uuid);
    char new_random_uuid_str[37];
    uuid_unparse(new_random_uuid, new_random_uuid_str);
    return std::string(new_random_uuid_str);
};

class SigGen_i : public SigGen_base
{
    ENABLE_LOGGING
    public:
        SigGen_i(const char *uuid, const char *label);
        ~SigGen_i();
        int serviceFunction();
        void start() throw (CF::Resource::StartError, CORBA::SystemException);

    private:
        boost::mutex sigGenLock_;
        bool stream_created;
        std::string eos_stream_id;

        void stream_idChanged(const std::string *oldValue, const std::string *newValue);
        void keywordUpdate(const double *oldValue, const double *newValue);
        void sri_blockingChanged(const bool *oldValue, const bool *newValue);
        void samplerateChanged(const double *oldValue, const double *newValue);
        void convertFloat2short(std::vector<float>& src, std::vector<short>& dst);

        std::vector<float> floatData;
        std::vector<short> shortData;
    	double phase;
    	double delta_phase;
    	BULKIO::StreamSRI sri;
    	bool sriUpdate;
        BULKIO::PrecisionUTCTime nextTime;

        SigGenCache cache;

};

#endif
