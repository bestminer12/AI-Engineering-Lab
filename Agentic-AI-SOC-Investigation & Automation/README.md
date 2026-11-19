# Agentic AI SOC Investigation & Alert Automation

**A security investigation and alert automation lab using LangGraph, Ollama, OpenSearch, and Python.**

## 1. Project Overview

This project implements an Agent-assisted Security Operations Center (SOC) investigation workflow for analyzing suspicious authentication activity.

Traditional SOC investigations require analysts to search logs, correlate events, reconstruct timelines, assess incident severity, and determine whether an alert should be issued.

The project explores how an LLM-based agent can coordinate investigation tools while deterministic Python logic handles evidence verification, severity classification, and notification control.

**The goal is to assist security analysts, not replace human judgment.**

**Project Status:** Core implementation and planned validation completed (Phases 1–7). Portfolio documentation in progress (Phase 8).

## 2. Project Objectives

- Implement multi-step security investigations using LangGraph.
- Retrieve and correlate security events stored in OpenSearch.
- Generate evidence-based investigation reports.
- Separate LLM-generated analysis from verified security findings.
- Classify severity using deterministic Python rules.
- Deliver Slack security alerts with duplicate suppression.
- Apply tool restrictions, prompt-injection safeguards, and sensitive-data masking.
- Compare manual investigation, single-LLM analysis, and Agent-assisted investigation.

## 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming Language | Python 3.11 | Investigation and automation logic |
| Development Environment | Windows / VS Code | Local development |
| Agent Orchestration | LangGraph | Agent workflow and tool execution |
| Local LLM Runtime | Ollama | Local LLM inference |
| LLM Model | Qwen2.5 1.5B | Tool selection and investigation summaries |
| Search Engine | OpenSearch 2.19.4 | Security log storage and retrieval |
| Log Format | JSON | Synthetic security events |
| Severity Engine | Python | Rule-based severity classification |
| State Storage | SQLite | Alert history and duplicate suppression |
| Notifications | Slack Incoming Webhook | Security alert delivery |
| Infrastructure | Docker / Docker Compose | Local OpenSearch environment |
| Version Control | Git / GitHub | Source code management |

The implemented workflow uses Python scripts and a command-line interface. **FastAPI is not part of this project's investigation architecture.**

## 4. System Architecture

```text
[Security Analyst / Investigation Request]
                  |
                  v
       [LangGraph SOC Agent]
                  |
                  +---- [Ollama / Qwen2.5]
                  |        Tool selection
                  |        Investigation summary
                  |
                  v
        [Approved Python Tools]
                  |
                  +-- search_security_logs
                  +-- aggregate_auth_failures
                  +-- correlate_auth_events
                  +-- build_event_timeline
                  |
                  v
             [OpenSearch]
                  |
                  v
          [Security Log Events]
                  |
                  v
       [Evidence Verification]
                  |
                  v
      [Verified Investigation Report]
                  |
                  v
       [Python Severity Engine]
                  |
                  v
       [Incident Identification]
                  |
                  v
       [SQLite Duplicate Check]
                  |
                  v
        [Slack Notification]
                  |
                  v
          [Security Analyst]
```

### Design Principles

**LLM responsibilities**
- Interpret investigation requests.
- Select approved investigation tools.
- Produce natural-language investigation summaries.

**Python responsibilities**
- Retrieve and correlate security events.
- Construct evidence-based reports.
- Apply deterministic severity rules.
- Identify incidents and suppress duplicate alerts.
- Control notification delivery.

The LLM's generated summary is not treated as authoritative evidence. Security-sensitive decisions are handled by deterministic application logic.

The repository also provides a standalone investigation pipeline through `run_investigation.py`.

## 5. Investigation Scenario

The primary scenario uses synthetic authentication and privilege-related events for the account `alice`.

### Test Scenario

- Eight failed authentication attempts.
- One successful authentication following the failures.
- One privilege-change event.

### Verified Investigation Results

| Metric | Result |
|---|---|
| Timeline events | 10 |
| Verified evidence events | 9 |
| Verified investigation findings | 1 |
| Key verified finding | Failure-to-success authentication pattern |
| Final severity | CRITICAL |
| Analyst review required | Yes |

