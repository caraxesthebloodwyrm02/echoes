# C# runner (language-bundle)

This folder is intended to hold the small C# runner used in end-to-end runs. The original project expects:
- `csharp/Program.cs` — a small program that probes `http://127.0.0.1:8000/transform` and optionally checks for Java under `bin/java.exe`.
- `language-bundle.csproj` — the project file for building/running the runner.

If you add or restore the runner, keep these semantics:
- Exit code `2` for Java-not-found, `1` for Java execution failure (preserve existing semantics if you reintroduce a runner)
- Tests: add a fake `bin/java.exe` in CI to validate the runner's Java probe behavior.

Build & run (example):
```powershell
cd csharp
dotnet build
dotnet run --project .
```
