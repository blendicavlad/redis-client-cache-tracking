import pytest
import time
from redis.commands.json.path import Path
from manage_redis import kill_redis, connect_redis_with_start, connect_redis
import cct_prepare
from constants import CCT_QUERIES, CCT_VALUE, CCT_QUERY_HALF_TTL, CCT_QUERY_TTL, CCT_EOS
from cct_test_utils import check_query_meta_data
import json


@pytest.fixture(autouse=True)
def before_and_after_test():
    print("Start")
    yield
    kill_redis()
    print("End")


def test_1_client_1_query_with_disconnect():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    # Check stream is empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    time.sleep(0.2)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    #print(from_stream)
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 in str(from_stream[0][1][0][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_1_client_2_query_with_disconnect():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1000"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    #FIRST CLIENT SECOND QUERY
    query_value = 1000
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # Check stream is empty
    time.sleep(0.5)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(count=2, streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 in str(from_stream[0][1][0][1])
    assert first_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert second_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_1_client_1_query_without_disconnect():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    # Check stream is empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 in str(from_stream[0][1][0][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_1_client_2_query_without_disconnect():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1000"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    #FIRST CLIENT SECOND QUERY
    query_value = 1000
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # Check stream is empty
    from_stream = client1.xread(count=2, streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(count=2, streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 in str(from_stream[0][1][0][1])
    assert first_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert second_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_1_client_1_query_1_key_multiple_update_still_match_query():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2001, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2002, passport_value)
    producer.json().set(key_1, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 4 == len(from_stream[0][1])

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    time.sleep(0.1)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(json.dumps(from_stream))
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 in str(from_stream[0][1][0][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert 2 == len(from_stream[0][1])


def test_1_client_1_query_1_key_multiple_update_doesnt_match_query():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2001, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2002, "bbb")
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2002, "ccc")
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1003, 2003, "ddd")
    producer.json().set(key_1, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 4 == len(from_stream[0][1])

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(from_stream)
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 not in str(from_stream[0][1][0][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert 2 == len(from_stream[0][1])


def test_1_client_1_query_multiple_key_multiple_update_still_match_query():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1000, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    d = cct_prepare.generate_single_object(1005, 2000, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1006, 2000, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1000, 2005, passport_value)
    producer.json().set(key_2, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1000, 2006, passport_value)
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 5 == len(from_stream[0][1])

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    time.sleep(0.1)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_2 in str(from_stream[0][1][0][1])
    assert key_1 in str(from_stream[0][1][1][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert str(2006) in from_stream[0][1][0][1][CCT_VALUE]
    assert 3 == len(from_stream[0][1])


def test_1_client_1_query_multiple_key_multiple_update_doesnt_match_query():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1000, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1007, 2007, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2002, passport_value)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2003, passport_value)
    producer.json().set(key_1, Path.root_path(), d)

    d = cct_prepare.generate_single_object(1004, 2004, passport_value)
    producer.json().set(key_2, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1004, 2004, passport_value)
    producer.json().set(key_2, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1007, 2007, passport_value)
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 8 == len(from_stream[0][1])

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(json.dumps(from_stream))
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_2 in str(from_stream[0][1][0][1])
    assert key_1 in str(from_stream[0][1][1][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert query_normalized in from_stream[0][1][1][1][CCT_QUERIES]
    assert 3 == len(from_stream[0][1])


def test_1_client_multiple_query_multiple_key_multiple_update_mixed_match_query():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    id_value = 1001
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1001"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")
    query_value = id_value
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # UPDATE DATA
    d = cct_prepare.generate_single_object(1002, 2003, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1004, 2004, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2005, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2004, passport_value)  # match both
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 5 == len(from_stream[0][1])

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(json.dumps(from_stream))
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert 3 == len(from_stream[0][1])
    assert key_2 in str(from_stream[0][1][0][1])
    assert key_1 in str(from_stream[0][1][1][1])
    assert first_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert second_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert first_query_normalized in from_stream[0][1][1][1][CCT_QUERIES]


def test_1_client_multiple_query_multiple_key_multiple_update_mixed_match_query_without_disconnect():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    id_value = 1001
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1001"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")
    query_value = id_value
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # UPDATE DATA
    d = cct_prepare.generate_single_object(1002, 2003, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1004, 2004, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2005, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2004, passport_value)  # match both
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 5 == len(from_stream[0][1])

    # RE-REGISTER
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(json.dumps(from_stream))
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert 3 == len(from_stream[0][1])
    assert key_2 in str(from_stream[0][1][0][1])
    assert key_1 in str(from_stream[0][1][1][1])
    assert first_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert second_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]
    assert first_query_normalized in from_stream[0][1][1][1][CCT_QUERIES]


def test_1_client_multiple_query_multiple_key_multiple_update_mixed_match_query_1_query_expire_while_disconnect():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    id_value = 1001
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1001"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    time.sleep(CCT_QUERY_HALF_TTL)

    query_value = id_value
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # UPDATE DATA
    d = cct_prepare.generate_single_object(1002, 2003, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1004, 2004, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2005, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)

    d = cct_prepare.generate_single_object(1001, 2004, passport_value)  # match both
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 5 == len(from_stream[0][1])

    # DISCONNECT
    client1.connection_pool.disconnect()

    # THIS WILL EXPIRE FIRST QUERY 
    time.sleep(CCT_QUERY_HALF_TTL)

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(from_stream)
    assert 2 == len(from_stream[0][1])
    assert key_2 in str(from_stream[0][1][0][1])
    assert second_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_1_client_multiple_query_multiple_key_multiple_update_mixed_match_query_1_query_expire_while_connected():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    id_value = 1001
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1001"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    time.sleep(CCT_QUERY_HALF_TTL)

    query_value = id_value
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # UPDATE DATA
    d = cct_prepare.generate_single_object(1002, 2003, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1004, 2004, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2005, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)

    d = cct_prepare.generate_single_object(1001, 2004, passport_value)  # match both
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 5 == len(from_stream[0][1])
    print(from_stream)

    # THIS WILL EXPIRE FIRST QUERY 
    time.sleep(CCT_QUERY_HALF_TTL)

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    time.sleep(0.1)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 2 == len(from_stream[0][1])
    assert key_2 in str(from_stream[0][1][0][1])
    assert second_query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_1_client_multiple_query_multiple_key_multiple_update_mixed_match_query_all_query_expire():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    id_value = 1001
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1001, 2001, passport_value)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    producer.json().set(key_2, Path.root_path(), d)
    first_query_normalized = "User\\.PASSPORT:aaa"
    second_query_normalized = "User\\.ID:1001"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    time.sleep(CCT_QUERY_HALF_TTL)

    query_value = id_value
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.ID:{" + str(query_value) + "}")

    # UPDATE DATA
    d = cct_prepare.generate_single_object(1002, 2003, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1004, 2004, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)
    d = cct_prepare.generate_single_object(1002, 2005, passport_value)  # match one
    producer.json().set(key_1, Path.root_path(), d)

    d = cct_prepare.generate_single_object(1001, 2004, passport_value)  # match both
    producer.json().set(key_2, Path.root_path(), d)

    # Check stream is not empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(from_stream)
    assert 4 == len(from_stream[0][0])

    # THIS WILL EXPIRE FIRST QUERY 
    time.sleep(CCT_QUERY_HALF_TTL)

    # DISCONNECT
    client1.connection_pool.disconnect()

    # THIS WILL EXPIRE SECOND QUERY 
    time.sleep(CCT_QUERY_HALF_TTL)

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 1 == len(from_stream)


def test_1_client_1_query_key_expire():
    KEY_EXPIRE_SECOND = 1  # Expire before the query

    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    producer.expire(key_1, KEY_EXPIRE_SECOND, nx=True)
    passport_value = "bbb"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    # Check stream is empty
    time.sleep(0.2)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # THIS WILL EXPIRE KEY 
    time.sleep(KEY_EXPIRE_SECOND + 0.1)

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 1 == len(from_stream)


def test_1_client_1_query_first_key_later_query_expire():
    KEY_EXPIRE_SECOND = 1  # Expire before the query

    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    producer.expire(key_1, KEY_EXPIRE_SECOND, nx=True)
    passport_value = "bbb"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    # Check stream is empty
    time.sleep(0.1)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # THIS WILL EXPIRE KEY 
    time.sleep(KEY_EXPIRE_SECOND + 0.1)

    # THIS WILL QUERY 
    time.sleep(CCT_QUERY_TTL + 0.1)

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 1 == len(from_stream)


def test_1_client_1_query_first_query_later_key_expire():
    KEY_EXPIRE_SECOND = 1  # Expire before the query

    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    producer.expire(key_1, (CCT_QUERY_TTL + 1), nx=True)
    passport_value = "bbb"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")

    # Check stream is empty
    time.sleep(1)
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # THIS WILL EXPIRE KEY AND QUERY 
    time.sleep(CCT_QUERY_TTL + 1)

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert 1 == len(from_stream)


def test_empty_queries_in_snapshot():
    producer = connect_redis_with_start()
    cct_prepare.flush_db(producer)  # clean all db first
    cct_prepare.create_index(producer)

    # ADD INITIAL DATA
    passport_value = "aaa"
    d = cct_prepare.generate_single_object(1000, 2000, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    producer.json().set(key_1, Path.root_path(), d)
    query_normalized = "User\\.PASSPORT:aaa"

    # FIRST CLIENT
    query_value = passport_value
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)
    client1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")
    query_value = "non_existing_1"
    query_normalized_non_matching_1 = "User\\.PASSPORT:non_existing_1"
    client1.execute_command(
        "CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")  # This will not match
    query_value = "non_existing_2"
    query_normalized_non_matching_2 = "User\\.PASSPORT:non_existing_2"
    client1.execute_command(
        "CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + query_value + "}")  # This will not match

    # Check stream is empty
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    assert CCT_EOS in from_stream[0][1][0][1]

    # DISCONNECT
    client1.connection_pool.disconnect()

    # RE-REGISTER
    client1 = connect_redis()
    client1.execute_command("CCT.REGISTER " + cct_prepare.TEST_APP_NAME_1)

    time.sleep(0.2)

    # Check stream content
    from_stream = client1.xread(streams={cct_prepare.TEST_APP_NAME_1: 0})
    print(from_stream)
    assert cct_prepare.TEST_APP_NAME_1 in from_stream[0][0]
    assert key_1 in str(from_stream[0][1][0][1])
    assert query_normalized in from_stream[0][1][0][1][CCT_QUERIES]


def test_overwritten_value_not_matching_query_should_be_removed_form_tracked_multiple_clients():
    r1 = connect_redis()
    cct_prepare.flush_db(r1)  # clean all db first
    cct_prepare.create_index(r1)
    client_1 = "client1"
    client_2 = "client2"

    passport_value = "aaa"
    addr_id = "2000"
    d1 = cct_prepare.generate_single_object(1, addr_id, passport_value)
    d2 = cct_prepare.generate_single_object(2, addr_id, passport_value)
    first_key = cct_prepare.TEST_INDEX_PREFIX + str(1)
    second_key = cct_prepare.TEST_INDEX_PREFIX + str(2)
    r1.json().set(first_key, Path.root_path(), d1)
    r1.json().set(second_key, Path.root_path(), d2)

    # FIRST CLIENT
    r1.execute_command("CCT.REGISTER " + client_1)
    r1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.Address\\.ID:{" + addr_id + "}")

    # SECOND CLIENT
    r2 = connect_redis()
    r2.execute_command("CCT.REGISTER " + client_2)
    r2.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.Address\\.ID:{" + addr_id + "}")

    r1.connection_pool.disconnect()
    r2.connection_pool.disconnect()

    r3 = connect_redis()

    # Overwrite Address (remove it)
    d = {
        "User": {
            "ID": 2,
            "PASSPORT": passport_value
        },
    }

    r3.json().set(second_key, Path.root_path(), d)
    r3.execute_command("CCT.REGISTER " + client_1)

    # CHECK THE STREAM
    from_stream = r3.xread(count=5, streams={client_1: 0})
    assert 2 == len(from_stream[0][1])
    assert second_key != from_stream[0][1][0][1]['key']
    assert first_key == from_stream[0][1][0][1]['key']


def test_overwritten_value_not_matching_query_should_be_removed_form_tracked_single_client():
    r1 = connect_redis()
    cct_prepare.flush_db(r1)  # clean all db first
    cct_prepare.create_index(r1)
    client_1 = "client1"

    passport_value = "aaa"
    addr_id = "2000"
    d1 = cct_prepare.generate_single_object(1, addr_id, passport_value)
    d2 = cct_prepare.generate_single_object(2, addr_id, passport_value)
    first_key = cct_prepare.TEST_INDEX_PREFIX + str(1)
    second_key = cct_prepare.TEST_INDEX_PREFIX + str(2)
    r1.json().set(first_key, Path.root_path(), d1)
    r1.json().set(second_key, Path.root_path(), d2)

    # SECOND CLIENT
    r1 = connect_redis()
    r1.execute_command("CCT.REGISTER " + client_1)
    r1.execute_command("CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.Address\\.ID:{" + addr_id + "}")

    # Overwrite Address (remove it)
    d = {
        "User": {
            "ID": 2,
            "PASSPORT": passport_value
        },
    }

    r1.json().set(second_key, Path.root_path(), d)

    # CHECK THE STREAM
    from_stream = r1.xread(streams={client_1: 0})
    print(json.dumps(from_stream))

    r1.connection_pool.disconnect()
    r1 = connect_redis()

    r1.execute_command("CCT.REGISTER " + client_1)

    from_stream = r1.xread(streams={client_1: 0})
    assert second_key != from_stream[0][1][0][1]['key']
    assert first_key == from_stream[0][1][0][1]['key']


def test_add_events_should_be_reflected_in_snapshot_for_query():
    r1 = connect_redis()
    cct_prepare.flush_db(r1)
    cct_prepare.create_index(r1)
    client_1 = "test_add_delete_events_should_be_reflected_in_snapshot_for_query_1"

    # Add data
    passport_value = "aaa"
    d1 = cct_prepare.generate_single_object(1001, 2001, passport_value)
    d2 = cct_prepare.generate_single_object(1002, 2002, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    r1.json().set(key_1, Path.root_path(), d1)
    r1.json().set(key_2, Path.root_path(), d2)

    r1 = connect_redis()
    r1.execute_command("CCT.REGISTER " + client_1)

    r1.execute_command(
        "CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + passport_value + "}")

    key_6 = cct_prepare.TEST_INDEX_PREFIX + str(6)
    d6 = cct_prepare.generate_single_object(1006, 2006, passport_value)
    r1.json().set(key_6, Path.root_path(), d6)

    # CHECK THE STREAM
    from_stream = r1.xread(streams={client_1: 0})
    assert from_stream[0][1][1][1]['key'] == key_6

    r1.connection_pool.disconnect()
    r1 = connect_redis()

    r1.execute_command("CCT.REGISTER " + client_1)

    from_stream = r1.xread(streams={client_1: 0})
    assert from_stream[0][1][0][1]['key'] == key_6
    assert from_stream[0][1][1][1]['key'] == key_2
    assert from_stream[0][1][2][1]['key'] == key_1


def test_delete_events_should_be_reflected_in_snapshot_for_query():
    r1 = connect_redis()
    cct_prepare.flush_db(r1)
    cct_prepare.create_index(r1)
    client_1 = "test_delete_events_should_be_reflected_in_snapshot_for_query_1"

    # Add data
    passport_value = "aaa"
    d1 = cct_prepare.generate_single_object(1001, 2001, passport_value)
    d2 = cct_prepare.generate_single_object(1002, 2002, passport_value)
    d3 = cct_prepare.generate_single_object(1003, 2003, passport_value)
    key_1 = cct_prepare.TEST_INDEX_PREFIX + str(1)
    key_2 = cct_prepare.TEST_INDEX_PREFIX + str(2)
    key_3 = cct_prepare.TEST_INDEX_PREFIX + str(3)
    r1.json().set(key_1, Path.root_path(), d1)
    r1.json().set(key_2, Path.root_path(), d2)
    r1.json().set(key_3, Path.root_path(), d3)

    r1 = connect_redis()
    r1.execute_command("CCT.REGISTER " + client_1)
    r1.execute_command(
        "CCT.FT.SEARCH " + cct_prepare.TEST_INDEX_NAME + " @User\\.PASSPORT:{" + passport_value + "}")

    r1.delete(key_3)

    # CHECK THE STREAM
    from_stream = r1.xread(streams={client_1: 0})

    assert from_stream[0][1][1][1]['operation'] == 'DELETE'
    assert from_stream[0][1][1][1]['key'] == key_3

    r1.connection_pool.disconnect()
    r1 = connect_redis()

    r1.execute_command("CCT.REGISTER " + client_1)

    from_stream = r1.xread(streams={client_1: 0})
    assert from_stream[0][1][0][1]['operation'] == 'DELETE'
    assert from_stream[0][1][0][1]['key'] == key_3
