"""Print a one-second heartbeat for 30 seconds during a manual buffer-read probe."""

import os
import time
from datetime import datetime, timezone


def main():
    duration = 30
    run_id = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"SHELLMCPEEK_ACTIVITY start run={run_id} pid={os.getpid()} duration={duration}s", flush=True)
    started = time.monotonic()
    max_delay = 0.0
    try:
        for tick in range(1, duration + 1):
            deadline = started + tick
            time.sleep(max(0.0, deadline - time.monotonic()))
            now = time.monotonic()
            delay = max(0.0, now - deadline)
            max_delay = max(max_delay, delay)
            print(
                f"SHELLMCPEEK_ACTIVITY tick={tick:02d}/{duration} "
                f"elapsed={now - started:.3f}s delay={delay * 1000:.1f}ms",
                flush=True,
            )
    except KeyboardInterrupt:
        print("SHELLMCPEEK_ACTIVITY interrupted", flush=True)
        return 130
    print(
        f"SHELLMCPEEK_ACTIVITY completed elapsed={time.monotonic() - started:.3f}s "
        f"max_tick_delay={max_delay * 1000:.1f}ms",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
