import streamlit as st
import pandas as pd
from datetime import datetime
import pathlib

SHEET_ID = st.secrets.get("SHEET_ID", "16BppQGDtoAK5eIaxaZfhJVgdpR7Q4cDj23ep3YO9bXU")
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"

BASE = pathlib.Path(__file__).parent
BACKUP_FILE = BASE / "backup_data.csv"
st.set_page_config(page_title="Najda - مبادرة الطالبة حفصة وائل", layout="wide")

bp = BASE / "banner_final.jpg"
if bp.exists():
    st.image(str(bp), use_container_width=True)

st.markdown("<div style='background:#0A6E2F; color:white; padding:12px; text-align:center; border-radius:10px;'><b>رؤية 2030 - #بترشيدنا_تدوم_نعمتنا</b><br>الابتدائية العاشرة بينبع البحر - مبادرة الطالبة حفصة وائل</div>", unsafe_allow_html=True)

activities = {
    "close_taps": "إغلاق الصنابير بعد الاستخدام",
    "fix_leak": "إصلاح تسريب مياه",
    "awareness": "حملة توعية داخل الفصل",
    "bottles": "استخدام قارورات قابلة لإعادة التعبئة",
    "garden": "تقليل سقي الحديقة",
    "wudu": "ترشيد مياه الوضوء",
    "clean": "تنظيف بدون هدر",
    "report": "الإبلاغ عن هدر"
}
# الأرقام العلمية لكل نشاط (مراجع)
auto_save_map = {
    "close_taps": 20,  # 6 لتر/دقيقة - صنبور عادي
    "fix_leak": 65,    # 72 لتر/يوم للتسريب حسب WWF و Learnz
    "awareness": 15,   # تغيير سلوكي 10-15%
    "bottles": 10,     # غسيل أقل
    "garden": 50,      # توفير 40-50% بالتنقيط
    "wudu": 6,         # 7 لتر حالي - 0.775 سنة = 6 توفير للفرد
    "clean": 35,       # دلو 15 لتر بدل خرطوم 10 لتر/دقيقة
    "report": 60       # منع تسريب مستمر
}
scientific_note = {
    "close_taps": "الحنفية تستهلك 6 لتر/دقيقة، إغلاقها يوفر 6 لتر كل مرة",
    "fix_leak": "الصنبور المنقط 50مل/دقيقة يهدر 72 لتر/يوم (مصدر: Learnz + WWF)",
    "awareness": "التوعية تغير سلوك 10% من الاستهلاك",
    "bottles": "القارورة القابلة لإعادة التعبئة توفر غسيل ومياه مهدرة",
    "garden": "الري بالتنقيط يوفر 40-50% حسب دراسات السعودية",
    "wudu": "الوضوء النبوي مد واحد = 0.775 لتر، الحالي 7 لتر، التوفير 6 لتر/طالبة",
    "clean": "الدلو 15 لتر بدل خرطوم 10 لتر/دقيقة يوفر 35 لتر",
    "report": "الإبلاغ يمنع هدر مستمر 60 لتر/يوم"
}

class_map = {"Grade1":"اول ابتدائي","Grade2":"ثاني ابتدائي","Grade3":"ثالث ابتدائي","Grade4":"رابع ابتدائي","Grade5":"خامس ابتدائي","Grade6":"سادس ابتدائي","Grade1M":"اول متوسط","Grade2M":"ثاني متوسط","Grade3M":"ثالث متوسط"}

def load_from_gsheet():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        all_dfs = []
        for ws in spreadsheet.worksheets():
            if "تقرير" in ws.title: continue
            try:
                records = ws.get_all_records()
                if records:
                    df_temp = pd.DataFrame(records)
                    if "cls" in df_temp.columns:
                        all_dfs.append(df_temp)
            except:
                continue
        if all_dfs:
            df = pd.concat(all_dfs, ignore_index=True)
            df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
            df.to_csv(BACKUP_FILE, index=False)
            return df
        df = pd.read_csv(SHEET_CSV_URL)
        if df.empty or "cls" not in df.columns:
            raise ValueError("الشيت فاضي")
        df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
        df.to_csv(BACKUP_FILE, index=False)
        return df
    except Exception as e:
        if BACKUP_FILE.exists():
            try:
                df = pd.read_csv(BACKUP_FILE)
                df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
                return df
            except:
                pass
        return pd.DataFrame(columns=["cls","save","dt","std","activity"])

