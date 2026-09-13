import os

def is_resources_changed(dir_path, last_modification_time):
    return os.path.getatime(dir_path) != last_modification_time


print(is_resources_changed("data/datasets_public", os.path.getatime("data/datasets_public")))