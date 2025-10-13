<<<<<<< Updated upstream
from speech.pause_model import predict_pause_type, train_stub

=======
from speech.pause_model import (
    predict_pause_label,
    predict_pause_type,
    train_on_json,
    train_stub,
)

>>>>>>> Stashed changes


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
<<<<<<< Updated upstream
=======


def test_train_on_json_and_predict_thresholds():
    model = train_on_json([
        "data/podcasts/lex_musk.json",
        "data/podcasts/jre_trump.json",
    ], seed=7)
    # Short pause should map to lowest-mean label (often handoff)
    assert predict_pause_label(model, {"pause_after_s": 0.2}) in model["thresholds"]["order"]
    # Medium pause should map to middle label
    assert predict_pause_label(model, {"pause_after_s": model["thresholds"]["low_mid"] + 1e-6}) in model["thresholds"]["order"]
    # Long pause should map to highest label
    assert predict_pause_label(model, {"pause_after_s": model["thresholds"]["high_mid"] + 0.5}) in model["thresholds"]["order"]


>>>>>>> Stashed changes
