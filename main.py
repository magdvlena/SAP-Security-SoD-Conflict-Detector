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