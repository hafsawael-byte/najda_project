def save_to_gsheet(new_row):
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        creds_dict = st.secrets["gcp_service_account"]

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1

        sheet.append_row([
            new_row["cls"],
            new_row["save"],
            str(new_row["dt"]),
            new_row["std"],
            new_row["activity"]
        ])

        return True

    except Exception as e:
        st.error(f"خطأ الحفظ: {e}")
        return False
