import json

DEFAULTS = {
    "network": "VGG16",
    "hard-cut detector": {
        "encoder": "VGG16",
        "input_dim": 224,
        "pool" : 1,
        "weights": "imagenet",
        "child_process": 1
    },
    "soft-cut detector": {
        "window_size":100
    }
}
def _merge(src, dst):
    for k, v in src.items():
        if k in dst:
            if isinstance(v, dict):
                _merge(src[k], dst[k])
        else:
            dst[k] = v


def load_config(config_file, defaults=DEFAULTS):
    with open(config_file, "r") as fd:
        config = json.load(fd)
    _merge(defaults, config)
    return config