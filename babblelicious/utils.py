def load_class(class_path):
    module_name, class_name = class_path.rsplit('.', 1)
    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)
