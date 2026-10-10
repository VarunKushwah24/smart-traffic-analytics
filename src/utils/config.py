import os
import yaml
from pathlib import Path

def get_project_root() -> Path:
    """Returns absolute path to the project root directory."""
    return Path(__file__).resolve().parent.parent.parent

def load_config(config_path: str = None) -> dict:
    """Loads configuration from YAML file."""
    root = get_project_root()
    if config_path is None:
        config_path = os.path.join(root, "config", "config.yaml")
    else:
        if not os.path.isabs(config_path):
            config_path = os.path.join(root, config_path)
            
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    return config
