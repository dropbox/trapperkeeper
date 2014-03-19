#!/bin/bash

BASE_DIR=$( dirname $0 )

DEST="localhost"
COMMON_OPTS="-Ln -mTRAPPERKEEPER-MIB -M+"${BASE_DIR}/mibs" -c public"
SYSLOC_VARBIND="SNMPv2-MIB::sysLocation.0 s TrapperKeeper-Test"

snmptrap -v 1 $COMMON_OPTS $DEST TRAPPERKEEPER-MIB::testtraps "" 6 1 "" $SYSLOC_VARBIND
snmptrap -v 2c $COMMON_OPTS $DEST "" TRAPPERKEEPER-MIB::testV2Trap $SYSLOC_VARBIND
