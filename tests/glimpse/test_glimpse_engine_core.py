import asyncio

from glimpse.Glimpse import Draft, GlimpseEngine


def test_two_tries_then_redial_and_reset():
    async def run():
        engine = GlimpseEngine()
        d = Draft(input_text="hello", goal="", constraints="")

        r1 = await engine.glimpse(d)
        assert r1.attempt == 1

        r2 = await engine.glimpse(d)
        assert r2.attempt == 2

        # Third attempt should immediately request redial
        r3 = await engine.glimpse(d)
        assert r3.status == "redial"
        assert r3.status_history == ["Clean reset. Same channel. Let's try again."]

        # After commit/reset we can start again from attempt 1
        engine.commit(d)
        r4 = await engine.glimpse(d)
        assert r4.attempt == 1

    asyncio.run(run())


def test_latency_statuses_and_stale():
    async def run():
        # Custom sampler that delays past t4 to force stale
        async def slow_sampler(_d: Draft):
            await asyncio.sleep(6.5)  # > 6000 ms (t4 threshold)
            return ("sample", "essence", None, True)

        engine = GlimpseEngine(sampler=slow_sampler)
        r = await engine.glimpse(Draft(input_text="x", goal="g", constraints="c"))

        # Should include a trying status and degraded + stale
        assert any(s.startswith("Glimpse 1") for s in r.status_history)
        assert any("Still trying" in s for s in r.status_history)
        assert any("Stale result" in s for s in r.status_history)
        assert r.stale is True
        assert r.status == "stale"

    asyncio.run(run())


def test_cancel_on_edit_does_not_consume_try_and_debounces():
    async def run():
        # Sampler that takes enough time to allow cancel before finishing
        async def medium_sampler(_d: Draft):
            await asyncio.sleep(0.5)
            return ("s", "e", None, True)

        engine = GlimpseEngine(sampler=medium_sampler)

        # Start glimpse as a task
        task = asyncio.create_task(
            engine.glimpse(Draft(input_text="x", goal="", constraints=""))
        )
        # Cancel quickly (simulate user editing)
        await asyncio.sleep(0.05)
        engine.cancel()
        r_cancel = await task

        # Cancel returns not_aligned and should not consume the try
        assert r_cancel.status == "not_aligned"

        # Next glimpse should still be attempt 1 (since previous was canceled and rolled back)
        r1 = await engine.glimpse(Draft(input_text="x", goal="", constraints=""))
        assert r1.attempt == 1

    asyncio.run(run())


def test_clarifier_when_intent_unspecified():
    import os

    async def run():
        # Enable pre-execution clarifier for this test
        old_val = os.environ.get("GLIMPSE_PREEXEC_CLARIFIER")
        os.environ["GLIMPSE_PREEXEC_CLARIFIER"] = "true"

        try:
            # Need to reimport to pick up the env var change
            from glimpse.engine import GlimpseEngine as ReloadedEngine

            engine = ReloadedEngine()
            r = await engine.glimpse(
                Draft(input_text="message", goal="", constraints="")
            )

            # With unspecified goal, clarifier should appear in delta and mark not_aligned
            assert r.status == "not_aligned"
            assert r.delta is not None
            assert "Clarifier:" in r.delta
        finally:
            # Restore original value
            if old_val is None:
                os.environ.pop("GLIMPSE_PREEXEC_CLARIFIER", None)
            else:
                os.environ["GLIMPSE_PREEXEC_CLARIFIER"] = old_val

    asyncio.run(run())


def test_essence_only_mode_hides_sample():
    async def run():
        engine = GlimpseEngine()
        engine.set_essence_only(True)
        r = await engine.glimpse(
            Draft(
                input_text="some long message that would normally produce a sample",
                goal="g",
                constraints="",
            )
        )
        assert r.essence
        assert r.sample == ""

        engine.set_essence_only(False)
        r2 = await engine.glimpse(
            Draft(input_text="some long message again", goal="g", constraints="")
        )
        assert r2.sample != ""

    asyncio.run(run())
