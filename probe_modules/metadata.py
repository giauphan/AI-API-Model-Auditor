from typing import Any, Dict, List, Optional
import hashlib
import re
from probe_modules.probes import BaseProbe
from probe_modules.observations import Observation


class MetadataProbe(BaseProbe):
    def __init__(
        self,
        name: str = "MetadataProbe",
        max_cost: float = 1.0,
        max_concurrency: int = 1,
    ):
        super().__init__(name, max_cost, max_concurrency)

    async def run_probe(self, adapter: Any) -> List[Observation]:
        # This probe works a bit differently and typically expects the
        # response directly, but to satisfy BaseProbe interface we
        # implement this basic check. The main logic is in extract_metadata.
        return []

    def _redact(self, text: str) -> str:
        # Improved redaction for PII/Secrets matching BaseProbe behavior
        text = re.sub(r"sk-[a-zA-Z0-9_-]+", "[REDACTED]", text)
        return text

    def _redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in data.items():
            if isinstance(v, str):
                result[k] = self._redact(v)
            elif isinstance(v, dict):
                result[k] = self._redact_dict(v)
            elif isinstance(v, list):
                # Redact strings, recurse for dicts in list, else keep
                mapped_list = []
                for item in v:
                    if isinstance(item, str):
                        mapped_list.append(self._redact(item))
                    elif isinstance(item, dict):
                        mapped_list.append(self._redact_dict(item))
                    else:
                        mapped_list.append(item)
                result[k] = mapped_list
            else:
                result[k] = v
        return result

    def extract_metadata(
        self,
        response: Any,
        requested_model: str,
        raw_request: Optional[Dict[str, Any]] = None,
        raw_response: Optional[str] = None,
    ) -> List[Observation]:
        """
        Extracts metadata from an adapter response.
        """

        if not isinstance(response, dict):
            return [
                Observation(
                    type="error",
                    data={"message": "Response is not a dictionary"},
                    evidence_strength="high",
                )
            ]

        returned_model = response.get("model")
        response_id = response.get("id")
        usage = response.get("usage", {})
        headers = response.get("headers", {})

        # Redact headers and usage just in case
        headers = self._redact_dict(headers)
        usage = self._redact_dict(usage)

        latency = response.get("latency", 0.0)
        stream_format = response.get("stream_format")

        finish_reason = None
        if (
            "choices" in response
            and isinstance(response["choices"], list)
            and len(response["choices"]) > 0
        ):
            finish_reason = response["choices"][0].get("finish_reason")
        elif "content" in response and "stop_reason" in response:
            finish_reason = response.get("stop_reason")

        raw_response_hash = None
        if raw_response:
            raw_hash = hashlib.sha256(raw_response.encode("utf-8")).hexdigest()
            raw_response_hash = raw_hash

        metadata = {
            "requested_model": requested_model,
            "returned_model": returned_model,
            "response_id": response_id,
            "finish_reason": finish_reason,
            "usage": usage,
            "headers": headers,
            "latency": latency,
            "stream_format": stream_format,
            "raw_response_hash": raw_response_hash,
        }

        if raw_request:
            # Capture the raw request, but redact it
            redacted_raw_request = self._redact_dict(raw_request)
            metadata["raw_request"] = redacted_raw_request
            metadata["raw_request_captured"] = True

        observations = []

        if returned_model and returned_model != requested_model:
            observations.append(
                Observation(
                    type="model_mismatch",
                    data={
                        "requested": requested_model,
                        "returned": returned_model,
                    },
                    evidence_strength="high",
                )
            )

        observations.append(
            Observation(
                type="response_metadata",
                data=metadata,
                evidence_strength="medium",
            )
        )

        return observations
