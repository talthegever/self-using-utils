# CLAUDE.md — PhoneAgent

Read this before proposing changes. It records **why** things are the way they
are, so settled decisions don't get re-litigated and reverted work doesn't get
rebuilt.

Companion docs:
- `design.txt` — the intended architecture (what the system *is*).
- `SESSION_NOTES.md` — what's actually built and tested vs. not (current state).

## What this project is

A local, private Siri/Bixby alternative for the user's **Poco X6 Pro (MIUI/
HyperOS)**. Two halves:

- **`android-app/`** (Kotlin) — owns the mic, the UI, and *all execution*.
- **`brain-server/`** (Python/FastAPI on the user's PC) — owns *understanding
  only*, via a local Ollama model. No cloud AI, no paid API.

The original motivation was reading messages off the screen. That's **v2** —
v1 deliberately ships a small fixed action set first.

---

## Load-bearing decisions (do not silently reverse)

### 1. The AI understands; it never decides what runs
This is the core constraint the user set, and everything else follows from it.
The model's only job is text → one of 6 fixed intents. Execution is a
`when` dispatch over a Kotlin **sealed class**, one fixed function per intent,
each calling one specific Android API.

Enforced in three places on purpose (belt *and* suspenders):
1. Server-side Pydantic validation coerces anything non-conforming → `Unknown`.
2. `IntentMapper` on the phone re-validates rather than trusting the server.
3. The sealed class makes "some other action" a compile error.

**Never** add a freeform/passthrough intent, let the model emit a package name
or phone number directly, or build an action dynamically from model output.
Slot values are raw text (`"spotify"`); resolving that to a real package or
contact happens **on-device** in `AppResolver`/`ContactResolver`.

### 2. Failures ask for clarification; they never guess or silently drop
Any `ExecutionResult.Failure` (including `Unknown`) prompts "could you say that
again?" and, if the command was spoken, re-opens the mic — capped at 2 retries
so an unreachable server can't loop forever. Added because the user watched a
misunderstood command get silently dropped. Still deterministic: a fixed rule,
not the model guessing.

### 3. Android's `SpeechRecognizer`, not Whisper — speed over multilingual
**A full server-side faster-whisper pipeline was built, verified working, and
then reverted on 2026-09-11.** Don't rebuild it without new information.

- Why it was built: Android's STT mangled the user's Hebrew (real observed
  output: `"??? ???? ????? and alarm in one hour ahead"`).
- Why it was reverted: it pushed a voice command to **~24s** (13s transcribe +
  11s parse), plus an **8-minute** first-run model warm-up. Asked directly, the
  user chose speed and English-only.
- Recoverable from git history (~2026-09-11) if Hebrew becomes a priority.
- Also built and reverted with it: a per-language setting + a "you're speaking
  a different language than configured, switch?" dialog. Same fate, same reason.

### 4. Latency is an open problem, and model size is NOT the lever
Currently **9–36s per command**, varying with complexity.

`qwen2.5:7b-instruct` → `qwen2.5:3b-instruct` was tried explicitly for speed and
**measured to make no meaningful difference**. This box has no GPU, so the cost
is CPU-bound token generation, which doesn't scale down with parameter count the
way you'd hope. 7b is still on disk if you want to A/B accuracy.

Don't propose "just use a smaller model" as if it's untested — it was tested.
Untried levers: a much smaller model (1.5b/0.5b, real accuracy risk on a
slot-extraction task), constraining `num_predict`, or a GPU.

Cold-start *is* solved: the model is warmed at server startup and held with
`keep_alive`, because a cold load (~60–100s) otherwise lands on the user's first
command and blows past the phone's HTTP timeout.

### 5. `Call` opens the dialer; it does not place calls
`ACTION_DIAL`, not `ACTION_CALL` — the user confirms. Upgrading is a one-line
change, deliberately deferred until trusted. Treat as a safety default.

### 6. Build from the CLI with JDK 17 — not the bundled JBR, not the GUI
Android Studio here bundles **JDK 25, which Gradle 8.9 rejects**. Use Eclipse
Temurin 17. The whole loop is command-line so it can be driven without the user
clicking through the IDE:

```bash
export JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-17.0.20.101-hotspot"
cd android-app && ./gradlew.bat assembleDebug
```

`adb` lives at `$LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe` — **use that
one.** There's an ancient `C:\Windows\adb.exe` (v1.0.32) on PATH that predates
wireless pairing and will fail confusingly.

### 7. Tests split by "does this need real hardware"
Fast JVM/pytest tests for pure logic; **no Robolectric**. `ActionExecutor`,
`AppResolver`, `ContactResolver`, and the accessibility service are validated
on-device, not mocked — mocking them would test the mocks. The model's
*judgment* isn't unit-tested either; one opt-in `pytest -m live` smoke test
checks the pipe (server → Ollama → schema-valid JSON), nothing more.

---

## MIUI/HyperOS gotchas (rediscovered the hard way)

- **`INSTALL_FAILED_USER_RESTRICTED`** — MIUI blocks ADB installs until "USB
  debugging (Security settings)" is on, which **requires a Mi account login**.
- **`pm grant` is blocked** (`SecurityException: GRANT_RUNTIME_PERMISSIONS`).
  Permissions must be tapped through on the device; can't be scripted.
- **Wireless ADB ports change** whenever the toggle is touched, and the pairing
  port differs from the connect port. Pairing codes expire in ~1 minute — have
  the command ready *before* asking the user to open the dialog.
- **`CloseApp` needs Accessibility Service enabled by hand** (Settings →
  Accessibility → PhoneAgent). Android permits no silent self-enrollment. Its
  recents-dismiss gesture logic is a **first pass, never run on-device** — expect
  to tune it against MIUI's actual Recents UI.
- The phone's UI is in **Hebrew**; MIUI labels also drift between versions, so
  give the user positional hints, not just exact label text.
- **Cleartext HTTP is blocked by default.** The manifest sets
  `usesCleartextTraffic="true"` on purpose — the LAN server has no TLS.

## Environment notes

- **RAM is tight (16GB).** Background processes have been OOM-killed here.
  Resident Ollama models are the usual culprit — `ollama stop <model>` and
  `./gradlew.bat --stop` free several GB.
- Logs: the server writes a rotating **UTF-8** file (explicitly, or Windows
  mangles Hebrew into mojibake — there's a regression test). The app logs under
  logcat tag **`PhoneAgent`**.
- Start the server: `.venv/Scripts/python.exe -m uvicorn brain.main:app --host 0.0.0.0 --port 8787 --reload`

## Working agreements with this user

- Lives in `talthegever/self-using-utils` under `ai/phone agent/`. The repo
  hosts unrelated projects too — **keep changes scoped to this folder**, and
  never stage `ai/answerer/chatbots-keys.json` (secrets) or the nested repo
  under `ai/answerer/si_answerer/`. Note the root `.gitignore` has `*.txt`,
  which silently excludes `design.txt` — it's tracked via `git add -f`.
- Routine local commits and pushes are pre-authorized; the standing limit is
  **don't delete anything already on the remote**.
- A `scripts/hooks/pre-push` gate exists (runs both suites, only when a push
  touches this folder). **Not activated** — needs `git config core.hooksPath
  "ai/phone agent/scripts/hooks"`, which is repo-wide, hence the user's call.
- The user prefers being told the honest measured result over an optimistic
  one — several decisions above exist *because* a hoped-for win was measured
  and didn't materialize. Say so plainly when that happens.