The severity engine identifies the failure-to-success pattern and the privilege-change event as reasons for a CRITICAL assessment.

This severity is assigned by Python rules, not independently by the LLM.

## 6. Core Investigation Capabilities

### 6.1 Security Log Search

`search_security_logs` retrieves security events from OpenSearch using supported filters.

### 6.2 Authentication Failure Aggregation

`aggregate_auth_failures` summarizes failed authentication activity to support investigation of repeated login attempts.

### 6.3 Event Correlation

`correlate_auth_events` analyzes relationships between authentication events, including suspicious failure-to-success sequences.

### 6.4 Event Timeline Reconstruction

`build_event_timeline` organizes relevant events chronologically to help analysts understand the investigation sequence.

### 6.5 Verified Investigation Reporting

The Python investigation pipeline generates structured reports with findings, event timelines, and supporting evidence.

### 6.6 Deterministic Severity Classification

The severity engine uses predefined Python rules rather than relying solely on LLM-generated assessments.

### 6.7 Slack Alert Automation

The notification pipeline uses incident identification, SQLite alert history, duplicate suppression, and sensitive-data filtering.

A repeated investigation of the same incident was verified to skip duplicate notification delivery.

## 7. Agent Security Controls

Security restrictions are applied to reduce the risks of integrating LLMs with investigation tools.

### 7.1 Tool Allowlist

The Agent is restricted to four approved investigation tools:

1. `search_security_logs`
2. `aggregate_auth_failures`
3. `correlate_auth_events`
4. `build_event_timeline`

A test using an unauthorized tool name, `delete_security_logs`, confirmed that the tool was rejected.

### 7.2 Tool Invocation Limit

The Agent has a maximum tool-call count of four.

Testing confirmed that a fifth tool call was blocked.

### 7.3 Prompt Injection Safeguards

Security log content is treated as untrusted investigation data.

A test inserted a malicious instruction attempting to convince the LLM that suspicious authentication activity was normal.

The tested LLM response did not follow that malicious instruction.

This result demonstrates resistance to the tested scenario only. It does not establish comprehensive prompt-injection protection.

### 7.4 Sensitive Data Masking

The project includes filtering for sensitive values such as:

- Passwords
- API keys
- Bearer tokens
- Access tokens

Tests confirmed that these values were replaced with `[REDACTED]`.

### 7.5 Slack Output Protection

A Slack masking test verified that sensitive values were removed from the outgoing alert payload.

### 7.6 Failure Handling

The command-line investigation and Agent entry points include exception handling for execution failures.

Connection-failure tests confirmed concise error reporting and pipeline termination when OpenSearch or Ollama was unavailable.

## 8. Performance Evaluation

Three investigation approaches were evaluated against the project's synthetic authentication scenario.

### 8.1 Measured Investigation Time

| Approach | Execution Time | Relative to Manual |
|---|---:|---:|
| Manual SOC investigation | 600.00 seconds | Baseline |
| Single LLM | 28.50 seconds | Approximately 21.1× faster |
| Agent-assisted pipeline | 57.10 seconds | Approximately 10.5× faster |

**The manual investigation time was measured through an actual manual investigation run, not estimated.**

### 8.2 Single-LLM Results

- Execution time: 28.50 seconds.
- Input tokens: 744.
- Output tokens: 173.
- Total tokens: 917.
- Correctly identified the four evaluated event/pattern criteria.
- Produced a MEDIUM severity assessment.

### 8.3 Agent-Assisted Pipeline Results

- Execution time: 57.10 seconds.
- Used LangGraph and approved investigation tools.
- Produced a verified investigation report.
- Identified 10 timeline events and 9 verified evidence events.
- Assigned CRITICAL severity through deterministic Python rules.
- Included incident identification and Slack duplicate-notification handling.

### 8.4 Interpretation

The single-LLM approach was faster than the Agent-assisted pipeline.

However, the Agent-assisted pipeline covered additional investigation and operational steps, including tool orchestration, evidence verification, deterministic severity assessment, and alert handling.

The difference between MEDIUM and CRITICAL severity demonstrates the importance of separating generative analysis from deterministic security decisions. It does not prove that the Agent's LLM is inherently more accurate.

**Evaluation limitations:**

