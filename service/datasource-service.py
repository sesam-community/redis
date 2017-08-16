from flask import Flask, Response, request
import json
import os
import redis
import logging

app = Flask(__name__)

host = os.environ.get("HOST", "localhost")
port = os.environ.get("PORT", 6379)
db = os.environ.get("DB", 0)
r = redis.StrictRedis(host=host, decode_responses=True, port=port, db=db)


@app.route('/', methods=['GET'])
def get_entities():
    def generate():
        first = True
        yield "["
        for key in r.scan_iter():
            # do something with the key
            redis_type = r.type(key)
            entity = {"_id": key, "redis_type": redis_type}
            if redis_type == "hash":
                info = r.hgetall(key)
                for vkey, value in info.items():
                    entity[vkey] = value
            elif redis_type == "zset":
                info = r.zscan(key, 0)
                # info[0] just contains the set size
                for (a, b) in enumerate(info[1]):
                    entity[b[0]] = b[1]
            else:
                logger.warn("key redis_type %s is not supported" % redis_type)

            if not first:
                yield ","
            yield json.dumps(entity)
            first = False
        yield "]"

    return Response(generate(), mimetype='application/json')


@app.route('/', methods=['POST'])
def post_entities():
    entities = request.get_json()
    for entity in entities:
        entity_id = entity["_id"]
        redis_type = entity.get("redis_type", "hash")
        if redis_type == "hash":
            def update(k, v): r.hset(entity_id, k, v)
        elif redis_type == "zset":
            def update(k, v): r.zadd(entity_id, v, k)
        else:
            logger.warn("redis_type %s is not supported" % redis_type)
            continue
        for key in entity:
            if key not in ("_id", "redis_type"):
                update(key, entity[key])
    return Response("Thanks!", mimetype='text/plain')

if __name__ == '__main__':
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('redis')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)

    app.run(threaded=True, debug=True, host='0.0.0.0')
