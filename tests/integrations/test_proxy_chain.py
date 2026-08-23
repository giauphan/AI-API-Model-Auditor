from modelaudit.integrations.proxy_chain import Hop, HopObservation, ProxyChain


def test_hop_observation_creation():
    obs = HopObservation(
        changed_model_id="new-model",
        inserted_prompts=["You are a helpful assistant."],
        rewritten_headers={"X-Forwarded-For": "127.0.0.1"},
        protocol_translation="HTTP/1.1 to HTTP/2",
        fallback_event="Model timeout, fallback triggered",
    )
    assert obs.changed_model_id == "new-model"
    assert obs.inserted_prompts == ["You are a helpful assistant."]
    assert obs.rewritten_headers == {"X-Forwarded-For": "127.0.0.1"}
    assert obs.protocol_translation == "HTTP/1.1 to HTTP/2"
    assert obs.fallback_event == "Model timeout, fallback triggered"


def test_hop_creation():
    obs = HopObservation(changed_model_id="another-model")
    hop = Hop(hop_id="hop-1", observations=obs)
    assert hop.hop_id == "hop-1"
    assert hop.observations.changed_model_id == "another-model"
    assert hop.observations.inserted_prompts == []


def test_proxy_chain_add_get_hop():
    chain = ProxyChain()
    hop1 = Hop(hop_id="gateway")
    hop2 = Hop(
        hop_id="internal-proxy",
        observations=HopObservation(changed_model_id="internal-v2"),
    )

    chain.add_hop(hop1)
    chain.add_hop(hop2)

    assert len(chain.hops) == 2
    assert chain.get_hop("gateway") == hop1
    assert chain.get_hop("internal-proxy") == hop2
    assert chain.get_hop("non-existent") is None


def test_proxy_chain_comparison():
    chain1 = ProxyChain()
    chain2 = ProxyChain()

    hop1 = Hop(hop_id="h1")
    hop2 = Hop(hop_id="h2", observations=HopObservation(changed_model_id="m1"))

    chain1.add_hop(hop1)
    chain1.add_hop(hop2)

    # Same structure
    chain2.add_hop(Hop(hop_id="h1"))
    chain2.add_hop(Hop(hop_id="h2", observations=HopObservation(changed_model_id="m1")))

    assert chain1.compare_chains(chain2) is True

    # Different number of hops
    chain3 = ProxyChain()
    chain3.add_hop(hop1)
    assert chain1.compare_chains(chain3) is False

    # Same number, different observations
    chain4 = ProxyChain()
    chain4.add_hop(hop1)
    chain4.add_hop(Hop(hop_id="h2", observations=HopObservation(changed_model_id="m2")))
    assert chain1.compare_chains(chain4) is False

    # Same hops, different order
    chain5 = ProxyChain()
    chain5.add_hop(hop2)
    chain5.add_hop(hop1)
    assert chain1.compare_chains(chain5) is False