def save_to_gsheet(new_row):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        month_name = datetime.now().strftime("%Y-%m")
        try:
            sheet = spreadsheet.worksheet(month_name)
        except:
            sheet = spreadsheet.add_worksheet(title=month_name, rows=1000, cols=10)
            sheet.append_row(["cls","save","dt","std","activity"])
        sheet.append_row([new_row["cls"], new_row["save"], str(new_row["dt"]), new_row["std"], new_row["activity"]])
        return True, "ok"
    except Exception as e:
        return False, str(e)

def generate_yearly_report(df_all, year):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SHEET_ID)
        df_year = df_all[pd.to_datetime(df_all["dt"]).dt.year == int(year)].copy()
        if df_year.empty:
            return False, "مفيش بيانات للسنة دي"
        total = df_year["save"].sum()
        by_month = df_year.groupby(pd.to_datetime(df_year["dt"]).dt.strftime("%Y-%m"))["save"].sum()
        by_class = df_year.groupby("cls")["save"].sum()
        by_act = df_year.groupby("activity")["save"].sum()
        report_name = f"تقرير {year}"
        try:
            ws = spreadsheet.worksheet(report_name)
            spreadsheet.del_worksheet(ws)
        except:
            pass
        ws = spreadsheet.add_worksheet(title=report_name, rows=100, cols=10)
        ws.append_row([f"تقرير مبادرة نجدة لسنة {year} - رؤية 2030"])
        ws.append_row([f"إجمالي التوفير السنوي", f"{total} لتر"])
        ws.append_row([f"عدد الأنشطة", f"{len(df_year)}"])
        ws.append_row([])
        ws.append_row(["التوفير حسب الشهر"])
        for m, v in by_month.items():
            ws.append_row([m, int(v)])
        ws.append_row([])
        ws.append_row(["التوفير حسب الفصل"])
        for c, v in by_class.items():
            ws.append_row([class_map.get(c,c), int(v)])
        ws.append_row([])
        ws.append_row(["التوفير حسب النشاط"])
        for a, v in by_act.items():
            ws.append_row([activities.get(a,a), int(v)])
        return True, report_name
    except Exception as e:
        return False, str(e)

def get_risk_level(s):
    if s >= 150: return "آمن", "#2ECC71", "green"
    elif s >= 70: return "متوسط", "#F39C12", "yellow"
    else: return "خطر", "#E74C3C", "red"

if 'data' not in st.session_state:
    st.session_state.data = load_from_gsheet()
if 'last_error' not in st.session_state:
    st.session_state.last_error = ""

