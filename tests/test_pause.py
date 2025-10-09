from speech.pause_model import train_stub, predict_pause_type


def test_train_stub_priors_seeded():
    samples = [
        {"label": "rhetorical"},
        {"label": "handoff"},
        {"label": "rhetorical"},
    ]
    m1 = train_stub(samples, seed=123)
    m2 = train_stub(samples, seed=123)
    assert m1["priors"] == m2["priors"]
    assert m1["seed"] == m2["seed"] == 123


def test_predict_uses_priors():
    priors = {"rhetorical": 0.6, "handoff": 0.4}
    label = predict_pause_type(priors, {"duration": 1.2})
    assert label == "rhetorical"


