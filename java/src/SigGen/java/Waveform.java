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

/**
  Class to create va
  rious waveforms.  Based fof code imported from NextMIDAS.

*/
public class Waveform {

  private static final double A=67081293.0, B=14181771.0, T26=67108864.0;
  private static final double BI = B/T26;
  private static long seed = 123456789;
  
  // Pre-calculate some useful constants
  private static double TWOPI = Math.PI * 2;
  
  /** Binary variant of a Giga. Note that this differs from the typical version
  (the decimal) version of Giga which is 10<sup>9</sup>.<br>
  <br>
  Value: <code>{@value} = 1G = 2<sup>30</sup></code><br>
  */
  final static int B1G  = 1073741824;

  /** Set the seed used in white noise waveform generation */
  public static void setSeed (int value) {
    if (value>0) seed = value;
  }

  /** Create a white noise FLOAT array of Mode one scalar per atom
      @param sdev Standard deviation
      @param n    Number of elements
  */
  public static float[] whitenoise (double sdev, int n) {
    float[] fbuf = new float[n];
    whitenoise (fbuf,sdev,n,1);
    return fbuf;
  }

  /** Create a white noise FLOAT array of given magnitude
      @param fbuf The output array
      @param sdev Standard deviation
      @param n    Number of elements
      @param spa  Scalars per atom, 2 for Complex
  */
  public static void whitenoise (float[] fbuf, double sdev, int n, int spa) {
    float v1,v2,sum, fdev = (float)sdev, factor = (float)(-2.0 / Math.log(10.0));
    double sis=((double)seed)/T26;
    for (int i=0; i<n*spa;) {
      sis = sis*A + BI;
      sis = sis - (double)(int)sis;
      v1 = (float)sis; v1 = v1+v1-1;
      sis = sis*A + BI;
      sis = sis - (double)(int)sis;
      v2 = (float)sis; v2 = v2+v2-1;
      sum = v1*v1 + v2*v2;
      if (sum>=1.0) continue;
      sum = fdev * (float)Math.sqrt(factor*Math.log(sum)/sum);
//      sum = fdev * Native.sqrtf(factor*Native.logf(sum)/sum);
      fbuf[i++] = v1*sum;
      if(i<n*spa){
    	  fbuf[i++] = v2*sum;
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
  public static void whitenoise (double[] dbuf, double sdev, int n, int spa) {
    double v1,v2,sum, sis=((double)seed)/T26;
    double factor = -2.0 / Math.log(10.0);
    for (int i=0; i<n*spa;) {
      sis = sis*A + BI;
      sis = sis - (double)(int)sis;
      v1 = sis+sis-1;
      sis = sis*A + BI;
      sis = sis - (double)(int)sis;
      v2 = sis+sis-1;
      sum = v1*v1 + v2*v2;
      if (sum>=1.0) continue;
      sum = sdev * Math.sqrt(factor*Math.log(sum)/sum);
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
  public static void sincos (float[] fbuf, double amp, double p, double dp, int n, int spa) {
    float cxr=0,cxi=0, dxr=0,dxi=0, axr,axi;
    if (spa>0) { // NTN 2009-12-16: only need to calculate below variables when spa>0
      cxr = (float) ( amp*Math.cos(p*TWOPI) );
      cxi = (float) ( amp*Math.sin(p*TWOPI) );
      dxr = (float) ( Math.cos(dp*TWOPI) );
      dxi =(float) (  Math.sin(dp*TWOPI) );
    }
    if (spa==2) for (int i=0; i<n*2;) {
      fbuf[i++]=cxr;
      fbuf[i++]=cxi;
      axr = (cxr*dxr - cxi*dxi);
      axi = (cxr*dxi + cxi*dxr);
      cxr=axr; cxi=axi;
    }
    else if (spa==1) for (int i=0; i<n;) {
      fbuf[i++]=cxi;
      axr = (cxr*dxr - cxi*dxi);
      axi = (cxr*dxi + cxi*dxr);
      cxr=axr; cxi=axi;
    }
    else if (spa==-1) for (int i=0; i<n;) {
      fbuf[i++]=(float)( amp*Math.sin(p*TWOPI) );
      p += dp;
    }
    else if (spa==-2) for (int i=0; i<n*2;) {
      fbuf[i++]=(float)( amp*Math.cos(p*TWOPI) );
      fbuf[i++]=(float)( amp*Math.sin(p*TWOPI) );
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
                  by calling Math.sin() and Math.cos()
  */
  /*
   *  fast algorithm based on:  sin(x+dp) = sin(x)*cos(dp) + cos(x)*sin(dp)
   *                            cos(x+dp) = cos(x)*cos(dp) - sin(x)*sin(dp)
   */
  public static void sincos (double[] dbuf, double amp, double p, double dp, int n, int spa) {
    double cxr=0,cxi=0, dxr=0,dxi=0, axr,axi;
    if (spa>0) { // NTN 2009-12-16: only need to calculate below variables when spa>0
      cxr = amp*Math.cos(p*TWOPI);
      cxi = amp*Math.sin(p*TWOPI);
      dxr = Math.cos(dp*TWOPI);
      dxi = Math.sin(dp*TWOPI);
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
      dbuf[i++]=amp*Math.sin(p*TWOPI);
      p += dp;
    }
    else if (spa==-2) for (int i=0; i<n*2;) {
      dbuf[i++]=amp*Math.cos(p*TWOPI);
      dbuf[i++]=amp*Math.sin(p*TWOPI);
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
  public static void square (float[] fbuf, double amp, double p, double dp, int n, int spa) {
    float value, famp = (float)amp, famp2 = -famp;
    for (int i=0; i<n*spa; ) {
      value = famp2;
      if (p>=1.0) p -= 1.0;
      else if (p>=0.5) value = famp;
      fbuf[i++] = value; if (spa==2) fbuf[i++] = value;
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
  public static void square (double[] dbuf, double amp, double p, double dp, int n, int spa) {
    double value, amp2 = -amp;
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
  public static void triangle (float[] fbuf, double amp, double p, double dp, int n, int spa) {
    float value, famp = (float)amp, famp2 = 4*famp;
    double fp = (p-0.5); // This needs to be in double precision for phase accuracy
    for (int i=0; i<n*spa; ) {
      if (fp>=0.5) fp -= 1.0;
      if (fp>0) value = (float)(famp - fp*famp2);
      else      value = (float)(famp + fp*famp2);
      fbuf[i++] = value; if (spa==2) fbuf[i++] = value;
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
  public static void triangle (double[] dbuf, double amp, double p, double dp, int n, int spa) {
    double value, amp2 = 4*amp;
    double fp = (p-0.5), fdp = dp;
    for (int i=0; i<n*spa; ) {
      if (fp>=0.5) fp -= 1.0;
      if (fp>0) value = amp - fp*amp2;
      else      value = amp + fp*amp2;
      dbuf[i++] = value; if (spa==2) dbuf[i++] = value;
      fp += fdp;
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
   public static void sawtooth (float[] fbuf, double amp, double p, double dp, int n, int spa) {
    float value, famp2 = 2*(float)amp;
    double fp = (p-0.5); // This needs to be in double precision for phase accuracy
    for (int i=0; i<n*spa; ) {
      if (fp>=0.5) fp -= 1.0;
      value = (float)fp*famp2;
      fbuf[i++] = value; if (spa==2) fbuf[i++] = value;
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
   public static void sawtooth (double[] dbuf, double amp, double p, double dp, int n, int spa) {
    double value, amp2 = 2*amp;
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
  public static void pulse (float[] fbuf, double amp, double p, double dp, int n, int spa) {
    float value, famp = (float)amp;
    for (int i=0; i<n*spa; ) {
      if (p>=1.0) { value = famp; p -= 1.0; } else value=0;
      fbuf[i++] = value; if (spa==2) fbuf[i++] = value;
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
  public static void pulse (double[] dbuf, double amp, double p, double dp, int n, int spa) {
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
  public static void constant (float[] fbuf, double amp, int n, int spa) {
    float famp = (float)amp;
    for (int i=0; i<n*spa; ) fbuf[i++]=famp;
  }

  /** Create a CONSTANT DOUBLE array of given amplitude
      @param dbuf The output array
      @param amp  Amplitude
      @param n    Number of elements
      @param spa  Scalars per atom, 2 for Complex
  */
  public static void constant (double[] dbuf, double amp, int n, int spa) {
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
  public static int lrs (float[] fbuf, double amp, int n, int spa, int lrs) {
    float data, factor = (float)(amp/2/B1G);
    for (int i=0; i<n*spa; i++) {
      data = factor * lrs;
      int bit0 = (~(lrs ^ (lrs>>1) ^  (lrs>>5) ^ (lrs>>25)))&0x1;
      lrs <<= 1;
      lrs |= bit0;
      if (spa==2) fbuf[i++] = data;
      fbuf[i] = data;
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
  public static int lrs (double[] dbuf, double amp, int n, int spa, int lrs) {
    double data, factor = (amp/2/B1G);
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
  public static int ramp (float[] fbuf, double amp, int n, int spa, int data) {
    for (int i=0; i<n*spa; i++) {
      if (spa==2) fbuf[i++] = data;
      fbuf[i] = data;
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
  public static int ramp (double[] dbuf, double amp, int n, int spa, int data) {
    for (int i=0; i<n*spa; i++) {
      if (spa==2) dbuf[i++] = data;
      dbuf[i] = data;
      if (++data >= amp) data = (int)(-amp);
    }
    return data;
  }

}
