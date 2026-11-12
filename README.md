![Tests](https://github.com/magdvlena/SAP-Security-SoD-Conflict-Detector/actions/workflows/tests.yml/badge.svg)
# SAP Security SoD Conflict Detector


A small Python project that checks which users have a risky combination of SAP transaction codes (T-codes) and writes the result to an Excel report.

I built it to practise Python, pandas, pytest, Git and GitHub, so it is a learning project, not a production audit tool.

## What is a SoD conflict?

Segregation of Duties (SoD) means that one person should not be able to do two steps of a process that are supposed to be checked by different people. For example, the same user should not be able to create a vendor **and** execute a payment to that vendor.

## How it works

1. `sod_matrix.csv` lists risky pairs of T-codes (`tcode_a` + `tcode_b`) with a risk level.
2. `user_roles.csv` lists which T-codes each user has through which role.
3. `main.py` finds users who have both T-codes of a risky pair and saves the result in `output/sod_analysis_report.xlsx`.

The report has three sheets: `Summary`, `User Authorizations` and `SoD Conflicts Report`.

## Example result

With the sample data in this repo the tool finds 3 conflicts for 3 users:

| user_id | risk_id | risk_level | tcode_a | tcode_b | role_name_a   | role_name_b   |
|---------|---------|------------|---------|---------|---------------|---------------|
| U001    | SOD_01  | CRITICAL   | FK01    | PAY01   | Vendor_Admin  | Payment_Clerk |
| U002    | SOD_02  | HIGH       | FB01    | PAY01   | GL_Accountant | Payment_Clerk |
| U003    | SOD_03  | MEDIUM     | ME21N   | MIRO    | Purchaser     | AP_Clerk      |

User `U004` has only one T-code, so there is no conflict.

## Getting started

You need Python 3.10 or newer.

```bash
git clone https://github.com/magdvlena/SAP-Security-SoD-Conflict-Detector.git
cd SAP-Security-SoD-Conflict-Detector
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The report is saved in the `output/` folder.

## Input files

`sod_matrix.csv`

| column      | meaning                          |
|-------------|----------------------------------|
| risk_id     | ID of the rule, e.g. `SOD_01`    |
| tcode_a     | first T-code of the risky pair   |
| tcode_b     | second T-code of the risky pair  |
| risk_level  | `CRITICAL`, `HIGH` or `MEDIUM`   |
| description | what the risk is                 |

`user_roles.csv`

| column    | meaning                       |
|-----------|-------------------------------|
| user_id   | user ID                       |
| tcode     | T-code the user can execute   |
| role_name | role that gives this T-code   |

T-codes are trimmed and converted to upper case when the files are loaded.

## Tests

```bash
pytest
```

## Limitations

- The data is **fictional** and very small (3 rules, 7 rows). Some T-codes, such as `PAY01`, are made up for the example.
- It only compares T-codes. Real SoD analysis in SAP also looks at authorization objects and their values.
  
## Project structure

```
main.py                 loading data, detecting conflicts, writing the report
tests/test_sod.py       pytest tests
sod_matrix.csv          sample risk rules
user_roles.csv          sample user authorizations
notebooks/              exploratory notebook used to prototype the logic
```
