import pandas as pd
import pytest

from main import (
    detect_sod_conflicts,
    generate_summary,
    load_sod_matrix,
    load_user_roles,
)


def make_sod_matrix():
    return pd.DataFrame([
        {
            "risk_id": "RSK01",
            "tcode_a": "FB60",
            "tcode_b": "F-53",
            "risk_level": "CRITICAL",
            "description": "Invoice and Payment",
        }
    ])


# --- detect_sod_conflicts ---

def test_detect_sod_conflicts_basic():
    user_roles = pd.DataFrame([
        {"user_id": "USR01", "tcode": "FB60", "role_name": "AP_CLERK"},
        {"user_id": "USR01", "tcode": "F-53", "role_name": "AP_PAYER"},
    ])

    conflicts = detect_sod_conflicts(user_roles, make_sod_matrix())

    assert len(conflicts) == 1
    assert conflicts.iloc[0]["user_id"] == "USR01"
    assert conflicts.iloc[0]["risk_id"] == "RSK01"


def test_no_conflicts_when_roles_do_not_overlap():
    user_roles = pd.DataFrame([
        {"user_id": "USR03", "tcode": "FB60", "role_name": "AP_CLERK"},
        {"user_id": "USR03", "tcode": "VA01", "role_name": "SALES_REP"},
    ])

    conflicts = detect_sod_conflicts(user_roles, make_sod_matrix())

    assert conflicts.empty


def test_no_conflict_when_tcodes_belong_to_different_users():
    # Each user has only one of the two risky T-codes.
    user_roles = pd.DataFrame([
        {"user_id": "USR01", "tcode": "FB60", "role_name": "AP_CLERK"},
        {"user_id": "USR02", "tcode": "F-53", "role_name": "AP_PAYER"},
    ])

    conflicts = detect_sod_conflicts(user_roles, make_sod_matrix())

    assert conflicts.empty


# --- generate_summary ---

def test_generate_summary_structure():
    conflicts = pd.DataFrame([
        {
            "user_id": "USR01",
            "risk_id": "RSK01",
            "risk_level": "HIGH",
            "tcode_a": "FB60",
            "tcode_b": "F-53",
            "role_name_a": "R1",
            "role_name_b": "R2",
            "description": "Test",
        }
    ])

    summary = generate_summary(conflicts)
    assert not summary.empty
    assert "Total Conflicts" in summary["Risk Level / Metric"].values


# --- loaders (reading CSV files) ---

def test_load_user_roles_cleans_tcodes_and_ids(tmp_path):
    csv_file = tmp_path / "user_roles.csv"
    csv_file.write_text(
        "user_id,tcode,role_name\n"
        " USR02 , fb60 , ROLE_A \n"
        "USR02,f-53,ROLE_B\n",
        encoding="utf-8",
    )

    df = load_user_roles(csv_file)

    assert list(df["tcode"]) == ["FB60", "F-53"]
    assert list(df["user_id"]) == ["USR02", "USR02"]
    assert list(df["role_name"]) == ["ROLE_A", "ROLE_B"]


def test_loaded_lowercase_data_still_finds_conflict(tmp_path):
    roles_file = tmp_path / "user_roles.csv"
    roles_file.write_text(
        "user_id,tcode,role_name\n"
        "USR02,fb60,ROLE_A\n"
        "USR02,f-53,ROLE_B\n",
        encoding="utf-8",
    )
    matrix_file = tmp_path / "sod_matrix.csv"
    matrix_file.write_text(
        "risk_id,tcode_a,tcode_b,risk_level,description\n"
        "RSK01,fb60,f-53,CRITICAL,Invoice and Payment\n",
        encoding="utf-8",
    )

    conflicts = detect_sod_conflicts(
        load_user_roles(roles_file), load_sod_matrix(matrix_file)
    )

    assert len(conflicts) == 1


def test_load_sod_matrix_cleans_tcodes_and_drops_duplicates(tmp_path):
    csv_file = tmp_path / "sod_matrix.csv"
    csv_file.write_text(
        "risk_id,tcode_a,tcode_b,risk_level,description\n"
        "RSK01, fb60 ,f-53,CRITICAL,Invoice and Payment\n"
        "RSK01,FB60,F-53,CRITICAL,Invoice and Payment\n",
        encoding="utf-8",
    )

    df = load_sod_matrix(csv_file)

    assert len(df) == 1
    assert df.iloc[0]["tcode_a"] == "FB60"
    assert df.iloc[0]["tcode_b"] == "F-53"


def test_load_user_roles_raises_on_missing_columns(tmp_path):
    csv_file = tmp_path / "user_roles.csv"
    csv_file.write_text("user_id,tcode\nUSR01,FB60\n", encoding="utf-8")

    with pytest.raises(ValueError, match="role_name"):
        load_user_roles(csv_file)


def test_load_sod_matrix_raises_on_missing_columns(tmp_path):
    csv_file = tmp_path / "sod_matrix.csv"
    csv_file.write_text("risk_id,tcode_a\nRSK01,FB60\n", encoding="utf-8")

    with pytest.raises(ValueError, match="tcode_b"):
        load_sod_matrix(csv_file)


def test_sample_data_in_repo_finds_expected_conflicts():
    conflicts = detect_sod_conflicts(load_user_roles(), load_sod_matrix())

    assert len(conflicts) == 3
    assert set(conflicts["user_id"]) == {"U001", "U002", "U003"}
