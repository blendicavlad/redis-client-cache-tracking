#include "redismodule.h"
#include "logger.h"

#include "cct_query_tracking_logic.h"
#include "cct_command_register.h"
#include "cct_command_search.h"
#include "cct_command_heartbeat.h"

#ifndef CCT_MODULE_VERSION
#define CCT_MODULE_VERSION "unknown"
#endif

#ifdef __cplusplus
extern "C" {
#endif

int RedisModule_OnLoad(RedisModuleCtx *ctx, RedisModuleString **argv, int argc) {
    
    if (RedisModule_Init(ctx,"CCT",1,REDISMODULE_APIVER_1) == REDISMODULE_ERR) {
        return REDISMODULE_ERR;
    }
    
    const char* version = CCT_MODULE_VERSION;
    LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "CCT_MODULE_VERSION : " + std::string(version));
    
    if (RedisModule_CreateCommand(ctx,"CCT.REGISTER", Register_RedisCommand , "admin write", 0, 0, 0) == REDISMODULE_ERR) {
        return REDISMODULE_ERR;
    } else {
        LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "CCT.REGISTER command created successfully.");
    }

    if (RedisModule_CreateCommand(ctx,"CCT.FT.SEARCH", FT_Search_RedisCommand , "readonly", 0, 0, 0) == REDISMODULE_ERR) {
        return REDISMODULE_ERR;
    } else {
        LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "CCT.FT.SEARCH command created successfully.");
    }

    if (RedisModule_CreateCommand(ctx,"CCT.HEARTBEAT", Heartbeat_RedisCommand , "readonly", 0, 0, 0) == REDISMODULE_ERR) {
        return REDISMODULE_ERR;
    } else {
        LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "CCT.HEARTBEAT command created successfully.");
    }    

    // Subscribe to key space events
    if ( RedisModule_SubscribeToKeyspaceEvents(ctx, REDISMODULE_NOTIFY_GENERIC | REDISMODULE_NOTIFY_SET | REDISMODULE_NOTIFY_STRING |
            REDISMODULE_NOTIFY_EVICTED | REDISMODULE_NOTIFY_EXPIRED | REDISMODULE_NOTIFY_LOADED | REDISMODULE_NOTIFY_NEW | REDISMODULE_NOTIFY_MODULE ,
             Notify_Callback) != REDISMODULE_OK ) {
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "RedisModule_OnLoad failed to SubscribeToKeyspaceEvents." );
        return RedisModule_ReplyWithError(ctx, strerror(errno));
    }

    if (RedisModule_SubscribeToServerEvent(ctx, RedisModuleEvent_ClientChange,
                                             Handle_Client_Event) != REDISMODULE_OK) {
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "RedisModule_OnLoad failed to SubscribeToServerEvent." );
        return RedisModule_ReplyWithError(ctx, strerror(errno));
    }

    Start_Client_Handler(ctx);
  
    return REDISMODULE_OK;
}


#ifdef __cplusplus
}
#endif

