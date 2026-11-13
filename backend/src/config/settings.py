import os
DATABASE_URL=os.getenv('DATABASE_URL','mysql+pymysql://ordinal:ordinal-demo-local@localhost:17731/ordinal?charset=utf8mb4')
REDIS_URL=os.getenv('REDIS_URL','redis://localhost:6379/0')
JWT_SECRET=os.getenv('JWT_SECRET','local-ordinal-fibers-change-this-before-hosting')
SEED_DEMO=os.getenv('SEED_DEMO','false').lower()=='true'
