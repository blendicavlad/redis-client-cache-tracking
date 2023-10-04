# redis-client-cache-tracking
Redis module for client cache tracking

## Development Environment 

* IDE : [Visual Studio Code with WSL](https://code.visualstudio.com/docs/cpp/config-wsl) 
* g++ 11.4
* WSL : 5.15.90.1-microsoft-standard-WSL2 (Ubuntu Ubuntu 22.04.2 LTS)
* Redis server v=Redis 7.2.1 (Latest Stable Package)
* Redis Modules :
    * [Redis Search] (https://github.com/RediSearch/RediSearch)
    * [Redis JSON] (https://github.com/RedisJSON/RedisJSON)

## Build

After preparing the build environment just run : 

```
make
```

Or if you want the Debug version which has lots of logs to standard output (don't run heavy stress tests) you can use: 

```
make DEBUG=1
```

## Load

To load the development module you can use these commands: 

```
redis-server --loadmodule ./bin/cct.so
```

or 

```
make load
```

## Test
Development is done by `Python 3.10.2` but any version after `3.6.X` should be fine. To install needed python packages just run (generated by `pipreqs`): 

```
pip install -r python/requirements.txt
```

For test purposes you can use the python client. To run the tests just run : 

```
make test
```

or only run performance tests: 

```
make perf_test
```

Normally to not effect the other test *client heartbeat tests* are disabled (skipped) by default. You can enable them by setting `SKIP_HB_TEST` to `True` .

## Logging

When build is done with `make DEBUG=1` logging is done to standard output. If no parameter is given it will be a release build and logging level is *hardcoded* to only `warning` level and it will be logging to log file given in config file. 

## Delimeters

Currently we are using 2 special delimeter :

1. Seperate the queries in the stream data . This one is defined in `CCT_MODULE_QUERY_DELIMETER`
2. Seperate stream entry that shows that snapshot has been finished. This one is defined in `CCT_MODULE_END_OF_SNAPSHOT`

## Constants

Server values such as TTL and other query tracking metadata string and values are defined in here : https://github.com/8365redis/redis-client-cache-tracking/blob/main/include/constants.h

 
## Commands

* CCT.REGISTER 
* CCT.FT.SEARCH
* CCT.HEARTBEAT
