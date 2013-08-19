#
# This file is protected by Copyright. Please refer to the COPYRIGHT file distributed with this 
# source distribution.
# 
# This file is part of REDHAWK Basic Components SigGen.
# 
# REDHAWK Basic Components SigGen is free software: you can redistribute it and/or modify it under the terms of 
# the GNU Lesser General Public License as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later version.
# 
# REDHAWK Basic Components SigGen is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License along with this 
# program.  If not, see http://www.gnu.org/licenses/.
#
import math

TWOPI = math.pi * 2.0

class Waveforms(object):
    def generate_sine(self, amp, n, p=0, dp=0, spa=1):
        outbuff = range(n*spa)
        cxr=0.0; cxi=0.0; dxr=0.0; dxi=0.0; axr=0.0; axi=0.0;
        cxr = float(amp*math.cos(p*TWOPI))
        cxi = float(amp*math.sin(p*TWOPI))
        dxr = float(math.cos(dp*TWOPI))
        dxi = float(math.sin(dp*TWOPI))
        for i in range(n):
            outbuff[i] = cxi
            axr = (cxr*dxr - cxi*dxi)
            axi = (cxr*dxi + cxi*dxr)
            cxr=axr
            cxi=axi
        return outbuff
    
    def generate_lrs(self, magnitude, n, spa=1, lrs=1):
        outbuff = range(n*spa)
        data = 0.0
        factor = float(magnitude/2.**31)
        for i in range(0, n*spa, spa):
            data = factor * lrs
            bit0 = (~(lrs ^ (lrs>>1) ^  (lrs>>5) ^ (lrs>>25)))&0x1
            lrs <<= 1
            lrs |= bit0
            # Correct for python not overflowing int_32s
            lrs &= 0xffffffff
            if lrs >= 2**31 -1:
                lrs &= 0x7fffffff
                lrs -= 2**31

            outbuff[i] = data
            if spa == 2:
                outbuff[i+1] = data
        return outbuff
    
    def generate_square(self, amp, n, p=0, dp=0, spa=1):
        outbuff = range(n*spa)
        value = 0.0
        famp = float(amp)
        famp2 = -famp
        
        for i in range(0, n*spa, spa):
            value = famp2
            if p >= 1.0:
                p -= 1.0
            elif p >= 0.5:
                value = famp
            outbuff[i] = value
            if spa == 2:
                outbuff[i+1] = value
            p += dp
            
        return outbuff
    
    def generate_triangle(self, amp, n, p=0, dp=0, spa=1):
        outbuff = range(n*spa)
        value = 0.0
        famp = float(amp)
        famp2 = 4*famp
        fp = float(p) - 0.5
        
        for i in range(0, n*spa, spa):
            if fp >= 0.5:
                fp -= 1.0
            if fp > 0:
                value = float(famp - fp*famp2)
            else:
                value = float(famp + fp*famp2)
            outbuff[i] = value
            if spa == 2:
                outbuff[i+1] = value
            fp += dp
        
        return outbuff
            
    def generate_sawtooth(self, amp, n, p=0, dp=0, spa=1):
        outbuff = range(n*spa)
        value = 0.0
        famp = float(amp)
        famp2 = 2*famp
        fp = float(p) - 0.5
        
        for i in range(0, n*spa, spa):
            if fp >= 0.5:
                fp -= 1.0
            value = float(fp*famp2)
            outbuff[i] = value
            if spa == 2:
                outbuff[i+1] = value
            fp += dp
            
        return outbuff