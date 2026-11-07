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