# Use Case 3: Self-Healing DevOps Infrastructure

System failures, Docker crashes, and pipeline bottlenecks happen at 3:00 AM. Relying on humans to read logs, SSH into servers, and reboot services costs enterprises millions in downtime. 

OpenJudge acts as an advanced, continuous **Site Reliability Engineer (SRE)**.

## The Problem with Vanilla LLMs
If you paste a 500-line Nginx error log into ChatGPT, it will correctly identify the misconfigured port mapping. But then, as a human, you still have to manually log in, stop the service, edit the `nginx.conf` file, and restart the daemon.

## The OpenJudge Solution
OpenJudge closes the loop. It doesn't just diagnose the problem; it physically deploys the fix, restarts the service, and verifies the resolution autonomously.

When bound to a secure orchestration layer (or running directly on a VM), OpenJudge operates via the `execute_bash` and `read_file` tools.

1. **Trigger:** A monitoring webhook (e.g., Datadog) pings the OpenJudge FastAPI endpoint indicating a `502 Bad Gateway` error on `api.internal.svc`.
2. **Investigation:** OpenJudge executes `tail -n 50 /var/log/nginx/error.log`.
3. **The Pivot:** It realizes the upstream container is dead. It attempts to restart it via `docker restart core-backend`.
4. **Verification:** The Engine empirically runs `curl -I http://localhost:8080/health`. If it receives a `200 OK`, the incident is resolved.
5. **Reporting:** It yields the final JSON payload documenting the exact sequence of Bash steps it took to heal the system.

## Implementation Example (Bash Telemetry)

```bash
# Incident Triggered: Investigating Disk Space
[TOOL_TRIGGERED] executing action `execute_bash` with payload {"command": "df -h"}
[THOUGHT_PROCESS] The /dev/nvme0n1 partition is at 99% capacity. I need to locate large temporary log files.
[TOOL_TRIGGERED] executing action `execute_bash` with payload {"command": "find /var/log -type f -size +1G"}
# ... (Discovered massive rotated logs)
[TOOL_TRIGGERED] executing action `execute_bash` with payload {"command": "rm -f /var/log/app.log.1"}
[ENGINE_HALT] Disk space successfully reclaimed. Current capacity is 82%.
```

## Business Value
- **Zero-Downtime Resilience:** Instantly diagnose and fix critical infrastructure errors in seconds without waking up human engineers.
- **Auditable Security:** The entire chain of execution is logged in the `state_manager`'s cryptographic Ledger, ensuring you know exactly *why* and *how* a server was modified.
