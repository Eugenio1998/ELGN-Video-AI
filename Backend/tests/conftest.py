# 📄 tests/conftest.py

import os
import types
import sys
from dotenv import load_dotenv

# === 🧪 Carrega .env.test para testes com PostgreSQL real ===
load_dotenv(dotenv_path=".env.test")

# ✅ Mock principal do rq (mantido)
mock_rq = types.ModuleType("rq")

class MockQueue:
    def __init__(self, *args, **kwargs): pass
    def enqueue(self, *args, **kwargs): return MockJob()

class MockJob:
    id = "fake-job-id"
    def get_status(self): return "mocked"
    def result(self): return "success"

mock_rq.Queue = MockQueue
mock_rq.Worker = lambda *args, **kwargs: None
mock_rq.Connection = lambda *args, **kwargs: None
mock_rq.SimpleWorker = lambda *args, **kwargs: None
mock_rq.SpawnWorker = lambda *args, **kwargs: None

# Submódulo rq.job
mock_rq_job = types.ModuleType("rq.job")
mock_rq_job.Job = MockJob

sys.modules["rq"] = mock_rq
sys.modules["rq.job"] = mock_rq_job
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
