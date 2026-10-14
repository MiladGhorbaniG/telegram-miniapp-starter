def __getattr__(name: str):
    if name in {"app", "celery_app"}:
        from config.celery import app as celery_app

        return celery_app
    raise AttributeError(name)
