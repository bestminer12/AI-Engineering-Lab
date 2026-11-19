# Security Engineering Portfolio

**AI Security · Cloud Security · Detection & Incident Response**

**5 Projects | 2 AI Security Projects · 3 Cloud & Container Security Projects**

### 01. GenAI Security Assessment Lab

**LLM Security Assessment and Defense Validation for RAG-Based Applications**

- **Implementation:** Reproduced Prompt Injection and RAG Data Poisoning attacks; implemented API authentication and authorization, document trust validation, retrieval relevance filtering, and security event detection.
- **Results:** Improved defenses against unauthorized access and response manipulation; successfully passed 25 automated security tests.
- **Technologies:** Python · FastAPI · Ollama · ChromaDB · pytest

### 02. Agentic AI SOC Investigation & Alert Automation

**AI Agent-Based Security Investigation and Incident Response Automation**

- **Implementation:** Developed a LangGraph-based investigation agent integrating OpenSearch log correlation, event timeline reconstruction, evidence-verified reporting, deterministic severity classification, and Slack alert automation with duplicate suppression.
- **Results:** Reduced investigation execution time from 600 seconds (manual) to 57.10 seconds (Agent-assisted pipeline). Validated CRITICAL severity classification, tool access restrictions, prompt injection safeguards, and sensitive-data masking.
- **Technologies:** Python · LangGraph · Ollama · OpenSearch · SQLite · Slack

### 03. AWS Access Key Exposure Detection & Incident Response

**AWS Credential Misuse Detection and Incident Response Automation**

- **Implementation:** Implemented CloudTrail-based detection of IAM access key creation events and automated Discord security notifications.
- **Technologies:** AWS CloudTrail · EventBridge · Lambda · IAM

### 04. AWS Security Group Public Exposure Detection & Response

**Automated Detection and Response for Publicly Exposed SSH Access**

- **Implementation:** Developed automated detection of Security Group rules exposing SSH (`0.0.0.0/0:22`), with real-time alerting and response workflows.
- **Technologies:** Terraform · GitHub Actions · CloudTrail · EventBridge · Lambda

### 05. Kubernetes Security Detection & Incident Response

**Container and Kubernetes Security Policy Validation**

- **Implementation:** Validated RBAC least-privilege access, NetworkPolicy isolation, and Pod Security Admission controls; integrated vulnerable container image blocking into CI pipelines.
- **Technologies:** Kubernetes · RBAC · NetworkPolicy · Trivy · GitHub Actions

---

**Core Competencies:** AI Security Assessment · Agentic AI SOC · Security Automation · Threat Detection · Incident Response · DevSecOps

*Detailed architecture diagrams, implementation procedures, and validation evidence are provided in the individual project reports.*

*Performance results are based on a single controlled scenario. Manual and Agent-assisted investigations involved different execution scopes.*