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

SigGen_jar_CLASSPATH = $(CLASSPATH_SOFTPKG_DEP)$(OSSIE_HOME)/lib/CFInterfaces.jar:$(OSSIE_HOME)/lib/log4j-1.2.15.jar:$(OSSIE_HOME)/lib/ossie.jar:$(OSSIE_HOME)/lib/bulkio.jar:$(OSSIE_HOME)/lib/BULKIOInterfaces.jar

SigGen.jar: $(SigGen_jar_SOURCES)
	mkdir -p bin
	$(JAVAC) -cp $(SigGen_jar_CLASSPATH) -d bin $(SigGen_jar_SOURCES)
	$(JAR) cf ./SigGen.jar -C bin .

clean-local:
	rm -rf bin

distclean-local:
	rm -f config.*
	rm -rf autom4te.cache
	rm -f acinclude.m4
	rm -f aclocal.m4
	rm -f configure
	rm -f depcomp
	rm -f install-sh
	rm -f ltmain.sh
	rm -f Makefile.in
	rm -f missing
	rm -rf .deps

ossieName = SigGen
bindir = $(prefix)/dom/components/SigGen/java/
bin_PROGRAMS = SigGen.jar
SigGen_jar_SOURCES := $(shell find ./src -name "*.java")

xmldir = $(prefix)/dom/components/SigGen/
dist_xml_DATA = ../SigGen.scd.xml ../SigGen.prf.xml ../SigGen.spd.xml

domdir = $(prefix)/dom/components/SigGen/java/
dist_dom_SCRIPTS = startJava.sh
