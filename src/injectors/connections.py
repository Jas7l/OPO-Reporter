from base_module.injectors import PgConnectionInj
from config import config
from models import *  # noqa

pg = PgConnectionInj(
    conf=config.pg,
)
