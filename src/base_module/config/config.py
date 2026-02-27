import dataclasses as dc

from ..models import Model


@dc.dataclass
class PgConfig(Model):
    """Конфиг настройки postgres"""

    host: str = dc.field()
    port: int = dc.field()
    user: str = dc.field()
    password: str = dc.field()
    database: str = dc.field()
    max_pool_connections: int = dc.field(default=100)
    debug: bool = dc.field(default=False)
    schema: str = dc.field(default='public')
