# Cybersecurity Internship Projects - Future Interns

This repository showcases a collection of projects completed during a cybersecurity internship with **Future Interns**. The tasks demonstrate practical skills across offensive security (Web Application Penetration Testing), defensive security (SOC Analysis & Incident Response), and secure software development.

---

## Task 1: Web Application Security Testing

### 🛡️ Project Objective
The primary goal of this task was to conduct a comprehensive web application vulnerability assessment of the **OWASP Juice Shop** application. The exercise simulated a real-world penetration test, leveraging a combination of automated and manual testing techniques to identify and analyze security flaws.

### 🔧 Tools & Technologies Used
* **OWASP ZAP**: Dynamic Application Security Testing (DAST) scanner for initial vulnerability discovery.
* **Nikto**: Web server scanner used to identify server misconfigurations and outdated software.
* **SQLMap**: Automated tool for detecting and exploiting SQL injection vulnerabilities.
* **Burp Suite (Community Edition)**: Intercepting proxy for manual inspection, modification, and replay of web requests.
* **Kali Linux**: The primary operating system for hosting all testing tools.

### 🔍 Summary of Findings
The assessment identified several critical and high-risk vulnerabilities, which are detailed below:

| Vulnerability | OWASP Top 10 Mapping | Risk Level |
| :--- | :--- | :--- |
| SQL Injection | A01: Broken Access Control | High |
| Cross-Site Scripting (XSS) | A03: Injection | Medium |
| Broken Authentication | A07: Identification & Auth Failures | High |
| Sensitive Data Exposure | A02: Cryptographic Failures | Medium |
| Broken Access Control | A01: Broken Access Control | High |

---

## Task 2: SOC Alert Monitoring & Incident Response Simulation

### 🛡️ Project Objective
This task simulated the duties of a Security Operations Center (SOC) Analyst. The core objective was to utilize a Security Information and Event Management (SIEM) system to monitor, detect, analyze, and report on malicious activity within a controlled environment.

### 🧰 Environment & Tools
* **SIEM**: Elastic Stack (ELK - Elasticsearch, Logstash, Kibana) deployed on Kali Purple.
* **Operating System**: Kali Purple Linux.
* **Query Language**: Kibana Query Language (KQL) for log analysis and threat hunting.
* **Log Sources**: A collection of sample system logs, authentication logs, malware alerts, and network traffic data.

### 🧪 MITRE ATT&CK® Tactics Identified
During the investigation, attacker behaviors were mapped to the MITRE ATT&CK® framework, revealing the following tactics:

* **Execution**: The attacker used PowerShell and Batch files to run malicious commands.
* **Persistence**: Persistence was achieved by creating a new admin account, scheduling tasks, and modifying registry autorun keys.
* **Privilege Escalation**: The attacker exploited MSI files and abused the "AlwaysInstallElevated" policy to gain SYSTEM-level privileges.
* **Defense Evasion**: The attacker utilized system binaries (LOLBins) to mask their activities.
* **Discovery**: The attacker performed system enumeration and network probing to understand the environment.

---

## Task 3: Secure File Sharing System

### 🧾 Project Overview
This project involved the development of a secure file upload and download web portal. The application was built to ensure the confidentiality of data both at rest and in transit by implementing strong, password-based AES encryption.

### 🔐 Core Features
* **End-to-End Encryption**: Files are encrypted with AES-256 before being stored and can only be decrypted with the correct user-provided password.
* **Secure Transport**: The application is served over HTTPS using self-signed SSL certificates to protect data in transit.
* **Zero Plaintext Storage**: No files or passwords are ever stored in plaintext on the server.
* **Secure Sharing**: Users can generate a secure link to share the encrypted file, which requires the recipient to enter the password for decryption.

### 🧰 Tech Stack
* **Backend**: Python Flask
* **Cryptography**: PyCryptodome library for AES encryption
* **Frontend**: HTML & CSS
* **Testing**: Postman and cURL for API validation
* **Version Control**: Git & GitHub

### 💻 Local Setup Instructions

To run this project on a local machine, follow these steps:

```bash
# 1. Clone the repository from GitHub
git clone [https://github.com/Magnus7811/FUTURE_CS_03.git](https://github.com/Magnus7811/FUTURE_CS_03.git)
cd FUTURE_CS_03

# 2. Create and activate a Python virtual environment
# For macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# For Windows:
# venv\Scripts\activate

# 3. Install the required dependencies
pip install -r requirements.txt

# 4. Run the Flask application with SSL enabled
python app.py
# cybersecurity_internship
# cybersecurity_internship
