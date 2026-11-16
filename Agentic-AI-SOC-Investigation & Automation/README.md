# Agentic AI SOC Investigation & Alert Automation Lab

**An Agentic AI-based security investigation and alert automation project for SOC environments.**

## 1. Project Overview

This project aims to design, implement, and evaluate an AI agent capable of performing multi-step security investigations using structured security logs.

Traditional SOC investigations often require analysts to execute multiple searches, correlate related events, reconstruct attack timelines, and assess potential security incidents.

This project explores whether an Agentic AI approach can improve investigation efficiency by coordinating these activities through controlled, read-only tools.

The system is designed to support security analysts rather than replace human judgment.

**Project Status:** Planning / Development Preparation

## 2. Project Objectives

- Implement an Agentic AI workflow for multi-step security investigations.
- Integrate OpenSearch for security log retrieval and correlation.
- Generate structured investigation reports supported by log evidence.
- Apply deterministic severity classification using server-side rules.
- Deliver validated HIGH and CRITICAL alerts through Slack.
- Implement security controls to restrict agent behavior and tool execution.
- Evaluate investigation accuracy, processing time, and operational efficiency against conventional approaches.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.11 |
| Development Environment | Windows 11 |
| API Framework | FastAPI |
| Agent Orchestration | LangGraph |
| Local LLM Runtime | Ollama |
| LLM Model | To be determined |
| Search Engine | OpenSearch |
| Log Format | ECS-like JSON |
| Data Validation | Pydantic |
| State Management | SQLite |
| Alert Delivery | Slack Incoming Webhook |
| Automated Testing | pytest |
| Infrastructure | Docker Compose |
| Version Control | Git / GitHub |

## 4. System Architecture

```text
[Security Analyst]
        |
        | Natural Language Investigation Request
        v
[FastAPI]
        |
        v
[LangGraph Investigation Agent]
        |
        +-- Tool Selection
        +-- Investigation Planning
        +-- Multi-Step Correlation
        |
        v
[Approved Read-Only Tools]
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
[Security Log Evidence]
        |
        v
[Investigation Report]
        |
        +-- Evidence Validation
        +-- Event Timeline
        +-- Investigation Findings
        |
        v
[Deterministic Severity Engine]
        |
        +-- LOW
        +-- MEDIUM
        +-- HIGH
        +-- CRITICAL
        |
        +-- LOW / MEDIUM --> Report Only
        |
        +-- HIGH / CRITICAL
                    |
                    v
             [Alert Validation]
                    |
                    v
              [Slack Webhook]
                    |
                    v
             [Security Analyst]
```

The LLM is responsible for investigation planning and tool orchestration.

Security-sensitive decisions, including severity classification and alert delivery, are controlled by server-side logic.

## 5. Core Investigation Capabilities

### 5.1 Security Log Search

Retrieve relevant security events from OpenSearch using approved read-only tools.

### 5.2 Authentication Failure Analysis

Identify repeated authentication failures and aggregate events by relevant attributes.

### 5.3 Event Correlation

Correlate related authentication events, including failure-to-success patterns and suspicious activity involving multiple IP addresses.

### 5.4 Attack Timeline Reconstruction

Organize correlated security events into a chronological timeline.

### 5.5 Evidence-Based Investigation Reports

Generate structured investigation reports containing findings, supporting log evidence, and event timelines.

### 5.6 Deterministic Severity Classification

Classify investigation results using predefined server-side rules.

Supported severity levels:

- LOW
- MEDIUM
- HIGH
- CRITICAL

The LLM does not independently determine the final severity level.

### 5.7 Slack Alert Automation

Deliver validated HIGH and CRITICAL alerts to Slack.

Alert delivery is controlled by server-side validation, deduplication, and delivery-state management.

## 6. Security Design

Security controls are an essential part of the project.

### 6.1 Read-Only Tool Access

The agent can access only explicitly approved investigation tools.

Direct modification of security logs and unrestricted command execution are outside the permitted workflow.

### 6.2 Query Restrictions

OpenSearch operations are subject to restrictions on:

- Allowed indices
- Query time ranges
- Searchable fields
- Result counts
- Tool invocation limits
- Execution timeouts

### 6.3 Prompt Injection Defense

The project includes test scenarios involving malicious instructions embedded in investigation inputs and retrieved data.

Agent behavior must remain within predefined tool and workflow boundaries.

### 6.4 Evidence Validation

Investigation findings must be supported by identifiable security log evidence.

