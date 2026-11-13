import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from redis import Redis
from src.config.database import Base,engine
from src.config.settings import SEED_DEMO,REDIS_URL
from src import models
from src.routes import auth,studies,treatments,readings,runs,notes,audit
from src.middlewares.audit import AuditMiddleware
from src.middlewares.errors import ErrorMiddleware
from src.middlewares.rate_limit import RateLimitMiddleware
@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    try:
        import importlib.util
        from pathlib import Path
        migration_path=Path(__file__).resolve().parents[1]/'migrations'/'002_run_bootstrap.py'
        spec=importlib.util.spec_from_file_location('migration_002_run_bootstrap',migration_path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.ensure_run_bootstrap_columns()
    except Exception:logging.exception('bootstrap column migration failed; app remains available')
    if SEED_DEMO:
        try:
            from scripts.seed_demo import seed
            seed()
        except Exception:logging.exception('seed failed; app remains available')
    yield
app=FastAPI(title='青蘖纸浆等级比较簿',lifespan=lifespan)
@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):
    return JSONResponse(status_code=422,content={'detail':[{'loc':list(e['loc']),'msg':e['msg']} for e in exc.errors()]})
app.add_middleware(AuditMiddleware);app.add_middleware(RateLimitMiddleware);app.add_middleware(ErrorMiddleware)
for mod in (auth,studies,treatments,readings,runs,notes,audit):app.include_router(mod.router)
@app.get('/health')
def health():
    with engine.connect() as conn:conn.execute(text('SELECT 1'))
    Redis.from_url(REDIS_URL).ping();return {'status':'ok'}
