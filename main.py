import pandas as pd


def load_sod_matrix(file_path: str = "sod_matrix.csv") -> pd.DataFrame:
    # Load SoD risk matrix from CSV file
    return pd.read_csv(file_path)


def load_user_roles(file_path: str = "user_roles.csv") -> pd.DataFrame:
    # Load user authorizations from CSV file
    return pd.read_csv(file_path)


def detect_sod_conflicts(
    df_user_roles: pd.DataFrame, df_sod: pd.DataFrame
) -> pd.DataFrame:
    # Cross-join user tcodes on user_id
    df_pairs = pd.merge(
        df_user_roles, df_user_roles, on="user_id", suffixes=("_a", "_b")
    )

    # Drop self-matched transactions
    df_pairs = df_pairs[df_pairs["tcode_a"] != df_pairs["tcode_b"]]

    # Match against risk matrix
    df_conflicts = pd.merge(
        df_pairs, df_sod, on=["tcode_a", "tcode_b"], how="inner"
    )

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
    return df_conflicts[cols]


def main():
    print("Starting SoD analysis from CSV files...")

    df_sod = load_sod_matrix()
    df_roles = load_user_roles()
    df_conflicts = detect_sod_conflicts(df_roles, df_sod)

    output_file = "sod_analysis_report.xlsx"
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_roles.to_excel(writer, sheet_name="User Authorizations", index=False)
        df_conflicts.to_excel(
            writer, sheet_name="SoD Conflicts Report", index=False
        )

    print(f"Done. Found {len(df_conflicts)} conflicts. Saved to {output_file}")


if __name__ == "__main__":
    main()