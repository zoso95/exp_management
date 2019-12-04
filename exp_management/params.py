import os
import json
from pathlib import Path
import numpy as np

"""

#TODO think about directory structure

def load(filepath):
    with open(filepath) as json_file:
        data = json.load(json_file)
    return Parameters(data)
"""


class Parameters:
    """
    A fancy dict that is useful for experiments.
    p = params.Parameters({"a":1, "prob":"!uni(0,1)"})

    p["a"], p.a will return 1
    p.prob, p["prob"] will get a new sample every time it is called.

    p.last_sample is a dict of the last sampled values for everything.

    there are special strings "!uni(a,b)", "!rint(a,b)", and "!eval(python code)"

    p.dict() gets you the parameter name, and the string used for it.
    """

    def __init__(self, init_values):
        super().__setattr__("last_sample", {})
        super().__setattr__("functions", {})
        super().__setattr__("keys", set())
        super().__setattr__("key_strings", {})
        super().__setattr__("_special_strings", ["!uni", "!rint", "!eval"])
        super().__setattr__("_reserved", dir(self))
        for k, v in init_values.items():
            self._add_param(k, v)

    """
    #TODO think about directory structure

    def save(self, filename, output_dir=None):

        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        full_path = os.path.join(output_dir, filename)

        with open(full_path, "w") as f:
            f.write(json.dumps(self.dict()))
    """

    def dict(self):
        return self.key_strings

    def items(self):
        return [(k, self[k]) for k in self.keys]

    def __setattr__(self, attr, value):
        self._add_param(attr, value)

    def __setitem__(self, key, value):
        self._add_param(key, value)

    def __dir__(self):
        return super().__dir__() + [str(k) for k in self.keys]

    def _get_and_save(self, key):
        v = self.functions[key]()
        self.last_sample[key] = v
        return v

    def _add_param(self, name, value):
        if name in self._reserved:
            raise Exception("Cannot use {} as a parameter".format(name))

        self.keys.add(name)
        self.key_strings[name] = value
        if name not in self.last_sample:
            self.last_sample[name] = None

        self.functions[name] = self._make_function(value)

    def __getattr__(self, attr):
        if attr in self.keys:
            v = self.functions[attr]()
            self.last_sample[attr] = v
            return v
        else:
            return super().__getattr__(attr)

    def __getitem__(self, key):
        if key in self.keys:
            v = self.functions[key]()
            self.last_sample[key] = v
            return v
        raise Exception("{} not in parameters".format(key))

    def get(self, key, default):
        if key in self.keys:
            return self[key]
        return default

    def _make_function(self, v):
        if isinstance(v, str):
            if v.startswith("!"):
                if any([v.startswith(s) for s in self._special_strings]):
                    if v.startswith("!uni"):
                        rng = v[len("!uni("):-1]
                        low, high = rng.split(",")
                        low, high = float(low), float(high)
                        return lambda: np.random.uniform(low, high)
                    elif v.startswith("!rint"):
                        rng = v[len("!rint("):-1]
                        low, high = rng.split(",")
                        low, high = int(low), int(high)
                        return lambda: np.random.randint(low, high)
                    elif v.startswith("!eval"):
                        string = v[len("!eval("):-1]
                        return lambda:eval(string)
                else:
                    raise Exception("Do not know how to make a function from {}".format(v))
                pass
            else:
                return lambda:v
        else:
            return lambda:v