with st.sidebar:
    st.header("تسجيل نشاط حقيقي")
    cls_en = st.selectbox("الفصل", list(class_map.keys()), format_func=lambda x: class_map[x])
    act_en = st.selectbox("نوع النشاط", list(activities.keys()), format_func=lambda x: activities[x])
    std = st.number_input("عدد الطالبات", value=27, min_value=1)
    
    base = auto_save_map.get(act_en, 20)
    if act_en == "wudu":
        suggested = base * std
    elif act_en in ["close_taps", "awareness"]:
        suggested = base * max(1, std // 9)
    else:
        suggested = base
    
    save = st.number_input("التوفير لتر (مقترح علمياً)", value=int(suggested), min_value=1)
    st.caption(f"💡 {scientific_note.get(act_en)}")
    
    label, color, _ = get_risk_level(save)
    st.markdown(f'<div style="background:{color}; color:white; padding:16px; border-radius:8px; text-align:center; font-weight:bold;">مؤشر الخطر: {label}<br>{save} لتر</div>', unsafe_allow_html=True)
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 حفظ النشاط", use_container_width=True, type="primary"):
            new_row = {"cls": cls_en, "save": save, "dt": datetime.now().date(), "std": std, "activity": act_en}
            ok, msg = save_to_gsheet(new_row)
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.data.to_csv(BACKUP_FILE, index=False)
            if ok:
                st.session_state.last_error = ""
                st.success("تم الحفظ!")
            else:
                st.session_state.last_error = msg
            st.rerun()
    with col2:
        if st.button("🗑️ تصفير", use_container_width=True):
            st.session_state.data = pd.DataFrame(columns=["cls","save","dt","std","activity"])
            st.session_state.last_error = ""
            if BACKUP_FILE.exists():
                BACKUP_FILE.unlink()
            st.warning("تم التصفير")
    if st.session_state.last_error:
        st.error(st.session_state.last_error)

df = st.session_state.data
if not df.empty:
    df["month"] = pd.to_datetime(df["dt"], errors='coerce').dt.strftime("%Y-%m")
    months = sorted(df["month"].dropna().unique(), reverse=True)
    current_month = datetime.now().strftime("%Y-%m")
    default_idx = months.index(current_month) if current_month in months else 0
    selected_month = st.selectbox(f"📅 عرض بيانات شهر: (الحالي {current_month})", months, index=default_idx)
    df_display = df[df["month"] == selected_month].copy()

    total = df_display["save"].sum()
    avg = df_display["save"].mean()
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي التوفير", f"{total} لتر")
    m2.metric("المتوسط", f"{int(avg) if not pd.isna(avg) else 0} لتر")
    m3.metric("الأنشطة", f"{len(df_display)}")

    st.subheader("📊 الجداول")
    t1, t2 = st.tabs(["حسب الفصل", "حسب النشاط"])
    with t1:
        by_class = df_display.groupby("cls")["save"].sum().reset_index()
        by_class["الفصل"] = by_class["cls"].map(class_map)
        st.bar_chart(by_class, x="الفصل", y="save")
    with t2:
        by_act = df_display.groupby("activity")["save"].sum().reset_index()
        by_act["النشاط"] = by_act["activity"].map(activities)
        st.bar_chart(by_act, x="النشاط", y="save")
    st.dataframe(df_display, use_container_width=True)

    st.subheader("🤖 الذكاء الاصطناعي")
    best_c = df_display.groupby("cls")["save"].sum().idxmax() if not df_display.empty else ""
    best_a = df_display.groupby("activity")["save"].sum().idxmax() if not df_display.empty else ""
    ai1, ai2, ai3 = st.columns(3)
    ai1.info(f"**التوفير القادم المتوقع:**\n\n{int(avg*1.15) if not pd.isna(avg) else 0} لتر")
    ai2.success(f"**أفضل فصل:**\n\n{class_map.get(best_c,best_c)}")
    ai3.warning(f"**أكثر نشاط مؤثر:**\n\n{activities.get(best_a,best_a)}")

    st.subheader("🏆 الشهادة")
    last_class = class_map.get(df_display.iloc[-1]["cls"], df_display.iloc[-1]["cls"]) if not df_display.empty else ""
    st.markdown(f"""
    <div style='border:3px solid #0A6E2F; padding:20px; text-align:center; border-radius:15px; background:#f0fff4;'>
    <h2>شهادة شكر وتقدير</h2>
    <p>تتقدم إدارة المدرسة بالشكر والتقدير للصف</p>
    <h3>{last_class}</h3>
    <p>على تميزه في ترشيد نعمة الماء وتوفير <b>{total} لتر</b> خلال شهر {selected_month}</p>
    <p>#بترشيدنا_تدوم_نعمتنا - رؤية 2030</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 تقرير نهاية العام")
    years = sorted(pd.to_datetime(df["dt"]).dt.year.dropna().unique().astype(int).tolist(), reverse=True)
    year_to_report = st.selectbox("اختر السنة للتقرير", years)
    if st.button(f"📄 إنشاء تقرير {year_to_report}", use_container_width=True):
        ok, msg = generate_yearly_report(df, year_to_report)
        if ok:
            st.success(f"تم إنشاء {msg} في جوجل شيت!")
        else:
            st.error(msg)
else:
    st.info("لا توجد بيانات بعد")

st.subheader("📍 موقع المدرسة")
st.map(pd.DataFrame([{"lat":24.0896, "lon":38.0618}]), zoom=12)
