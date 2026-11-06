import pandas as pd


def get_sod_matrix() -> pd.DataFrame:
    # Define standard SAP SoD risk rules
    sod_data = [
        {
            "risk_id": "SOD_01",
            "tcode_a": "FK01",
            "tcode_b": "PAY01",
            "risk_level": "CRITICAL",
            "description": "Vendor creation and payment execution by same user",
        },
        {
            "risk_id": "SOD_02",
            "tcode_a": "FB01",
            "tcode_b": "PAY01",
            "risk_level": "HIGH",
            "description": "GL posting and payment execution by same user",
        },
        {
            "risk_id": "SOD_03",
            "tcode_a": "ME21N",
            "tcode_b": "MIRO",
            "risk_level": "MEDIUM",
            "description": "PO creation and Invoice verification by same user",
        },
    ]
    return pd.DataFrame(sod_data)


def get_user_roles() -> pd.DataFrame:
    # Dummy user access data for testing
    user_roles_data = [
        {"user_id": "U001", "tcode": "FK01", "role_name": "Vendor_Admin"},
        {"user_id": "U001", "tcode": "PAY01", "role_name": "Payment_Clerk"},
        {"user_id": "U002", "tcode": "FB01", "role_name": "GL_Accountant"},
        {"user_id": "U002", "tcode": "PAY01", "role_name": "Payment_Clerk"},
        {"user_id": "U003", "tcode": "ME21N", "role_name": "Purchaser"},
        {"user_id": "U003", "tcode": "MIRO", "role_name": "AP_Clerk"},
        {"user_id": "U004", "tcode": "FK01", "role_name": "Vendor_Admin"},
    ]
    return pd.DataFrame(user_roles_data)


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
    print("Starting SoD analysis...")

    df_sod = get_sod_matrix()
    df_roles = get_user_roles()
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