class Auditor:
    def claim_model_identity(self, certainty: str, evidence_strength: str) -> str:
        if certainty == "DEFINITIVE" and evidence_strength != "DEFINITIVE":
            raise ValueError("Unsupported certainty claim: exact hidden-model identity cannot be claimed without definitive technical evidence.")
        return "Claim valid"
