import pandas as pd
from pathlib import Path

def main():
    print("Starting SoD analysis...")

    df_sod = load_sod_matrix()
    df_roles = load_user_roles()
    df_conflicts = detect_sod_conflicts(df_roles, df_sod)

    # Ensure output directory exists
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "sod_analysis_report.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_roles.to_excel(writer, sheet_name="User Authorizations", index=False)
        df_conflicts.to_excel(
            writer, sheet_name="SoD Conflicts Report", index=False
        )

    print(
        f"Done. Found {len(df_conflicts)} conflicts. Saved report to"
        f" {output_file}"
    )

def load_sod_matrix(file_path: str = "sod_matrix.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype=str)
    required_cols = {
        "risk_id",
        "tcode_a",
        "tcode_b",
        "risk_level",
        "description",
    }
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(
            f"Missing required columns in SoD matrix CSV: {missing}"
        )

    for col in ["tcode_a", "tcode_b"]:
        df[col] = df[col].str.strip().str.upper()

    return df.drop_duplicates()


def load_user_roles(file_path: str = "user_roles.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path, dtype=str)
    required_cols = {"user_id", "tcode", "role_name"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(
            f"Missing required columns in User Roles CSV: {missing}"
        )

    df["tcode"] = df["tcode"].str.strip().str.upper()
    df["user_id"] = df["user_id"].str.strip()
    df["role_name"] = df["role_name"].str.strip()

    return df.drop_duplicates()
def detect_sod_conflicts(
    df_user_roles: pd.DataFrame, df_sod: pd.DataFrame
) -> pd.DataFrame:
    # Match user roles against tcode_a of risk matrix
    matched_a = pd.merge(
        df_user_roles,
        df_sod,
        left_on="tcode",
        right_on="tcode_a",
        how="inner",
    )

    # Match user roles against tcode_b for the same user
    matched_b = pd.merge(
        matched_a,
        df_user_roles,
        left_on=["user_id", "tcode_b"],
        right_on=["user_id", "tcode"],
        suffixes=("_a", "_b"),
        how="inner",
    )

    df_conflicts = matched_b[matched_b["tcode_a"] != matched_b["tcode_b"]]

    cols = [
        "user_id",
        "risk_id",
        "risk_level",
        "tcode_a",
        "tcode_b",
        "role_name_a",
        "role_name_b",
        "description",
    ]
    return df_conflicts[cols].drop_duplicates()


def generate_summary(df_conflicts: pd.DataFrame) -> pd.DataFrame:
    if df_conflicts.empty:
        return pd.DataFrame(columns=["Metric", "Value"])

    by_risk = df_conflicts["risk_level"].value_counts().reset_index()
    by_risk.columns = ["Risk Level / Metric", "Count"]

    total_conflicts = pd.DataFrame(
        [{"Risk Level / Metric": "Total Conflicts", "Count": len(df_conflicts)}]
    )
    affected_users = pd.DataFrame(
        [{
            "Risk Level / Metric": "Affected Users Count",
            "Count": df_conflicts["user_id"].nunique(),
        }]
    )

    return pd.concat([total_conflicts, affected_users, by_risk], ignore_index=True)

df_summary = generate_summary(df_conflicts)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_summary.to_excel(writer, sheet_name="Summary", index=False)
        df_roles.to_excel(writer, sheet_name="User Authorizations", index=False)
        df_conflicts.to_excel(
            writer, sheet_name="SoD Conflicts Report", index=False
        )