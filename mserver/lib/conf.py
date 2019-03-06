import yaml
from pathlib import Path

def conf_data(style,age=None):
    conf_file = Path(__file__).resolve().parent.parent / 'conf.yaml'
    data = yaml.load(conf_file.read_text(), Loader=yaml.FullLoader)
    if not age:
        return data.get(style)
    else:
        return data.get(style).get(age)
