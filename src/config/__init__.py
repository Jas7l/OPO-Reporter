import dataclasses as dc
import os

import yaml
from base_module.config import PgConfig
from base_module.models import Model


@dc.dataclass
class AppConfig(Model):
    """Конфиг приложения"""

    pg: PgConfig
    sync_interval: int = dc.field(default=60)
    debug: bool = dc.field(default=False)


config: AppConfig = AppConfig.load(
    yaml.safe_load(open(os.getenv('YAML_PATH', '/app/config.yaml'))) or {}
)
