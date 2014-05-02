# trapperkeeper

## Description
TrapperKeeper is a suite of tools for ingesting and displaying SNMP traps. This 
is designed as a replacement for snmptrapd and to supplement existing stateful
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

The trapperkeeper command receives SNMP traps and handles e-mailing and writing
to the database. An example configuration file with documentation is available [here.](conf/trapperkeeper.yaml)

### trapdoor

trapdoor is a webserver that provides a view into the existing traps as well as an
API for viewing the state of traps. An example configuration file with documentation is available [here.](conf/trapdoor.yaml)

![Screenshot](https://raw.githubusercontent.com/dropbox/trapperkeeper/master/images/trapdoor.png)

#### API

##### /api/activetraps
_*Optional Parameters:*_
 * hostname
 * oid
 * severity

_*Returns:*_
```javascript
[
    (<hostname>, <oid>, <severity>)
]
```

##### /api/varbinds/<notification_id>

_*Returns:*_
```javascript
[
    {
        "notification_id": <notification_id>,
        "name": <varbind_name>,
        "pretty_value": <pretty_value>,
        "oid": <oid>,
        "value": <value>,
        "value_type": <value_type>
    }
]
```

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
