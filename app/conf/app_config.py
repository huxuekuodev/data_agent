from pathlib import Path

from omegaconf import OmegaConf

app_config_path = Path(__file__).parents[2] / "conf" / "app_config.yaml"
app_config = OmegaConf.load(app_config_path)
print(app_config)


class APPConfig:

    pass
