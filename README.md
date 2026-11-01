In enterprise ERP environments like **SAP S/4HANA**, managing user authorizations is critical for preventing financial fraud, data leaks, and compliance failures. A core security challenge in these systems is maintaining **Segregation of Duties (SoD)** ensuring that no single user holds conflicting permissions, such as the ability to both create a vendor and approve payments to that vendor.
This project is a **Security Data Science prototype** written in Python that automates the auditing of SAP authorization structures. By synthesizing relational SAP security tables (`AGR_USERS` and `AGR_TCODES`), the engine evaluates user-role mappings against a predefined SoD risk matrix. Beyond static rule-based checks, it applies **Unsupervised Machine Learning (Isolation Forest)** to detect over-privileged accounts and anomalous access patterns across the organization.

# Key Features & Objectives
- **Synthetic SAP Data Engine:** Generates realistic relational structures mimicking SAP authorization tables.
- **SoD Matrix Audit:** Joins and evaluates user-role-transaction mappings against a predefined risk matrix using `pandas`.
- **Anomaly Detection:** Uses `scikit-learn` (Isolation Forest) to isolate outlier user profiles with excessive access.
- **Audit Reporting:** Exporting structured conflict logs and summary metrics for GRC/Cyber Risk teams.
