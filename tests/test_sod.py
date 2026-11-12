import pandas as pd
from main import detect_sod_conflicts, generate_summary

def test_detect_sod_conflicts_basic():
    user_roles = pd.DataFrame([
        {"user_id": "USR01", "tcode": "FB60", "role_name": "AP_CLERK"},
        {"user_id": "USR01", "tcode": "F-53", "role_name": "AP_PAYER"},
    ])

    sod_matrix = pd.DataFrame([
        {
            "risk_id": "RSK01",
            "tcode_a": "FB60",
            "tcode_b": "F-53",
            "risk_level": "CRITICAL",
            "description": "Invoice and Payment",
        }
    ])

    conflicts = detect_sod_conflicts(user_roles, sod_matrix)

    assert len(conflicts) == 1
    assert conflicts.iloc[0]["user_id"] == "USR01"
    assert conflicts.iloc[0]["risk_id"] == "RSK01"


def test_detect_sod_conflicts_case_insensitivity():
    user_roles = pd.DataFrame([
        {"user_id": "USR02", "tcode": "FB60", "role_name": "ROLE_A"},
        {"user_id": "USR02", "tcode": "F-53", "role_name": "ROLE_B"},
    ])

    sod_matrix = pd.DataFrame([
        {
            "risk_id": "RSK01",
            "tcode_a": "FB60",
            "tcode_b": "F-53",
            "risk_level": "CRITICAL",
            "description": "Invoice and Payment",
        }
    ])

    conflicts = detect_sod_conflicts(user_roles, sod_matrix)
    assert len(conflicts) == 1

def test_no_conflicts_when_roles_do_not_overlap():
    user_roles = pd.DataFrame([
        {"user_id": "USR03", "tcode": "FB60", "role_name": "AP_CLERK"},
        {"user_id": "USR03", "tcode": "VA01", "role_name": "SALES_REP"},
    ])

    sod_matrix = pd.DataFrame([
        {
            "risk_id": "RSK01",
            "tcode_a": "FB60",
            "tcode_b": "F-53",
            "risk_level": "CRITICAL",
            "description": "Invoice and Payment",
        }
    ])

    conflicts = detect_sod_conflicts(user_roles, sod_matrix)
    assert conflicts.empty