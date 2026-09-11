# PhoneAgent — session summary (2026-09-08 to 2026-09-11)

## What got built

A local, privacy-respecting phone assistant for your Poco phone: an Android app
(execution) talking to a Python brain server on this PC (understanding, via a
local Ollama model). Full architecture is in `design.txt` — this file is just
a log of what happened and what's left.

**android-app/** (Kotlin, Gradle) — installs as a sideloaded APK:
- Single-screen UI: type or speak a command, see `heard -> understood -> did`.
- `speech/SpeechModule.kt` — Android's built-in `SpeechRecognizer`.
- `network/BrainClient.kt` — talks to the brain server's `/parse-intent`.
- `intent/`, `action/`, `resolver/` — the deterministic pipeline: a fixed
  JSON schema is mapped to a Kotlin sealed class, then dispatched to one
  specific Android API call per intent. The model never decides what code
  runs, only what the intent *is*.
- Fixed v1 action set: OpenApp, CloseApp, Call, CreateCalendarEvent,
  CreateReminder, Unknown.
- On any failure (including Unknown), the app now asks "could you say that
  again?" and re-opens the mic automatically if the command was spoken
  (capped at 2 retries) — added this session per your request, instead of
  silently dropping unrecognized commands.

**brain-server/** (Python, FastAPI) — runs on this PC:
- `POST /parse-intent` — local Ollama model (currently `qwen2.5:3b-instruct`)
  turns text into one of the 6 schema shapes; Pydantic validates/coerces
  anything malformed to `Unknown` before it ever reaches the phone.
- Warms the model up at server startup so the ~100s cold-load cost is paid
  once, not on your first real command.

**Tooling installed this session:** Android Studio (JDK 17 + SDK), Eclipse
Temurin JDK 17 (Android Studio's bundled JDK 25 turned out incompatible with
Gradle 8.9), Ollama, Python deps. All local, all free.

**Tests:** 27 automated tests (pytest, mocked — no live model needed) plus 1
live sanity test, and Android JVM unit tests for `IntentMapper`, `Fuzzy`,
`ActionIntent`, `ExecutionResult`. All green as of this session. A pre-push
git hook exists at `scripts/hooks/pre-push` (runs both suites, but only when
a push touches this project) — **not activated yet**, needs:
```
git config core.hooksPath "ai/phone agent/scripts/hooks"
```
(that's a repo-wide setting — only run it if nothing else in `self-using-utils`
already uses a different hooks path).

## What was tried and reverted

Built server-side Whisper STT (faster-whisper) + a phone-side language
setting + a "you're speaking a different language than configured, switch?"
dialog, to fix real Hebrew-recognition failures seen in testing. It worked
(verified live), but made things slower (~24s/command) and you decided to
prioritize speed + English-only instead. Fully reverted via git — none of it
is in the current code, but it's recoverable from git history (commit
history on `main` around 2026-09-11, look for the STT/Whisper-related diffs)
if Hebrew support becomes a priority again later.

Also tried `qwen2.5:3b-instruct` instead of `7b` for speed. Honest result
(tested live with 5 example commands, not just theory): **not meaningfully
faster** — still 9-36s per command depending on complexity. This machine has
no GPU, so the bottleneck is CPU-bound generation time, which doesn't scale
down linearly with model size the way I'd hoped. Real options if this speed
is still a problem: a much smaller model (1.5b/0.5b, real accuracy risk for
a 3-parameter slot-extraction task), or accept the latency, or revisit this
once/if a GPU is available. `qwen2.5:7b-instruct` (4.7GB) is still on disk,
unused, in case you want to A/B compare accuracy later.

## What's on GitHub now

Pushed to `talthegever/self-using-utils`, under `ai/phone agent/`:
- `9c651b4` — v1 app + server (initial checkpoint)
- `d7a5275` — test coverage + pre-push hook
- `a86eca1` — qwen2.5:3b-instruct swap (current HEAD)

Nothing force-pushed, nothing deleted from what was already on the remote.

## What's tested vs. not

**Verified on the real device (earlier in this session):** OpenApp (opened
Chrome and Camera for real), server connectivity/pairing over wireless ADB,
MIUI's install-restriction and permission quirks.

**Verified server-side only (curl/pytest), not yet on the real phone:**
Call, CreateCalendarEvent, CreateReminder, Unknown-handling — the brain
server produces correct JSON for all of these, but `ActionExecutor`'s
actual on-device execution of them hasn't been watched happening on your
phone yet.

**Not tested at all yet:**
- **CloseApp** — needs Accessibility Service manually enabled on the phone
  first (Settings > Accessibility > PhoneAgent), which hadn't happened as of
  this session. The gesture-dispatch implementation is a first pass and
  will likely need on-device tuning against MIUI's actual Recents UI.
- The new "ask for clarification and re-listen" retry behavior — built and
  compiles, never exercised with a real failed voice command.
- Calendar/reminder side effects on your actual calendar/notifications.

## Next steps, in rough priority order

1. **Reconnect the phone**, rebuild (`gradlew assembleDebug`), reinstall,
   and actually test Call/Calendar/Reminder/Unknown end-to-end on-device —
   this is the biggest gap between "works on paper" and "actually works."
2. **Enable Accessibility Service** on the phone, then test CloseApp and
   iterate on the gesture logic against the real Recents UI.
3. Decide whether the current LLM latency (9-36s/command) is acceptable
   long-term, or worth another pass (smaller model, or wait for GPU).
4. Activate the pre-push hook (`core.hooksPath`, see above) once you're
   comfortable with it running repo-wide.
5. v2 backlog, unchanged from `design.txt` section 13: screen/notification
   reading (the feature that originally motivated this project), wake-word,
   TTS responses, direct-dial instead of dialer-only.
