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
package SigGen.java.ports;


import java.util.HashMap;
import java.util.Map;
import org.ossie.component.QueryableUsesPort;
import java.util.ArrayList;
import java.util.List;
import CF.PropertiesHelper;
import CF.DataType;
import org.omg.CORBA.ORB;
import org.omg.CORBA.Any;
import SigGen.java.SigGen.*;
import java.util.Map.Entry;
import ExtendedCF.UsesConnection;
import BULKIO.*;

/**
 * @generated
 */
public class BULKIO_dataDoubleOutPort extends UsesPortStatisticsProviderPOA {

    /**
     * @generated
     */
    protected double[] dataOut;

    /**
     * @generated
     */
    protected boolean refreshSRI;
    
    /**
     * Map of connection Ids to port objects
     * @generated
     */
    protected Map<String, dataDoubleOperations> outConnections = new HashMap<String, dataDoubleOperations>();

    /**
     * Map of connection ID to statistics
     * @generated
     */
    protected Map<String, BULKIO_dataDoubleOutPort.linkStatistics> stats;

    /**
     * Map of stream IDs to streamSRI's
     * @generated
     */
    protected Map<String, StreamSRI> currentSRIs;

    /**
     * @generated
     */
	protected String name;

    /**
     * @generated
     */
	protected Object updatingPortsLock;

    /**
     * @generated
     */
	protected boolean active;

    /**
     * @generated
     */
    public BULKIO_dataDoubleOutPort(String portName) 
    {
        this.name = portName;
        this.updatingPortsLock = new Object();
        this.active = false;
        this.outConnections = new HashMap<String, dataDoubleOperations>();
        this.stats = new HashMap<String, BULKIO_dataDoubleOutPort.linkStatistics>();
        this.currentSRIs = new HashMap<String, StreamSRI>();

        //begin-user-code
        //end-user-code
    }

    /**
     * @generated
     */
    public PortUsageType state() {
        PortUsageType state = PortUsageType.IDLE;

        if (this.outConnections.size() > 0) {
            state = PortUsageType.ACTIVE;
        }

        //begin-user-code
        //end-user-code

        return state;
    }

    /**
     * @generated
     */
    public void enableStats(final boolean enable)
    {
        for (String connId : outConnections.keySet()) {
            stats.get(connId).enableStats(enable);
        }
    };

    /**
     * @generated
     */
    public UsesPortStatistics[] statistics() {
        UsesPortStatistics[] portStats = new UsesPortStatistics[this.outConnections.size()];
        int i = 0;
        
        synchronized (this.updatingPortsLock) {
            for (String connId : this.outConnections.keySet()) {
                portStats[i] = new UsesPortStatistics(connId, this.stats.get(connId).retrieve());
            }
        }
        
        return portStats;
    }

    /**
     * @generated
     */
    public StreamSRI[] activeSRIs() 
    {
        return this.currentSRIs.values().toArray(new StreamSRI[0]);
    }

    /**
     * @generated
     */
    public boolean isActive() {
        return this.active;
    }

    /**
     * @generated
     */
    public void setActive(final boolean active) {
        this.active = active;
    }

    /**
     * @generated
     */
    public String getName() {
        return this.name;
    }

    /**
     * @generated
     */
    public HashMap<String, dataDoubleOperations> getPorts() {
        return new HashMap<String, dataDoubleOperations>();
    }
 
    /**
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
     * @generated
     */
    public void pushSRI(StreamSRI header) 
    {
        // Header cannot be null
        if (header == null) return;
        // Header cannot have null keywords
        if (header.keywords == null) header.keywords = new DataType[0];

        synchronized(this.updatingPortsLock) {    // don't want to process while command information is coming in
            if (this.active) {
                //begin-user-code
                //end-user-code

                for (dataDoubleOperations p : this.outConnections.values()) {
                    try {
                        p.pushSRI(header);
                    } catch(Exception e) {
                        System.out.println("Call to pushSRI by BULKIO_dataDoubleOutPort failed");
                    }
                }
            }

            //begin-user-code
            //end-user-code
            
            this.currentSRIs.put(header.streamID, header);
            this.refreshSRI = false;

            //begin-user-code
            //end-user-code
        }    // don't want to process while command information is coming in

        return;
    }
        
    /**
     * @generated
     */
    public void pushPacket(double[] doubleData, PrecisionUTCTime time, boolean endOfStream, String streamID) 
    {
        if (this.refreshSRI) {
        	if (!this.currentSRIs.containsKey(streamID)) {
				StreamSRI sri = new StreamSRI();
				sri.mode = 0;
				sri.xdelta = 1.0;
				sri.ydelta = 0.0;
				sri.subsize = 0;
				sri.xunits = 1; // TIME_S
				sri.streamID = streamID;
                this.currentSRIs.put(streamID, sri);
            }
            this.pushSRI(this.currentSRIs.get(streamID));
        }
        
        synchronized(this.updatingPortsLock) {    // don't want to process while command information is coming in
            this.dataOut = doubleData;
            if (this.active) {
                //begin-user-code
                //end-user-code
                
                for (Entry<String, dataDoubleOperations> p : this.outConnections.entrySet()) {
                    try {
                        p.getValue().pushPacket(this.dataOut, time, endOfStream, streamID);
                        this.stats.get(p.getKey()).update(this.dataOut.length, 0, endOfStream, streamID);
                    } catch(Exception e) {
                        System.out.println("Call to pushPacket by BULKIO_dataDoubleOutPort failed");
                    }
                }

                //begin-user-code
                //end-user-code
            }
        }    // don't want to process while command information is coming in
        
        return;
    }

