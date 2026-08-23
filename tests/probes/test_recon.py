from ai_api_model_auditor.probes.recon import probe_endpoint
from ai_api_model_auditor.adapters.base import BaseAdapter

class DummyAdapter(BaseAdapter):
    def get_provider_name(self): return "dummy"
    def list_models(self): return ["model1", "model2"]
    def chat(self, model, messages, **kwargs): return {}

class FailingAdapter(BaseAdapter):
    def get_provider_name(self): return "failing"
    def list_models(self): raise Exception("Connection error")
    def chat(self, model, messages, **kwargs): return {}

def test_probe_endpoint_success():
    adapter = DummyAdapter()
    findings = probe_endpoint(adapter)
    assert findings["status"] == "success"
    assert findings["provider"] == "dummy"
    assert findings["models_discovered"] == ["model1", "model2"]

def test_probe_endpoint_failure():
    adapter = FailingAdapter()
    findings = probe_endpoint(adapter)
    assert findings["status"] == "failed"
    assert "Connection error" in findings["error"]
