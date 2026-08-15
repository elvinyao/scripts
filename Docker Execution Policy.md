# Docker Execution Policy

IMPORTANT: The host machine is for source inspection and editing, not for executing project code.

## Host

Direct host shell execution is allowed only for pure inspection operations such as:

- reading files
- searching files
- listing directories
- checking file metadata
- read-only Git inspection

Examples include `ls`, `cat`, `grep`, `rg`, `find` for searching, `git status`, `git diff`, `git log`, and `git show`.

Source files may be edited normally using the agent's file editing tools.

Do not use shell redirection or executable commands on the host to perform project work.

## Project execution

Any operation that may execute code, load project code, install dependencies, compile, build, test, lint, format, generate code, start a server, run a script, or invoke a project tool MUST run through:

    bash .agent/run.sh <command> [args...]

Examples:

    bash .agent/run.sh pytest
    bash .agent/run.sh python main.py
    bash .agent/run.sh npm test
    bash .agent/run.sh go test ./...
    bash .agent/run.sh ./mvnw test
    bash .agent/run.sh dotnet test
    bash .agent/run.sh cargo test

For compound commands, put the shell inside Docker:

    bash .agent/run.sh sh -lc 'command1 && command2'

Never run project execution directly on the host.

Never invoke `docker run` directly during normal project work. Use `.agent/run.sh`.

## New repository

When entering a repository, first check whether `.agent/run.sh` exists.

If it exists, read and reuse it.

If it does not exist:

1. Inspect the repository using read-only operations only.
2. Determine the project's runtime and version.
3. Create `.agent/run.sh`.
4. Do not execute project code until the runner exists.
5. After creation, execute all project commands through the runner.

`mkdir -p .agent` is allowed only when needed to create the runner.

Write `.agent/run.sh` using file editing tools rather than shell redirection.

## Docker image selection

Prefer the runtime version explicitly declared by the repository.

Python:
- inspect `.python-version`, `pyproject.toml`, `Pipfile`
- use `python:<major.minor>-bookworm`

Node.js:
- inspect `.nvmrc`, `.node-version`, `package.json` engines
- use `node:<major>-bookworm`

Go:
- inspect `go.mod` `go` and `toolchain`
- use `golang:<major.minor>-bookworm`

Java:
- inspect `pom.xml`, Gradle files, Java toolchains, `.java-version`
- when `mvnw` or `gradlew` exists, prefer the wrapper
- use `eclipse-temurin:<java-major>-jdk`
- if there is no wrapper, an appropriate Maven or Gradle build image may be used

.NET:
- inspect `global.json`, `.csproj`, `.fsproj`, and TargetFramework
- use `mcr.microsoft.com/dotnet/sdk:<major.minor>`

Rust:
- inspect `rust-toolchain.toml`, `rust-toolchain`, and `Cargo.toml` rust-version
- use `rust:<version>-bookworm`

Do not use `latest` when the repository declares a runtime version.

Do not arbitrarily upgrade the project's runtime.

If the repository genuinely requires multiple runtimes, `.agent/run.sh` may select between multiple appropriate images internally, but the external execution interface must remain:

    bash .agent/run.sh ...

## Runner requirements

`.agent/run.sh` must:

- use `docker run --rm`
- mount the project at `/workspace`
- use `/workspace` as the container working directory
- pass the requested command and arguments to the container
- contain no project execution on the host

Use this basic pattern:

    docker run --rm -i --init \
      -v "${PROJECT_ROOT}:/workspace" \
      -w /workspace \
      "${IMAGE}" \
      "$@"

If Docker is unavailable or the runner fails, report the problem.

Never fall back to executing the project command directly on the host.
