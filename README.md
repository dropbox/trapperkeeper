# trapperkeeper

## Description
TrapperKeeper is a suite a tools for ingesting and displaying SNMP traps. This 
is designed as a replacement for snmptrapd and to supplements existing stateful
monitoring solutions.

## Installation

New versions will be updated to PyPI pretty regularly so it should be as easy
as:

```bash
$ pip install trapperkeeper
```

Once you've created a configuration file with your database information you
can run the following to create the database schema.

```bash
$ python -m trapperkeeper.cmds.sync_db -c /path/to/trapperkeeper.yaml
```
## Tools

### trapperkeeper

### trapdoor

## TODO

  * Runtime rules language for things like blackhole and e-mail subjects.
  * Allow Custom E-mail templates for TrapperKeeper
  * cdnjs prefix for local cdnjs mirrors
  * User ACLs for resolution
  * Logging resolving user

## Known Issues

  * Doesn't currently support SNMPv3
  * Doesn't currently support inform
  * Doesn't support listening on IPv6
  * Certain devices have been known to send negative TimeTicks. pyasn1 fails to handle this.
