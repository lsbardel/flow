# import fastest json available
try:
    try:
        import json
    except ImportError:
        try:
            import cjson as json
        except ImportError:
            try:
                import simplejson as json
            except ImportError:
                import demjson as json
except ImportError:
    raise ImportError, "Could not load one of: Python json, cjson, simplejson, demjson. Please install a json module."

if hasattr(json, 'encode'):
    encode = json.encode
    decode = json.decode
elif hasattr(json, 'dumps'):
    encode = json.dumps
    decode = json.loads
elif hasattr(json, 'write'):
    encode = json.write
    decode = json.read
else:
    raise ImportError, 'Loaded unknown json module: "%s"'%(json.__file__,)

dumps  = encode
loads  = decode
