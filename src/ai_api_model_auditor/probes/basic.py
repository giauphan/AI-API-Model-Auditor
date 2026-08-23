from typing import Dict, Any, List

def run_basic_probes(adapter: Any, model: str) -> List[Dict[str, Any]]:
    """
    Runs a deterministic set of basic probes against the specified model.
    """
    prompts = [
        {"role": "user", "content": "What is 2+2? Reply only with the number 4."},
        {"role": "user", "content": "Repeat the word 'apple' 3 times."}
    ]

    observations = []

    for prompt in prompts:
        try:
            response_data = adapter.chat(model, [prompt], max_tokens=50)
            observations.append({
                "prompt": prompt["content"],
                "status": "success",
                "response": response_data.get("content", ""),
                "raw_response": response_data.get("raw_response", {})
            })
        except Exception as e:
            observations.append({
                "prompt": prompt["content"],
                "status": "error",
                "error": str(e)
            })

    return observations
