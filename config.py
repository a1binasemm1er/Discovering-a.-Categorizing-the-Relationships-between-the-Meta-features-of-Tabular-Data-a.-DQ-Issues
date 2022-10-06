from pathlib import Path
import yaml

class ConfigManager:
    def load(configfile):
        assert configfile is not None, "Config file not found"
        with open(configfile, 'r') as f:
            config = yaml.safe_load(f)
        assert "folders" in config, "`folders` not in config"

        # create folders if they don't exist
        for folder in config["folders"].values():
            Path(folder).mkdir(parents=True, exist_ok=True)
        return config
