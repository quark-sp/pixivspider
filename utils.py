import os
from datetime import datetime
import json

#创建基本路径
def create_dir():
    BASE_DIR=datetime.now().strftime('%Y_%m_%d')
    os.makedirs(BASE_DIR,exist_ok=True)
    img_dir=os.path.join(BASE_DIR,'images')
    json_dir=os.path.join(BASE_DIR,'json')

    for dir_path in [img_dir,json_dir]:
        os.makedirs(dir_path,exist_ok=True)
    
    return img_dir,json_dir

#验证配置文件
def validate_config(config):
    required_fields = ["headers", "ranking", "save"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing config section: {field}")
    if "mode" not in config["ranking"]:
        raise ValueError("Missing ranking mode in config.")