### 6.5 Sensitive Data Protection

Report and alert outputs are subject to field allowlisting and sensitive-data masking.

### 6.6 Alert Delivery Protection

The LLM cannot directly invoke Slack webhooks.

Alert delivery is handled by server-side logic with validation, deduplication, and retry handling.

### 6.7 Audit Logging

Agent actions, tool execution, investigation results, and alert delivery events are recorded for traceability.

## 7. Planned Security Investigation Scenarios

The evaluation will include the following scenarios:

| Scenario | Description |
|---|---|
| Repeated Authentication Failures | Detect and investigate repeated failed login attempts |
| Failure-to-Success Correlation | Identify successful authentication following repeated failures |
| Multi-IP Activity | Correlate suspicious authentication events across multiple source IPs |
| Privilege Escalation | Investigate suspicious privilege-related events |
| Alert Delivery | Validate HIGH / CRITICAL Slack notifications |
| Delivery Failure | Verify handling of Slack delivery failures |
| Prompt Injection | Evaluate resistance to malicious instructions |
| Unauthorized Tool Access | Verify rejection of unapproved tool execution |
| Sensitive Data Leakage | Verify output filtering and masking |
| Agent Loop | Verify execution limits and termination behavior |
| Alert Flooding | Verify deduplication and alert delivery controls |

All security logs used in this project will be synthetic.

## 8. Evaluation Methodology

A primary objective of this project is to evaluate whether Agentic AI provides measurable benefits over conventional security investigation approaches.

The same security log datasets and investigation scenarios will be used for comparison.

### 8.1 Investigation Approaches

| Approach | Description |
|---|---|
| Baseline A | Manual security investigation |
| Baseline B | Single-step natural-language-to-query investigation |
| Proposed | Agentic AI-based multi-step investigation |
| Extended | Agentic investigation with automated Slack alerting |

### 8.2 Evaluation Metrics

- Investigation time
- Investigation accuracy
- Evidence identification accuracy
- Tool invocation count
- Search query execution count
- False positives and false negatives
- Alert precision and recall
- Alert delivery latency

### 8.3 Evaluation Principles

- Use consistent datasets and scenarios across approaches.
- Repeat measurements where applicable.
- Validate investigation findings against predefined expected results.
- Analyze both successful and unsuccessful investigation outcomes.
- Report measured results without assuming performance improvements in advance.

The project does not assume that an AI agent will outperform conventional approaches in every scenario.

Simple investigations may be more efficiently handled by traditional searches or deterministic automation.

The evaluation will identify the conditions under which multi-step agentic investigation provides practical benefits.

## 9. Development Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Infrastructure and development environment setup | Planned |
| Phase 2 | OpenSearch integration and investigation tools | Planned |
| Phase 3 | LangGraph agent workflow | Planned |
| Phase 4 | Evidence-based investigation reporting | Planned |
| Phase 5 | Deterministic severity classification and Slack integration | Planned |
| Phase 6 | Agent security controls and adversarial testing | Planned |
| Phase 7 | Quantitative evaluation and baseline comparison | Planned |
| Phase 8 | Documentation and GitHub portfolio finalization | Planned |

## 10. Expected Deliverables

The project aims to produce:

1. A functional Agentic AI security investigation workflow.
2. A synthetic security log dataset and reproducible investigation scenarios.
3. Approved OpenSearch investigation tools.
4. Evidence-based investigation reports.
5. Deterministic severity classification and Slack alert delivery.
6. Automated functional and security tests.
7. Quantitative comparisons with conventional investigation methods.
8. A final technical assessment report documenting results and limitations.

## 11. Project Scope and Limitations

This project is a laboratory implementation intended for security engineering research and portfolio demonstration.

It is not a production SOC platform.

The project uses synthetic security logs and controlled investigation scenarios.

Investigation accuracy, performance improvements, and operational suitability will be assessed after implementation and testing.

No performance or security guarantees are claimed before validation.

## 12. Conclusion

The Agentic AI SOC Investigation & Alert Automation Lab explores the practical application of AI agents to security investigation workflows.

Its primary goal is not simply to demonstrate an AI agent, but to evaluate whether controlled, multi-step agentic investigation can provide measurable value in SOC operations.

The final assessment will consider investigation accuracy, efficiency, evidence quality, security controls, and operational limitations.

**The project will prioritize measurable engineering outcomes over feature expansion.**

---

**Project Status: Planned — Implementation and evaluation pending.**
