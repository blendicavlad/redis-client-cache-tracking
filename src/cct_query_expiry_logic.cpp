#include "cct_query_expiry_logic.h"

int Handle_Query_Expire(RedisModuleCtx *ctx , std::string key) {
    RedisModule_AutoMemory(ctx);
    
    if (key.rfind(CCT_MODULE_KEY_SEPERATOR) == std::string::npos) {
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire key : " + key  + " is invalid.");
        return REDISMODULE_ERR;
    }
    std::string client_name(key.substr(key.rfind(CCT_MODULE_KEY_SEPERATOR) + 1));
    std::string query(key.substr(0, key.rfind(CCT_MODULE_KEY_SEPERATOR)));
    LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "Handle_Query_Expire parsed  client_name :" + client_name  + " , query :" + query);
    std::string plain_query(query.substr(CCT_MODULE_QUERY_CLIENT.length()));
    
    bool expired_query_has_other_clients = true;

    // Delete the Query:{Clients}
    std::string new_query_with_prefix = CCT_MODULE_QUERY_2_CLIENT  + plain_query;
    LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "Handle_Query_Expire (Query:{Clients}) parsed  client_name :" + client_name  + " , q2c_query :" + new_query_with_prefix);
    RedisModuleCallReply *q2c_srem_key_reply = RedisModule_Call(ctx, "SREM", "cc", new_query_with_prefix.c_str()  , client_name.c_str());
    if (RedisModule_CallReplyType(q2c_srem_key_reply) != REDISMODULE_REPLY_INTEGER){
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Query:{Clients}) failed while deleting client: " +  client_name);
        return REDISMODULE_ERR;
    } else if ( RedisModule_CallReplyInteger(q2c_srem_key_reply) == 0 ) { 
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Query:{Clients}) failed while deleting client (non existing key): " +  client_name);
        return REDISMODULE_ERR;
    }

    // Check if the query has any other tracking client
    RedisModuleString *q2c_key = RedisModule_CreateString(ctx, new_query_with_prefix.c_str() , new_query_with_prefix.length());
    if( !RedisModule_KeyExists(ctx, q2c_key) ){
        expired_query_has_other_clients = false;
        LOG(ctx, REDISMODULE_LOGLEVEL_DEBUG , "Handle_Query_Expire parsed (Query:{Clients}) " + new_query_with_prefix + " has no other client tracking.");
    }

    // If query doesn't belong to any client 
    if (expired_query_has_other_clients == false) {

        // First find all keys matching to query
        std::vector<std::string> keys_matching_expired_query; 
        std::string q2k_str = CCT_MODULE_QUERY_2_KEY + plain_query;
        RedisModuleCallReply *q2k_smembers_reply = RedisModule_Call(ctx, "SMEMBERS", "c", q2k_str.c_str());
        const size_t reply_length = RedisModule_CallReplyLength(q2k_smembers_reply);
        for (size_t i = 0; i < reply_length; i++) {
            RedisModuleCallReply *q2k_key_reply = RedisModule_CallReplyArrayElement(q2k_smembers_reply, i);
            if (RedisModule_CallReplyType(q2k_key_reply) == REDISMODULE_REPLY_STRING){
                RedisModuleString *key_name = RedisModule_CreateStringFromCallReply(q2k_key_reply);
                const char *key_name_str = RedisModule_StringPtrLen(key_name, NULL);
                keys_matching_expired_query.push_back(std::string(key_name_str));
            }
        }

        // Now delete the queries to matching these keys from "Key:{Queries}"
        for (auto &key_name : keys_matching_expired_query) {
            std::string k2q_key = CCT_MODULE_KEY_2_QUERY + key_name;
            RedisModuleCallReply *k2q_srem_key_reply = RedisModule_Call(ctx, "SREM", "cc", k2q_key.c_str()  , plain_query.c_str());
            if (RedisModule_CallReplyType(k2q_srem_key_reply) != REDISMODULE_REPLY_INTEGER){
                LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Key:{Queries}) failed while deleting query: " +  plain_query);
                return REDISMODULE_ERR;
            } else if ( RedisModule_CallReplyInteger(k2q_srem_key_reply) == 0 ) { 
                LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Key:{Queries}) failed while deleting query (non existing key): " +  plain_query);
                return REDISMODULE_ERR;
            }
        } 


        // Finally delete all "Query:{Keys}"" set
        std::string q2k_key_name_str = CCT_MODULE_QUERY_2_KEY + plain_query ;
        RedisModuleString *q2k_key_name = RedisModule_CreateString(ctx, q2k_key_name_str.c_str() , q2k_key_name_str.length());
        RedisModuleKey *q2k_key = RedisModule_OpenKey(ctx, q2k_key_name, REDISMODULE_WRITE);
        if (RedisModule_DeleteKey(q2k_key) !=  REDISMODULE_OK ) {
            LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Query:{Keys}) failed while deleting key: " +  q2k_key_name_str);
        }


    }

    // Delete the Client:{Queries}
    std::string client_with_prefix = CCT_MODULE_CLIENT_2_QUERY + client_name;
    RedisModuleCallReply *c2q_srem_key_reply = RedisModule_Call(ctx, "SREM", "cc", client_with_prefix.c_str()  , plain_query.c_str());
    if (RedisModule_CallReplyType(c2q_srem_key_reply) != REDISMODULE_REPLY_INTEGER){
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Client:{Queries}) failed while deleting query: " +  plain_query);
        return REDISMODULE_ERR;
    } else if ( RedisModule_CallReplyInteger(c2q_srem_key_reply) == 0 ) { 
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire (Client:{Queries}) failed while deleting query (non existing key): " +  plain_query);
        return REDISMODULE_ERR;
    }


    // Add event to stream
    if (Add_Event_To_Stream(ctx, client_name, "query_expired", "" , "", plain_query) != REDISMODULE_OK) {
        LOG(ctx, REDISMODULE_LOGLEVEL_WARNING , "Handle_Query_Expire failed to adding to the stream." );
        return REDISMODULE_ERR;
    }
    
    return REDISMODULE_OK;
}