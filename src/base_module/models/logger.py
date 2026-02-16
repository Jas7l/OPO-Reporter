import contextvars
import dataclasses as dc
import json
import logging
import os
import typing as t

import logstash

from .model import Model


@dc.dataclass
class ModuleLoggingConfig(Model):
    """."""

    name: str = dc.field()
    log_level: int = dc.field()


@dc.dataclass
class SyslogProviderConfig(Model):
    """."""

    host: str = dc.field()
    port: int = dc.field()
    app_extra: dict = dc.field(default_factory=dict)


@dc.dataclass
class LoggerConfig(Model):
    """."""

    root_log_level: t.Union[str, int] = dc.field(
        default='INFO',
        metadata={'type': str},
    )
    modules: t.List[ModuleLoggingConfig] = dc.field(
        default_factory=list,
        metadata={'type': list, 'items_type': ModuleLoggingConfig},
    )
    logstash: t.Optional[SyslogProviderConfig] = dc.field(default=None)


class StdoutFormatter(logging.Formatter):
    """."""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        declarer = record.__dict__.get('declarer', record.name)
        res = f'[{declarer}] {message}'
        if data := record.__dict__.get('data', {}):
            if isinstance(data, dict):
                data['trace_id'] = ClassesLoggerAdapter.TRACE_ID.get()
            return f'{res} -> {data}'

        return res


class LogstashAdaptiveFormatter(logstash.LogstashFormatterVersion1):
    """."""

    DUMP_CLS = None

    @classmethod
    def serialize(cls, message):
        dumped = json.dumps(message, cls=cls.DUMP_CLS)
        return dumped.encode('utf-8')


def setup_logging(config: LoggerConfig = None, dump_cls=None):
    if config:
        console = logging.StreamHandler()
        console.setFormatter(StdoutFormatter())
        logging.basicConfig(level=config.root_log_level, handlers=[console])

        if config.logstash:
            logstash_handler = logstash.TCPLogstashHandler(
                config.logstash.host,
                config.logstash.port,
                message_type='thematic',
                version=1,
            )
            logs_formatter = LogstashAdaptiveFormatter(message_type='thematic')
            LogstashAdaptiveFormatter.DUMP_CLS = dump_cls
            logstash_handler.setFormatter(logs_formatter)
            logging.getLogger().addHandler(logstash_handler)
            ClassesLoggerAdapter.APP_EXTRA = config.logstash.app_extra

        for module in config.modules:
            logging.getLogger(module.name).setLevel(module.log_level)
    else:
        logging.basicConfig(level=int(os.environ.get('LOG_LEVEL') or 10))


class ClassesLoggerAdapter(logging.LoggerAdapter):
    """."""

    APP_EXTRA = {}
    DEFAULT_TRACE_ID = 'root'
    TRACE_ID = contextvars.ContextVar('trace_id', default=DEFAULT_TRACE_ID)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.service_name = cls.__name__

    def __init__(self, **kwargs):
        """."""

        super().__init__(logging.getLogger(), kwargs.pop('extra', {}))

    @classmethod
    def create(cls, issuer: t.Union[str, t.Type, object], **kwargs):
        logger = cls(**kwargs)
        logger.service_name = issuer if isinstance(issuer, str) \
            else type(issuer).__name__
        return logger

    def process(self, msg, kwargs):
        kwargs['extra'] = {
            'data': kwargs.get('extra') or {},
            'declarer': self.service_name,
            'trace_id': self.TRACE_ID.get(),
            **self.extra,
            **self.APP_EXTRA
        }
        return msg, kwargs
