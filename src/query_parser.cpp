#include "query_parser.h"
#include <string>
#include <unordered_map>

std::string Get_Str_Between(const std::string &s,
        const std::string &start_delim,
        const std::string &stop_delim) {
    unsigned first_delim_pos = s.find(start_delim);
    unsigned end_pos_of_first_delim = first_delim_pos + start_delim.length();
    unsigned last_delim_pos = s.find(stop_delim);
 
    return s.substr(end_pos_of_first_delim, last_delim_pos - end_pos_of_first_delim);
}

std::string Get_Query_Term(const std::string &s) {
    return Get_Str_Between(s, TERM_START, TERM_END);
}

std::string Get_Query_Attribute(const std::string &s) {
    return Get_Str_Between(s, TAG_ATTRIBUTE_START, TAG_ATTRIBUTE_END);
}

std::unordered_map<char, std::string> specialChars = {
    {',', "\\,"}, {'.', "\\."}, {'<', "\\<"}, {'>', "\\>"},
    {'{', "\\{"}, {'}', "\\}"}, {'[', "\\["}, {'"', "\\\""},
    {'\\', "\\\\"}, {':', "\\:"}, {';', "\\;"}, {']', "\\]"},
    {'!', "\\!"}, {'@', "\\@"}, {'#', "\\#"}, {'$', "\\$"},
    {'%', "\\%"}, {'^', "\\^"}, {'*', "\\*"}, {'(', "\\("},
    {'-', "\\-"}, {'+', "\\+"}, {'=', "\\="}, {'~', "\\~"},
    {'/', "\\/"}
};

std::string Escape_Special_Chars(const std::string &input) {
    std::string escapedString;
    escapedString.reserve(input.length() * 2);

    for (char c : input) {
        if (specialChars.find(c) != specialChars.end()) {
            escapedString.append(specialChars[c]);
        } else {
            escapedString.push_back(c);
        }
    }

    return escapedString;
}

std::string Escape_FtQuery(const std::string &input) {
    size_t colonPos = input.find(':');
    if (colonPos == std::string::npos) {
        // No colon found, return the input as is
        return input;
    }

    std::string beforeColon = input.substr(0, colonPos + 1);
    std::string afterColon = input.substr(colonPos + 1);

    std::string escapedAfterColon = Escape_Special_Chars(afterColon);

    return beforeColon + escapedAfterColon;
}