- Results represent individual measured runs rather than repeated statistical benchmarks.
- The three approaches did not perform identical workloads.
- Execution times depend on local hardware, model inference performance, and workflow scope.
- Broader accuracy, false-positive, and false-negative rates were not established.

## 9. Integration and Reliability Testing

| Test | Result |
|---|---|
| End-to-end Python investigation pipeline | PASS |
| Tool-call limit enforcement | PASS |
| Unauthorized tool rejection | PASS |
| Tested prompt-injection scenario | PASS |
| Sensitive-data masking | PASS |
| Slack payload masking | PASS |
| Duplicate alert suppression | PASS |
| OpenSearch connection-failure handling | PASS |
| Ollama connection-failure handling | PASS |
| Ollama request timeout configuration | Configured; behavior not empirically tested |

### Reliability Notes

- OpenSearch connection failures terminate the CLI investigation pipeline with error messages.
- Ollama connection failures terminate the Agent CLI with error messages.
- A 120-second timeout is configured for the Ollama client, but an actual delayed-response timeout test has not been completed.
- Full Agent recovery after a simulated dependency failure has not been verified.

These tests validate the specified scenarios; they are not a comprehensive production reliability assessment.

## 10. Project Structure

```text
.
├── agent/                    # LangGraph Agent and safety tests
├── alerts/                   # Slack notifications and alert history
├── data/                     # Synthetic security log data
├── security/                 # Sensitive-data filtering
├── severity/                 # Deterministic severity rules
├── tools/                    # OpenSearch investigation tools
├── benchmark_single_llm.py  # Single-LLM benchmark
├── docker-compose.yml       # Local OpenSearch environment
├── requirements.txt         # Python dependencies
├── run_investigation.py     # Standalone investigation pipeline
└── README.md
```

## 11. Running the Project

### Prerequisites

- Python 3.11
- Docker
- Ollama
- Qwen2.5 1.5B model
- Python dependencies listed in `requirements.txt`
- Slack Incoming Webhook for notification testing

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start OpenSearch

```bash
docker compose up -d
```

### Prepare the Local LLM

```bash
ollama pull qwen2.5:1.5b
```

Ensure that Ollama is running and accessible through the configured local endpoint.

### Run the Investigation Pipeline

```bash
python -u run_investigation.py
```

### Run the Agent

```bash
python -u agent/soc_agent.py
```

### Run the Single-LLM Benchmark

```bash
python -u benchmark_single_llm.py
```

**Important:** OpenSearch must contain the required synthetic security events before an investigation is executed. Slack notification tests additionally require a valid webhook configuration.

## 12. Development Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | OpenSearch environment and log ingestion | Completed |
| Phase 2 | Log investigation tools, correlation, and timelines | Completed |
| Phase 3 | Ollama and LangGraph Agent integration | Completed |
| Phase 4 | Severity classification and Slack alert automation | Completed |
| Phase 5 | Agent security controls | Completed |
| Phase 6 | End-to-end integration and benchmark evaluation | Completed |
| Phase 7 | Security, integration, and reliability validation | Completed |
| Phase 8 | Documentation and GitHub portfolio finalization | In Progress |

## 13. Limitations

This project is a controlled laboratory implementation, not a production SOC platform.

Current limitations include:

- Synthetic rather than production security logs.
- A limited number of investigation scenarios.
- Local, CPU-based LLM inference.
- Single-run performance measurements.
- Limited prompt-injection test coverage.
- No comprehensive accuracy or alert precision/recall evaluation.
- No empirically verified delayed-response timeout behavior.
- No demonstrated production-scale concurrency or high availability.

Future work could explore additional attack scenarios, larger datasets, repeated benchmarks, and integration with production-grade LLM services and SIEM environments.

These improvements are outside the scope of the current implementation.

## 14. Conclusion

This project demonstrates a practical approach to combining Agentic AI with deterministic security investigation and alert automation.

The main engineering lesson is that **LLMs are useful for investigation orchestration and summarization, but security decisions should remain grounded in verified evidence and controlled application logic.**

The benchmark also shows that an Agent-assisted workflow is not necessarily faster than a simpler LLM approach. Its potential value lies in coordinating multi-step investigation, verification, and operational controls.

The project prioritizes measurable implementation results, security boundaries, and clearly documented limitations over unnecessary feature expansion.