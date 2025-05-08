# ADR-004: Sandboxing Strategy for Executing Student Code

**Date:** 2025-05-08  
**Status:** Accepted

---

## Context

The *CellSensei* project must safely execute a fixed set of student-defined functions extracted from Jupyter notebooks. This requires executing **untrusted code** — raising serious concerns about security, resource abuse, and system integrity.

Full container-based isolation (e.g., Docker per submission) is ideal in theory, but:
- The host system is underpowered
- Docker introduces high runtime overhead
- Privilege requirements (root or Docker group access) add operational risk
- The project is self-funded, so cloud-based scaling is not feasible

The sandboxing strategy must be:
- Secure “enough” for controlled educational use
- Lightweight and performant
- Easy to set up and run on modest Linux systems

---

## Decision

The project will use **Firejail** to sandbox the execution environment, combined with a per-submission **Python virtual environment (venv)**.

This combination provides:
- Namespaced isolation using Linux kernel features
- Lightweight filesystem and network restrictions
- Minimal dependencies (Firejail is a single-user-space tool)
- No requirement for root or container infrastructure

---

## Alternatives Considered

### 1. **No Sandbox (direct exec)** ❌
- Pros: Simplest possible implementation
- Cons: Dangerous — untrusted code could read/delete files, overuse CPU/RAM, or attack the host

### 2. **Docker per submission**
- Pros: Strongest isolation guarantees (filesystem, process, network)
- Cons:
  - High resource cost (slow startup, large image base)
  - Requires root or docker group access
  - Complex orchestration for per-task containers

### 3. **chroot + venv**
- Pros: File system isolation using known Unix primitives
- Cons:
  - Requires root setup
  - Harder to maintain or replicate across distros
  - Doesn’t protect against syscalls or CPU abuse

### 4. **Jupyter Kernel Gateway / nbclient execution**
- Pros: More native to the notebook ecosystem
- Cons:
  - Still needs sandboxing of the kernel or subprocess
  - Adds Jupyter orchestration overhead for minimal gain

### 5. **Firejail + venv (Chosen)**
- Pros:
  - Lightweight, CLI-based, and supports app sandboxing with minimal setup
  - Uses Linux namespaces, seccomp-bpf, and capability dropping
  - Allows control over:
    - Network access
    - Filesystem (read-only, whitelists, temp overlays)
    - CPU/memory usage (indirectly, via ulimits)
  - Easy to deploy: available in most package managers
- Cons:
  - Slight learning curve for profile setup
  - Not as well-known in backend web development workflows (but widely used in Linux desktops)

---

## Justification

### 1. Security Coverage
Firejail blocks many classes of attacks:
- Prevents student code from accessing system files or arbitrary paths
- Can disable network access completely (for offline testing)
- Limits syscalls (e.g., process forking, device access) using seccomp
- Enforces namespace isolation for PID and mount tables

### 2. No Need for Root
Unlike chroot or Docker, Firejail can be run by unprivileged users and still provide effective isolation using SUID techniques and the kernel's built-in features.

### 3. Low Overhead
Firejail launches quickly — suitable even under high submission load. Combining it with `venv` means every execution happens in:
- A clean Python environment
- A restricted Linux namespace

This provides a clean separation of student dependencies and prevents unwanted side effects.

### 4. Flexibility and Portability
- Profiles can be customized to restrict or allow specific paths or commands.
- Sandbox rules can evolve without major changes to the pipeline.
- Works on most Linux distributions out of the box.

---

## Consequences

- All student code execution must be routed through a Firejail sandbox runner script
- Developers must maintain a reusable test harness that:
  - Extracts the 5 student functions
  - Writes them to a temporary `.py` file inside a sandbox directory
  - Launches a Firejailed Python subprocess using that file and a test runner
- The backend (Celery worker) must ensure:
  - Temporary files are cleaned up
  - Execution timeouts and logging are enforced
- Firejail must be installed and verified on all deployment environments

---

## Future Considerations

If performance or attack surface becomes a larger concern:
- **Docker** or **Podman** could be reintroduced once root access or a stronger host is available
- Firejail profiles can be tightened further (e.g., using `--seccomp`, `--caps`, `--net=none`)
- Additional tools like `ulimit` or `systemd-run` could be layered for finer resource control

---

## Summary

The *CellSensei* grading backend will use **Firejail + venv** to execute extracted student functions securely and efficiently. This approach provides solid protection with minimal complexity — balancing performance, cost, and operational simplicity while covering 80–90% of the sandboxing concerns in a typical academic environment.

