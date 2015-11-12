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
/*
 * Waveform.cpp
 *  - Based off of code imported from NextMIDAS
 *
 */

#include <cmath>

namespace Waveform{


	const static double A = 67081293.0;
	const static double B = 14181771.0;
	const static double T26 = 67108864.0;
	const static double BI = B/T26;
	long seed = 123456789;

	// Pre-calculate some useful constants
	const static double TWOPI = M_PI * 2;
	const static double HALFPI = M_PI / 2.0;

	/** Binary variant of a Giga. Note that this differs from the typical version
	  (the decimal) version of Giga which is 10<sup>9</sup>.<br>
	  <br>
	  Value: <code>{@value} = 1G = 2<sup>30</sup></code><br>
	 */
	const static int B1G  = 1073741824;

	/** Set the seed used in white noise waveform generation */
	void setSeed (int value) {
		if (value>0) seed = value;
	}

	/** Create a white noise FLOAT array of given magnitude
		  @param fbuf The output array
		  @param sdev Standard deviation
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void whitenoise(std::vector<float>& fbuf, double sdev, int n, int spa) {
		double v1,v2,sum;
		double sis=((double)seed)/T26;
		double factor = -2.0 / log(10.0);
		for (int i=0; i<n*spa;) {
			sis = sis*A + BI;
			sis = sis - (double)(int)sis;
			v1 = sis+sis-1;
			sis = sis*A + BI;
			sis = sis - (double)(int)sis;
			v2 = sis+sis-1;
			sum = v1*v1 + v2*v2;
			if (sum>=1.0) continue;
			sum = sdev * sqrt(factor*log(sum)/sum);
			//      sum = sdev * Native.sqrtf(factor*Native.logf(sum)/sum);
			fbuf[i++] =(float) v1*sum;
			if(i<n*spa){
				fbuf[i++] =(float) v2*sum;
			}
		}
		seed = (int)(sis*T26);
	}

	/** Create a white noise DOUBLE array of given magnitude
		  @param dbuf The output array
		  @param sdev Standard deviation
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void whitenoise (std::vector<double>& dbuf, double sdev, int n, int spa) {
		double v1,v2,sum;
		double sis=((double)seed)/T26;
		double factor = -2.0 / log(10.0);
		for (int i=0; i<n*spa;) {
			sis = sis*A + BI;
			sis = sis - (double)(int)sis;
			v1 = sis+sis-1;
			sis = sis*A + BI;
			sis = sis - (double)(int)sis;
			v2 = sis+sis-1;
			sum = v1*v1 + v2*v2;
			if (sum>=1.0) continue;
			sum = sdev * sqrt(factor*log(sum)/sum);
			dbuf[i++] = v1*sum;
			if(i<n*spa){
				dbuf[i++] = v2*sum;
			}
		}
		seed = (int)(sis*T26);
	}

	/** Create a SIN or COSINE FLOAT array of given magnitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	/*
	 *  fast algorithm based on:  sin(x+dp) = sin(x)*cos(dp) + cos(x)*sin(dp)
	 *                            cos(x+dp) = cos(x)*cos(dp) - sin(x)*sin(dp)
	 */
	void sincos (std::vector<float>& fbuf, double amp, double p, double dp, int n, int spa) {
		double cxr=0,cxi=0, dxr=0,dxi=0, axr,axi;
		if (spa>0) { // NTN 2009-12-16: only need to calculate below variables when spa>0
			cxr = amp*cos(p*TWOPI);
			cxi = amp*sin(p*TWOPI);
			dxr = cos(dp*TWOPI);
			dxi = sin(dp*TWOPI);
		}
		if (spa==2) for (int i=0; i<n*2;) {
			fbuf[i++]=(float) cxr;
			fbuf[i++]=(float) cxi;
			axr = (cxr*dxr - cxi*dxi);
			axi = (cxr*dxi + cxi*dxr);
			cxr=axr; cxi=axi;
		}
		else if (spa==1) for (int i=0; i<n;) {
			fbuf[i++]=(float) cxi;
			axr = (cxr*dxr - cxi*dxi);
			axi = (cxr*dxi + cxi*dxr);
			cxr=axr; cxi=axi;
		}
		else if (spa==-1) for (int i=0; i<n;) {
			fbuf[i++]=(float)( amp*sin(p*TWOPI) );
			p += dp;
		}
		else if (spa==-2) for (int i=0; i<n*2;) {
			fbuf[i++]=(float)( amp*cos(p*TWOPI) );
			fbuf[i++]=(float)( amp*sin(p*TWOPI) );
			p += dp;
		}
	}

