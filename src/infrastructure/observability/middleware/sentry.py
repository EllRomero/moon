from sentry_sdk.integrations.asgi import SentryAsgiMiddleware


def add_sentry_middleware(app):
    """adding a middleware for tracebacks in the center"""
    app.add_middleware(SentryAsgiMiddleware)
