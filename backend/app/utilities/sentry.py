import sentry_sdk

from ..utilities import SENTRY_DSN

def init_sentry():
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )