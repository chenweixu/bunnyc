import yaml
from pathlib import Path


def conf_data(style, age=None):
    conf_file = str(Path(__file__).resolve().parent.parent / 'etc/conf.yaml')
    # conf_file = str(Path(__file__).resolve().parent.parent / 'etc/devel.yaml')
    data = yaml.load(open(conf_file, 'r').read())
    if not age:
        return data.get(style)
    else:
        return data.get(style).get(age)