	/** Create a SIN or COSINE DOUBLE array of given magnitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex; negative to use exact method
					  by calling sin() and cos()
	 */
	/*
	 *  fast algorithm based on:  sin(x+dp) = sin(x)*cos(dp) + cos(x)*sin(dp)
	 *                            cos(x+dp) = cos(x)*cos(dp) - sin(x)*sin(dp)
	 */
	void sincos (std::vector<double>& dbuf, double amp, double p, double dp, int n, int spa) {
		double cxr=0,cxi=0, dxr=0,dxi=0, axr,axi;
		if (spa>0) { // NTN 2009-12-16: only need to calculate below variables when spa>0
			cxr = amp*cos(p*TWOPI);
			cxi = amp*sin(p*TWOPI);
			dxr = cos(dp*TWOPI);
			dxi = sin(dp*TWOPI);
		}
		if (spa==2) for (int i=0; i<n*2;) {
			dbuf[i++]=cxr;
			dbuf[i++]=cxi;
			axr = (cxr*dxr - cxi*dxi);
			axi = (cxr*dxi + cxi*dxr);
			cxr=axr; cxi=axi;
		}
		else if (spa==1) for (int i=0; i<n;) {
			dbuf[i++]=cxi;
			axr = (cxr*dxr - cxi*dxi);
			axi = (cxr*dxi + cxi*dxr);
			cxr=axr; cxi=axi;
		}
		else if (spa==-1) for (int i=0; i<n;) {
			dbuf[i++]=amp*sin(p*TWOPI);
			p += dp;
		}
		else if (spa==-2) for (int i=0; i<n*2;) {
			dbuf[i++]=amp*cos(p*TWOPI);
			dbuf[i++]=amp*sin(p*TWOPI);
			p += dp;
		}
	}

	/** Create a SQUARE FLOAT array of given amplitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void square (std::vector<float>& fbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		double amp2 = -amp;
		for (int i=0; i<n*spa; ) {
			value = amp2;
			if (p>=1.0) p -= 1.0;
			else if (p>=0.5) value = amp;
			fbuf[i++] =(float) value; if (spa==2) fbuf[i++] =(float) value;
			p += dp;
		}
	}

	/** Create a SQUARE DOUBLE array of given amplitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void square (std::vector<double>& dbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		double amp2 = -amp;
		for (int i=0; i<n*spa; ) {
			value = amp2;
			if (p>=1.0) p -= 1.0;
			else if (p>=0.5) value = amp;
			dbuf[i++] = value; if (spa==2) dbuf[i++] = value;
			p += dp;
		}
	}

	/** Create a TRIANGLE FLOAT array of given amplitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void triangle (std::vector<float>& fbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		double amp2 = 4*amp;
		double fp = (p-0.5); // This needs to be in double precision for phase accuracy
		for (int i=0; i<n*spa; ) {
			if (fp>=0.5) fp -= 1.0;
			if (fp>0) value = amp - fp*amp2;
			else      value = amp + fp*amp2;
			fbuf[i++] =(float) value; if (spa==2) fbuf[i++] =(float) value;
			fp += dp;
		}
	}

	/** Create a TRIANGLE DOUBLE array of given amplitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void triangle (std::vector<double>& dbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		double amp2 = 4*amp;
		double fp = (p-0.5);
		for (int i=0; i<n*spa; ) {
			if (fp>=0.5) fp -= 1.0;
			if (fp>0) value = amp - fp*amp2;
			else      value = amp + fp*amp2;
			dbuf[i++] = value; if (spa==2) dbuf[i++] = value;
			fp += dp;
		}
	}

	/** Create a SAWTOOTH FLOAT array of given amplitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void sawtooth (std::vector<float>& fbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		double amp2 = 2*amp;
		double fp = (p-0.5); // This needs to be in double precision for phase accuracy
		for (int i=0; i<n*spa; ) {
			if (fp>=0.5) fp -= 1.0;
			value = fp*amp2;
			fbuf[i++] =(float) value; if (spa==2) fbuf[i++] =(float) value;
			fp += dp;
		}
	}

	/** Create a SAWTOOTH DOUBLE array of given amplitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void sawtooth (std::vector<double>& dbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		double amp2 = 2*amp;
		double fp = (p-0.5);
		for (int i=0; i<n*spa; ) {
			if (fp>=0.5) fp -= 1.0;
			value = fp*amp2;
			dbuf[i++] = value; if (spa==2) dbuf[i++] = value;
			fp += dp;
		}
	}

	/** Create a PULSE FLOAT array of given amplitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void pulse (std::vector<float>& fbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		for (int i=0; i<n*spa; ) {
			if (p>=1.0) { value = amp; p -= 1.0; } else value=0;
			fbuf[i++] =(float) value; if (spa==2) fbuf[i++] =(float) value;
			p += dp;
		}
	}

	/** Create a PULSE DOUBLE array of given amplitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param p    Phase
		  @param dp   Delta Phase
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void pulse (std::vector<double>& dbuf, double amp, double p, double dp, int n, int spa) {
		double value;
		for (int i=0; i<n*spa; ) {
			if (p>=1.0) { value = amp; p -= 1.0; } else value=0;
			dbuf[i++] = value; if (spa==2) dbuf[i++] = value;
			p += dp;
		}
	}

	/** Create a CONSTANT FLOAT array of given amplitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void constant (std::vector<float>& fbuf, double amp, int n, int spa) {
		for (int i=0; i<n*spa; ) fbuf[i++]=(float) amp;
	}

	/** Create a CONSTANT DOUBLE array of given amplitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
	 */
	void constant (std::vector<double>& dbuf, double amp, int n, int spa) {
		for (int i=0; i<n*spa; ) dbuf[i++]=amp;
	}

