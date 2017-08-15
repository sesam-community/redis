# sesam-redis
Sample REDIS REST datasource and sink for Sesam

The service tekes the following parameters:

`host = Hostname or IP address for REDIS server (Default = localhost)`

`port = What port the REDIS server is using (Default = 6379)`

`db = Which database id (0-15) you want to use (Default = 0)`

## Supported datatypes

The datatypes hash and zset are currently supported, other datatypes are ignored.

