# SentinelAI User Flows

## Version

v1.0

---

# Overview

This document defines how users interact with SentinelAI from login to threat investigation and report generation.

---

# User Types

1. Security Analyst
2. SOC Manager
3. System Administrator

---

# Flow 1: User Login

Purpose:

Allow authenticated access to SentinelAI.

Flow:

User

↓

Enter Email

↓

Enter Password

↓

Authentication

↓

Dashboard

---

# Flow 2: Log Upload and Analysis

Purpose:

Analyze uploaded security logs.

Flow:

Login

↓

Upload CSV/JSON Logs

↓

Log Validation

↓

Log Normalization

↓

Threat Detection Engine

↓

Alerts Generated

↓

Dashboard Updated

---

# Flow 3: Alert Investigation

Purpose:

Investigate suspicious security activity.

Flow:

Dashboard

↓

Select Alert

↓

View Alert Details

↓

AI Investigation

↓

Threat Explanation

↓

Timeline Reconstruction

↓

Recommended Actions

---

# Flow 4: Security Copilot Investigation

Purpose:

Natural language threat investigation.

Flow:

Open Security Copilot

↓

Ask Question

↓

AI Processes Context

↓

Retrieve Relevant Data

↓

Generate Response

↓

Display Findings

Example Questions:

Why was this user flagged?

Show suspicious logins in the last 24 hours.

Explain this alert.

---

# Flow 5: Incident Creation

Purpose:

Convert alerts into incidents.

Flow:

Alert

↓

Create Incident

↓

Assign Severity

↓

Start Investigation

↓

Track Resolution

---

# Flow 6: Report Generation

Purpose:

Generate incident reports.

Flow:

Incident

↓

AI Analysis

↓

Executive Summary

↓

Technical Summary

↓

Recommendations

↓

Export PDF

---

# Flow 7: Alert Resolution

Purpose:

Close investigated incidents.

Flow:

Open Alert

↓

Review Findings

↓

Apply Remediation

↓

Mark Resolved

↓

Archive

---

# Flow 8: Threat Intelligence Lookup

Purpose:

Check suspicious indicators.

Flow:

Indicator

↓

Threat Intelligence Search

↓

Match Found

↓

Risk Evaluation

↓

Investigation Recommendation

---

# Future Flow: Autonomous Investigation

Version 3

Alert Generated

↓

Investigation Agent

↓

Evidence Collection Agent

↓

MITRE Mapping Agent

↓

Report Agent

↓

Response Recommendation Agent

↓

Analyst Review

---

# Key User Journey

Most Common Path

Login

↓

Upload Logs

↓

Threat Detection

↓

Alert Generated

↓

AI Investigation

↓

Threat Explanation

↓

Report Generation

↓

Resolution

---

# Success Criteria

A security analyst should be able to:

* Upload logs
* Detect threats
* Understand alerts
* Investigate incidents
* Generate reports

without requiring deep knowledge of SQL queries or manual log analysis.