	/** Create an LRS noise FLOAT array of given magnitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
		  @param lrs  LRS seed from previous call
		  @return the LRS at end of array
	 */
	int lrs (std::vector<float>& fbuf, double amp, int n, int spa, int lrs) {
		double data;
		double factor = (amp/2/B1G);
		for (int i=0; i<n*spa; i++) {
			data = factor * lrs;
			int bit0 = (~(lrs ^ (lrs>>1) ^  (lrs>>5) ^ (lrs>>25)))&0x1;
			lrs <<= 1;
			lrs |= bit0;
			if (spa==2) fbuf[i++] = (float) data;
			fbuf[i] = (float) data;
		}
		return lrs;
	}

	/** Create an LRS noise DOUBLE array of given magnitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
		  @param lrs  LRS seed from previous call
		  @return the LRS at end of array
	 */
	int lrs (std::vector<double>& dbuf, double amp, int n, int spa, int lrs) {
		double data;
		double factor = (amp/2/B1G);
		for (int i=0; i<n*spa; i++) {
			data = factor * lrs;
			int bit0 = (~(lrs ^ (lrs>>1) ^  (lrs>>5) ^ (lrs>>25)))&0x1;
			lrs <<= 1;
			lrs |= bit0;
			if (spa==2) dbuf[i++] = data;
			dbuf[i] = data;
		}
		return lrs;
	}

	/** Create an RAMP FLOAT array of given magnitude
		  @param fbuf The output array
		  @param amp  Amplitude
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
		  @param data RAMP seed from previous call
		  @return the RAMP value at end of array
	 */
	int ramp (std::vector<float>& fbuf, double amp, int n, int spa, int data) {
		for (int i=0; i<n*spa; i++) {
			if (spa==2) fbuf[i++] =(float) data;
			fbuf[i] =(float) data;
			if (++data >= amp) data = (int)(-amp);
		}
		return data;
	}

	/** Create an RAMP DOUBLE array of given magnitude
		  @param dbuf The output array
		  @param amp  Amplitude
		  @param n    Number of elements
		  @param spa  Scalars per atom, 2 for Complex
		  @param data RAMP seed from previous call
		  @return the RAMP value at end of array
	 */
	int ramp (std::vector<double>& dbuf, double amp, int n, int spa, int data) {
		for (int i=0; i<n*spa; i++) {
			if (spa==2) dbuf[i++] =(double) data;
			dbuf[i] =(double) data;
			if (++data >= amp) data = (int)(-amp);
		}
		return data;
	}
}
