import streamlit as st
import pandas as pd
from datetime import datetime
import pathlib

SHEET_ID = "16BppQGDtoAKSelaxaZfhVgdpR7Q4cDj23ep3YO9bXU" 
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Sheet1"

BASE = pathlib.Path(__file__).parent
st.set_page_config(page_title="نجدة - مبادرة حفصة وائل", layout="wide", page_icon="💧")

# --- Banner ---
bp = BASE / "banner_final.jpg"
if bp.exists():
    st.image(str(bp), use_container_width=True)

st.markdown("""
<div style='background:#0A6E2F; color:white; padding:12px; text-align:center; border-radius:10px; font-size:18px;'>
<b>رؤية 2030 - #بترشيدنا_تدوم_نعمتنا</b><br>
الابتدائية العاشرة بينبع البحر - مبادرة الطالبة حفصة وائل
</div>
""", unsafe_allow_html=True)

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
class_map = {"Grade1":"اول ابتدائي","Grade2":"ثاني ابتدائي","Grade3":"ثالث ابتدائي","Grade4":"رابع ابتدائي","Grade5":"خامس ابتدائي","Grade6":"سادس ابتدائي","Grade1M":"اول متوسط","Grade2M":"ثاني متوسط","Grade3M":"ثالث متوسط"}

@st.cache_data(ttl=60)
def load_from_gsheet():
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if df.empty or "cls" not in df.columns:
            return pd.DataFrame(columns=["cls","save","dt","std","activity"])
        df["dt"] = pd.to_datetime(df["dt"], errors='coerce').dt.date
        return df
    except:
        return pd.DataFrame(columns=["cls","save","dt","std","activity"])

def save_to_gsheet(new_row):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        sheet.append_row([new_row["cls"], new_row["save"], str(new_row["dt"]), new_row["std"], new_row["activity"]])
        return True
    except Exception as e:
        st.error(f"خطأ في الحفظ: {e}")
        return False

def get_risk_level(s):
    if s >= 150: return "آمن ✅", "#2ECC71"
    elif s >= 70: return "متوسط ⚠️", "#F39C12"
    else: return "خطر ❗", "#E74C3C"

if 'data' not in st.session_state:
    st.session_state.data = load_from_gsheet()

# --- Sidebar ---
with st.sidebar:
    st.header("💧 تسجيل نشاط حقيقي")
    cls_en = st.selectbox("الفصل", list(class_map.keys()), format_func=lambda x: class_map[x])
    act_en = st.selectbox("نوع النشاط", list(activities.keys()), format_func=lambda x: activities[x])
    save = st.number_input("التوفير (لتر)", value=55, min_value=1, max_value=1000)
    std = st.number_input("عدد الطالبات المشاركات", value=27, min_value=1)
    
    label, color = get_risk_level(save)
    st.markdown(f'<div style="background:{color}; color:white; padding:16px; border-radius:8px; text-align:center; font-weight:bold; font-size:18px;">مؤشر التوفير: {label}<br>{save} لتر</div>', unsafe_allow_html=True)
    st.write("")

    if st.button("💾 حفظ النشاط", use_container_width=True, type="primary"):
        new_row = {"cls": cls_en, "save": save, "dt": datetime.now().date(), "std": std, "activity": act_en}
        ok = save_to_gsheet(new_row)
        if ok:
            st.success("تم الحفظ في جوجل شيت!")
            st.cache_data.clear()
            st.session_state.data = load_from_gsheet()
            st.rerun()
        else:
            st.warning("تم الحفظ محلياً فقط - تأكدي من Secrets")

    if st.button("🔄 تحديث البيانات", use_container_width=True):
        st.cache_data.clear()
        st.session_state.data = load_from_gsheet()
        st.rerun()

# --- Main Dashboard ---
df = st.session_state.data
if not df.empty:
    total = df["save"].sum()
    avg = df["save"].mean()
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي التوفير", f"{total} لتر")
    m2.metric("المتوسط", f"{int(avg)} لتر")
    m3.metric("الأنشطة", f"{len(df)} نشاط")

    st.subheader("📊 التحليلات")
    t1, t2 = st.tabs(["حسب الفصل", "حسب النشاط"])
    with t1:
        by_class = df.groupby("cls")["save"].sum().reset_index()
        by_class["الفصل"] = by_class["cls"].map(class_map)
        st.bar_chart(by_class, x="الفصل", y="save", color="#0A6E2F")
    with t2:
        by_act = df.groupby("activity")["save"].sum().reset_index()
        by_act["النشاط"] = by_act["activity"].map(activities)
        st.bar_chart(by_act, x="النشاط", y="save", color="#0A6E2F")
    
    with st.expander("📋 عرض الجدول كامل"):
        st.dataframe(df, use_container_width=True)

    st.subheader("🤖 الذكاء الاصطناعي")
    best_c = df.groupby("cls")["save"].sum().idxmax()
    best_a = df.groupby("activity")["save"].sum().idxmax()
    ai1, ai2, ai3 = st.columns(3)
    ai1.info(f"**التوفير القادم المتوقع:**\n\n{int(avg*1.15)} لتر")
    ai2.success(f"**أفضل فصل:**\n\n{class_map.get(best_c,best_c)}")
    ai3.warning(f"**أكثر نشاط مؤثر:**\n\n{activities.get(best_a,best_a)}")

    st.subheader("🏆 الشهادة")
    last_class = class_map.get(df.iloc[-1]["cls"], df.iloc[-1]["cls"])
    st.markdown(f"""
    <div style='border:3px solid #0A6E2F; padding:20px; text-align:center; border-radius:15px; background:#f0fff4;'>
    <h2>شهادة شكر وتقدير</h2>
    <p>تتقدم إدارة المدرسة بالشكر والتقدير للصف</p>
    <h3>{last_class}</h3>
    <p>على تميزه في ترشيد نعمة الماء وتوفير <b>{total} لتر</b> من المياه</p>
    <p><b>#بترشيدنا_تدوم_نعمتنا - رؤية 2030</b></p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("لا توجد بيانات بعد - ابدأي بتسجيل أول نشاط من الشريط الجانبي 💧")

st.subheader("📍 موقع المدرسة - ينبع البحر")
st.map(pd.DataFrame([{"lat":24.0896, "lon":38.0618}]), zoom=12)
