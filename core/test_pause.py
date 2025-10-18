# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from speech.pause_model import (
    predict_pause_label,
    predict_pause_type,
    train_on_json,
    train_stub,
)


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


def test_train_on_json_and_predict_thresholds():
    model = train_on_json(
        [
            "data/podcasts/lex_musk.json",
            "data/podcasts/jre_trump.json",
        ],
        seed=7,
    )
    # Short pause should map to lowest-mean label (often handoff)
    assert (
        predict_pause_label(model, {"pause_after_s": 0.2})
        in model["thresholds"]["order"]
    )
    # Medium pause should map to middle label
    assert (
        predict_pause_label(
            model, {"pause_after_s": model["thresholds"]["low_mid"] + 1e-6}
        )
        in model["thresholds"]["order"]
    )
    # Long pause should map to highest label
    assert (
        predict_pause_label(
            model, {"pause_after_s": model["thresholds"]["high_mid"] + 0.5}
        )
        in model["thresholds"]["order"]
    )
