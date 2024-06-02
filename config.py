import json

default_config = {"base_directory": "C:/Users/Justin/Downloads/Heroes_assets_pngs"}

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        print("Creating config file")
        with open('config.json', "w") as config_file:
            json.dump(default_config, config_file, indent=2)
    
    return default_config
