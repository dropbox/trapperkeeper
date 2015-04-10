#!/bin/bash

BASE_DIR=$( dirname $0 )

DEST="localhost"
IPv6_DEST="udp6:[::1]:162"
COMMON_OPTS="-Ln -mTRAPPERKEEPER-MIB -M+"${BASE_DIR}/mibs" -c public"
PRIV_COMMON_OPTS="-Ln -mTRAPPERKEEPER-MIB -M+"${BASE_DIR}/mibs" -c private"
SYSLOC_VARBIND="SNMPv2-MIB::sysLocation.0 s TrapperKeeper-Test"

snmptrap -v 1 $COMMON_OPTS $DEST TRAPPERKEEPER-MIB::testtraps "" 6 1 "" $SYSLOC_VARBIND
snmptrap -v 2c $COMMON_OPTS $DEST "" TRAPPERKEEPER-MIB::testV2Trap $SYSLOC_VARBIND
snmptrap -v 1 $PRIV_COMMON_OPTS $DEST TRAPPERKEEPER-MIB::testtraps "" 6 1 "" $SYSLOC_VARBIND

snmptrap -v 1 $COMMON_OPTS $IPv6_DEST TRAPPERKEEPER-MIB::testtraps "" 6 1 "" $SYSLOC_VARBIND
snmptrap -v 2c $COMMON_OPTS $IPv6_DEST "" TRAPPERKEEPER-MIB::testV2Trap $SYSLOC_VARBIND
snmptrap -v 1 $PRIV_COMMON_OPTS $IPv6_DEST TRAPPERKEEPER-MIB::testtraps "" 6 1 "" $SYSLOC_VARBIND