    /**
     * @generated
     */
    public void connectPort(final org.omg.CORBA.Object connection, final String connectionId) throws CF.PortPackage.InvalidPort, CF.PortPackage.OccupiedPort
    {
        synchronized (this.updatingPortsLock) {
            final dataDoubleOperations port;
            try {
            	port = BULKIO.jni.dataDoubleHelper.narrow(connection);
            } catch (final Exception ex) {
            	throw new CF.PortPackage.InvalidPort((short)1, "Invalid port for connection '" + connectionId + "'");
            }
            this.outConnections.put(connectionId, port);
            this.active = true;
            this.stats.put(connectionId, new linkStatistics());
            this.refreshSRI = true;
        
            //begin-user-code
            //end-user-code
        }
    }

    /**
     * @generated
     */
    public void disconnectPort(String connectionId) {
        synchronized (this.updatingPortsLock) {
            dataDoubleOperations port = this.outConnections.remove(connectionId);
            this.stats.remove(connectionId);
            this.active = (this.outConnections.size() != 0);

            //begin-user-code
            //end-user-code
        }
    }

    /**
     * @generated
     */
    public UsesConnection[] connections() {
        final UsesConnection[] connList = new UsesConnection[this.outConnections.size()];
        int i = 0;
        synchronized (this.updatingPortsLock) {
            for (Entry<String, dataDoubleOperations> ent : this.outConnections.entrySet()) {
                connList[i++] = new UsesConnection(ent.getKey(), (org.omg.CORBA.Object) ent.getValue());
            }
        }
        return connList;
    }

    /**
     * @generated
     */
    public class statPoint implements Cloneable {
        /** @generated */
        int elements;
        /** @generated */
        float queueSize;
        /** @generated */
        double secs;
    }
    
    /**
     * @generated
     */
    public class linkStatistics {
        /** @generated */
        protected double bitSize;
        /** @generated */
        protected PortStatistics runningStats;
        /** @generated */
        protected statPoint[] receivedStatistics;
        /** @generated */
        protected List<String> activeStreamIDs;
        /** @generated */
        protected final int historyWindow;
        /** @generated */
        protected int receivedStatistics_idx;
        /** @generated */
        protected boolean enabled;

        /**
         * @generated
         */
        public linkStatistics() {
            this.enabled = true;
            this.bitSize = 8.0 * 8.0;
            this.historyWindow = 10;
            this.receivedStatistics_idx = 0;
            this.receivedStatistics = new BULKIO_dataDoubleOutPort.statPoint[historyWindow];
            this.activeStreamIDs = new ArrayList<String>();
            this.runningStats = new PortStatistics();
            this.runningStats.portName = BULKIO_dataDoubleOutPort.this.name;
            this.runningStats.elementsPerSecond = -1.0f;
            this.runningStats.bitsPerSecond = -1.0f;
            this.runningStats.callsPerSecond = -1.0f;
            this.runningStats.averageQueueDepth = -1.0f;
            this.runningStats.streamIDs = new String[0];
            this.runningStats.timeSinceLastCall = -1.0f;
            this.runningStats.keywords = new DataType[0];
            for (int i = 0; i < historyWindow; ++i) {
                this.receivedStatistics[i] = new BULKIO_dataDoubleOutPort.statPoint();
            }
        }

        /**
         * @generated
         */
        public void setBitSize(double bitSize) {
            this.bitSize = bitSize;
        }

        /**
         * @generated
         */
        public void enableStats(boolean enable) {
            this.enabled = enable;
        }

        /**
         * @generated
         */
        public void update(int elementsReceived, float queueSize, boolean EOS, String streamID) {
            if (!this.enabled) {
                return;
            }
            long nanos = System.nanoTime();
            this.receivedStatistics[this.receivedStatistics_idx].elements = elementsReceived;
            this.receivedStatistics[this.receivedStatistics_idx].queueSize = queueSize;
            this.receivedStatistics[this.receivedStatistics_idx++].secs = nanos * 1.0e-9;
            this.receivedStatistics_idx = this.receivedStatistics_idx % this.historyWindow;
            if (!EOS) {
                if (!this.activeStreamIDs.contains(streamID)) {
                    this.activeStreamIDs.add(streamID);
                }
            } else {
                this.activeStreamIDs.remove(streamID);
            }
        }

        /**
         * @generated
         */
        public PortStatistics retrieve() {
            if (!this.enabled) {
                return null;
            }
            long nanos = System.nanoTime();
            double secs = nanos * 1.0e-9;
            int idx = (this.receivedStatistics_idx == 0) ? (this.historyWindow - 1) : (this.receivedStatistics_idx - 1) % this.historyWindow;
            double front_sec = this.receivedStatistics[idx].secs;
            double totalTime = secs - this.receivedStatistics[this.receivedStatistics_idx].secs;
            double totalData = 0;
            float queueSize = 0;
            int startIdx = (this.receivedStatistics_idx + 1) % this.historyWindow;
            for (int i = startIdx; i != receivedStatistics_idx; ) {
                totalData += this.receivedStatistics[i].elements;
                queueSize += this.receivedStatistics[i].queueSize;
                i = (i + 1) % this.historyWindow;
            }
            int receivedSize = receivedStatistics.length;
            synchronized (this.runningStats) {
                this.runningStats.timeSinceLastCall = (float)(secs - front_sec);
                this.runningStats.bitsPerSecond = (float)((totalData * this.bitSize) / totalTime);
                this.runningStats.elementsPerSecond = (float)(totalData / totalTime);
                this.runningStats.averageQueueDepth = (float)(queueSize / receivedSize);
                this.runningStats.callsPerSecond = (float)((receivedSize - 1) / totalTime);
                this.runningStats.streamIDs = this.activeStreamIDs.toArray(new String[0]);
            }
            return runningStats;
        }
    }
}