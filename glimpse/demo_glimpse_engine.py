import asyncio

from glimpse.Glimpse import Draft, GlimpseEngine


async def main() -> None:
    engine = GlimpseEngine()
    draft = Draft(
        input_text="Send a brief status note about intermittent errors; keep tone calm and same channel.",
        goal="Reassure and provide next update time",
        constraints="No channel change; non-alarmist",
    )

    res1 = await engine.glimpse(draft)
    print("Attempt:", res1.attempt)
    print("Status:", res1.status)
    print("History:", res1.status_history)
    print("Sample:", res1.sample)
    print("Essence:", res1.essence)
    print("Delta:", res1.delta)

    if res1.status != "aligned":
        draft.goal += " (internal only)"
        res2 = await engine.glimpse(draft)
        print("Attempt:", res2.attempt)
        print("Status:", res2.status)
        print("History:", res2.status_history)

    engine.commit(draft)


if __name__ == "__main__":
    asyncio.run(main())
