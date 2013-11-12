import yaml
import os


def getcfg(name):
    try:
        path = os.path.dirname(__file__)
        with open(os.path.join(path, 'config.yml'), 'rb') as fd:
            data = fd.read()
        data = yaml.load(data)
        value = data[name]
        return value
    except:
#        raise
        pass
    return


def setcfg(name, value):
    path = os.path.dirname(__file__)

    try:
        with open(os.path.join(path, 'config.yml'), 'rb') as fd:
            data = fd.read()
        data = yaml.load(data)
    except BaseException as e:
        data = {}

    if data is None:
        data = {}

    try:
        data[name] = value
        data = yaml.dump(data, default_flow_style=False)
        with open(os.path.join(path, 'config.yml'), 'wb') as fd:
            fd.write(data)
    except BaseException as e:
        print repr(e)
        return False
    return True
