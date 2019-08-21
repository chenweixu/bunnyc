
import yaml

def conf_data(style, age=None):
    work_dir = Path(__file__).resolve().parent.parent
    conf_file = work_dir / 'conf.yaml'
    data = yaml.load(conf_file.read_text(), Loader=yaml.FullLoader)
    if not age:
        return data.get(style)
    else:
        return data.get(style).get(age)
