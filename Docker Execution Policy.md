# Docker Execution Policy

## Core Rule

The host machine may be used for file inspection, searching, source editing, and Git inspection.

**Do not directly execute project code, tests, builds, scripts, binaries, package tools, or development commands on the host.**

All such execution MUST use the repository's:

`.agent/run.sh`

The only approved host-side execution gateway for project commands is:

`bash .agent/run.sh <command> [args...]`

The script must execute the requested command using a disposable:

`docker run --rm`

container.

---

## Commands Allowed Directly on the Host

Pure inspection commands are allowed, including:

* `pwd`
* `ls`
* `cat`
* `head`
* `tail`
* `grep`
* `rg`
* `wc`
* `sed -n`
* `find` only when not using `-exec`, `-execdir`, `-delete`, or other execution/mutation options
* `git status`
* `git diff`
* `git log`
* `git show`
* `git branch`
* `git ls-files`

Agent-native read/search tools are also allowed.

Editing and creating source/configuration files is allowed.

Creating or updating `.agent/run.sh` is allowed.

---

## Commands That MUST Run in Docker

Any command that may execute code, load project code, compile code, install dependencies, start a program, or run project tooling MUST be executed through:

`bash .agent/run.sh ...`

This includes, but is not limited to:

* Python execution
* pytest
* tox
* uv
* Poetry commands that execute/install code
* Node.js
* npm
* npx
* pnpm
* yarn
* Go build/test/run
* Java
* javac
* Maven
* Maven Wrapper
* Gradle
* Gradle Wrapper
* dotnet
* Cargo
* rustc
* make
* cmake
* shell scripts
* project binaries
* migrations
* code generators
* linters
* formatters
* development servers
* unit tests
* integration tests
* build commands

Examples:

Instead of:

`pytest`

use:

`bash .agent/run.sh pytest`

Instead of:

`python scripts/check.py`

use:

`bash .agent/run.sh python scripts/check.py`

Instead of:

`go test ./...`

use:

`bash .agent/run.sh go test ./...`

Instead of:

`./mvnw test`

use:

`bash .agent/run.sh ./mvnw test`

Instead of:

`dotnet test`

use:

`bash .agent/run.sh dotnet test`

Instead of:

`cargo test`

use:

`bash .agent/run.sh cargo test`

For compound commands, execute the shell inside Docker:

`bash .agent/run.sh sh -lc 'command1 && command2'`

Do not execute the compound shell command directly on the host.

---

# New Project Bootstrap Rule

Whenever working in a repository for the first time, check whether:

`.agent/run.sh`

exists.

If it does not exist:

1. Inspect the repository using read-only operations only.
2. Determine the primary runtime and required runtime version.
3. Create `.agent/run.sh`.
4. Do not execute project code before `.agent/run.sh` has been created.
5. After creation, use it for every project execution command.

The generated script must follow this basic structure:

```bash
#!/usr/bin/env bash
set -euo pipefail

IMAGE="<selected-image>"

PROJECT_ROOT="$(
  cd "$(dirname "${BASH_SOURCE[0]}")/.." &&
  pwd
)"

exec docker run \
  --rm \
  -i \
  --init \
  -v "${PROJECT_ROOT}:/workspace" \
  -w /workspace \
  "${IMAGE}" \
  "$@"
```

Do not create a Dockerfile unless the project actually requires one.

Do not create a complex sandbox system.

The normal execution model is simply:

Host → `.agent/run.sh` → `docker run --rm` → command.

---

# Runtime Image Selection

Always determine the runtime version from the repository before choosing an image.

## Python

Inspect, in order where applicable:

* `.python-version`
* `pyproject.toml`
* `Pipfile`
* runtime documentation

Use:

`python:<major.minor>-slim-bookworm`

Example:

`python:3.12-slim-bookworm`

---

## Go

Read the version from:

`go.mod`

Use:

`golang:<major.minor>-bookworm`

Example:

`golang:1.24-bookworm`

---

## Java

Determine the required Java version from:

* `pom.xml`
* `build.gradle`
* `build.gradle.kts`
* Maven toolchains
* Gradle toolchains
* project documentation

If `mvnw` or `gradlew` exists, prefer the project wrapper and use:

`eclipse-temurin:<java-version>-jdk`

Example:

`eclipse-temurin:21-jdk`

Then execute:

`bash .agent/run.sh ./mvnw test`

or:

`bash .agent/run.sh ./gradlew test`

If the project does not contain a build-tool wrapper, an appropriate Maven or Gradle build image may be used instead.

---

## .NET

Inspect:

* `global.json`
* `*.csproj`
* `*.fsproj`
* `TargetFramework`
* project documentation

Use:

`mcr.microsoft.com/dotnet/sdk:<major.minor>`

Example:

`mcr.microsoft.com/dotnet/sdk:10.0`

---

## Rust

Inspect:

* `rust-toolchain.toml`
* `rust-toolchain`
* project documentation

Use:

`rust:<version>-bookworm`

Example:

`rust:1.85-bookworm`

If no Rust version is pinned, use the stable Rust image family rather than nightly.

---

## Node.js

Inspect:

* `.nvmrc`
* `.node-version`
* `package.json` `engines.node`
* project documentation

Use:

`node:<major>-bookworm-slim`

Example:

`node:22-bookworm-slim`

---

# Image Selection Rules

Priority:

1. Explicit runtime version declared by the repository.
2. Runtime version documented by the project.
3. Stable/LTS runtime when the repository specifies no version.

Do not arbitrarily upgrade the project's runtime.

Do not use prerelease, beta, RC, nightly, or development images unless the project explicitly requires them.

Prefer standard Debian-based official runtime images.

Do not default to Alpine unless the project explicitly requires Alpine or musl compatibility.

---

# Existing `.agent/run.sh`

If `.agent/run.sh` already exists:

1. Read it first.
2. Reuse it when it satisfies this policy.
3. Do not unnecessarily regenerate it.
4. Update it only if the project's runtime requirements have changed or the script is incorrect.

---

# Failure Rule

If Docker is unavailable or `.agent/run.sh` cannot execute:

**Stop execution and report the problem.**

Do not fall back to running project commands directly on the host.
