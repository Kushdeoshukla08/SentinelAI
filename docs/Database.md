# SentinelAI Database Design

## Version

v1.0

---

# Database Overview

SentinelAI uses PostgreSQL as its primary database.

The database is responsible for storing:

* Users
* Security Logs
* Alerts
* Incidents
* Reports
* Investigations
* Chat History

---

# Entity Relationship Overview

Users

↓

Alerts

↓

Incidents

↓

Reports

Logs

↓

Alerts

↓

Investigations

---

# Users Table

Table Name:

users

Purpose:

Store user accounts and authentication information.

Fields:

id (UUID, Primary Key)

name (VARCHAR)

email (VARCHAR, Unique)

password_hash (TEXT)

role (ENUM)

created_at (TIMESTAMP)

updated_at (TIMESTAMP)

---

Roles

* analyst
* manager
* administrator

---

# Logs Table

Table Name:

logs

Purpose:

Store normalized security logs.

Fields:

id (UUID, Primary Key)

timestamp (TIMESTAMP)

source_ip (VARCHAR)

destination_ip (VARCHAR)

username (VARCHAR)

event_type (VARCHAR)

event_source (VARCHAR)

severity (VARCHAR)

raw_log (TEXT)

created_at (TIMESTAMP)

---

# Alerts Table

Table Name:

alerts

Purpose:

Store generated security alerts.

Fields:

id (UUID, Primary Key)

title (VARCHAR)

description (TEXT)

severity (VARCHAR)

confidence_score (FLOAT)

status (VARCHAR)

alert_type (VARCHAR)

created_at (TIMESTAMP)

updated_at (TIMESTAMP)

---

Alert Status

* open
* investigating
* resolved
* closed

---

# Alert Logs Mapping

Table Name:

alert_logs

Purpose:

Many-to-many relationship between alerts and logs.

Fields:

id (UUID)

alert_id (UUID)

log_id (UUID)

---

# Incidents Table

Table Name:

incidents

Purpose:

Store confirmed security incidents.

Fields:

id (UUID)

alert_id (UUID)

title (VARCHAR)

description (TEXT)

incident_status (VARCHAR)

created_at (TIMESTAMP)

resolved_at (TIMESTAMP)

---

Incident Status

* open
* active
* resolved

---

# Reports Table

Table Name:

reports

Purpose:

Store AI-generated incident reports.

Fields:

id (UUID)

incident_id (UUID)

executive_summary (TEXT)

technical_summary (TEXT)

recommendations (TEXT)

generated_at (TIMESTAMP)

---

# Investigations Table

Table Name:

investigations

Purpose:

Store AI investigation results.

Fields:

id (UUID)

alert_id (UUID)

root_cause (TEXT)

timeline (JSON)

recommendations (TEXT)

confidence_score (FLOAT)

created_at (TIMESTAMP)

---

# Chat History Table

Table Name:

chat_history

Purpose:

Store Security Copilot conversations.

Fields:

id (UUID)

user_id (UUID)

question (TEXT)

answer (TEXT)

created_at (TIMESTAMP)

---

# Threat Intelligence Table

Table Name:

threat_intelligence

Purpose:

Store malicious indicators.

Fields:

id (UUID)

indicator_type (VARCHAR)

indicator_value (VARCHAR)

threat_level (VARCHAR)

source (VARCHAR)

created_at (TIMESTAMP)

---

# Future Tables

Version 2

user_behavior_profiles

risk_scores

mitre_mappings

---

Version 3

agent_actions

threat_hunting_sessions

attack_graphs

---

# Database Design Principles

* UUID-based primary keys
* Auditability
* Scalability
* Data normalization
* Easy integration with AI services

---

# Database Choice

Primary Database:

PostgreSQL

Reason:

* ACID Compliance
* Strong Query Support
* Scalability
* Enterprise Adoption
