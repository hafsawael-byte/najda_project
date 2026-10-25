import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Najda Project", layout="wide")

# البانر - آمن
banner = "banner_final.jpg"
if not os.path.exists(banner):
    banner = r"C:\NAJDA\dashboard\banner_final.jpg"
if os.path.exists(banner):
    st.image(banner, use_container_width=True)
else:
    st.markdown("<div style='background:#0A5C36; padding:20px; text-align:center; border-radius:10px;'><h2 style='color:white;'>مشروع نجدة - #بترشيدنا تدوم نعمتنا</h2></div>", unsafe_allow_html=True)

CSV = "najda_data.csv"
CLASSES = ["روضة 1","روضة 2","اول ابتدائي","ثاني ابتدائي","ثالث ابتدائي","رابع ابتدائي","خامس ابتدائي","سادس ابتدائي","اول متوسط","ثاني متوسط","ثالث متوسط"]

def get_stage(f):
    if "روضة" in f:
        return "الروضة"
    if "ابتدائي" in f:
        return "الابتدائي"
    return "المتوسط"

try:
    df = pd.read_csv(CSV, encoding="utf-8-sig")
    total = int(df["لتر"].sum())
except:
    total = 0
    df = pd.DataFrame(columns=["التاريخ","الفصل","النشاط","لتر"])

c1,c2,c3,c4 = st.columns(4)
c1.metric("اجمالي التوفير", f"{total} لتر")
c2.metric("عدد الانشطة", len(df))
c3.metric("الميلادي", "10/2026")
c4.metric("الهجري", "1447 هـ")

if total == 0:
    st.warning("ضيفي اول نشاط")
else:
    df["المرحلة"] = df["الفصل"].apply(get_stage)
    st.subheader("الفائزين")
    stages = ["الروضة","الابتدائي","المتوسط"]
    for stage in stages:
        sub = df[df["المرحلة"]==stage]
        if not sub.empty:
            g = sub.groupby("الفصل")["لتر"].sum().reset_index().sort_values("لتر", ascending=False)
            data = g.iloc[0]
            st.success(f"{stage}: {data['الفصل']} - {data['لتر']} لتر")
            html = f"<div style='background:white; border:12px solid #0A5C36; outline:4px solid #C8A415; padding:25px; text-align:center; font-family:tahoma;'><p><b>المملكة العربية السعودية<br>وزارة التعليم<br>الابتدائية العاشرة والمتوسطة الرابعة - بينبع البحر</b></p><h1 style='color:#0A3D8A; margin:15px; font-size:42px;'>شهادة تقدير</h1><p style='font-size:20px;'><b>الفصل الفائز: {data['الفصل']}</b></p><p>المرحلة: {stage}</p><p style='color:#0A5C36; font-weight:bold; font-size:18px;'>كمية التوفير: {data['لتر']} لتر</p><p>التاريخ: 10/2026 - 1447 هـ</p><hr><p>تقديرا لتميزه كأفضل فصل في ترشيد المياه</p><p style='color:#0A7A2A;'><b>#بترشيدنا تدوم نعمتنا - مشروع نجدة</b></p><p style='background:#f0f8f0; padding:8px; margin-top:15px;'><b>مبادرة الطالبة: حفصة وائل</b></p><p style='font-size:11px; margin-top:10px;'>منسقة الموهوبات: أ. قمر الرويسي - مديرة المدرسة: أ. عبير الشريف</p></div>"
            components.html(html, height=560)
            st.download_button(f"تحميل شهادة {data['الفصل']}", data=html, file_name=f"شهادة_{data['الفصل']}.html", mime="text/html", key=f"cert_{data['الفصل']}_{stage}")

    st.divider()
    st.subheader("مقارنة الفصول")
    st.bar_chart(df.groupby("الفصل")["لتر"].sum())
    st.dataframe(df, use_container_width=True)

st.divider()
st.subheader("اضافة نشاط جديد")
fasl = st.selectbox("اختاري الفصل", CLASSES)
nash = st.selectbox("اختاري النشاط", ["قفل الحنفيات - 5 لتر","سقيا الزرع - 7 لتر","الابلاغ عن تسريب - 15 لتر","توعية الزملاء - 10 لتر"])

if st.button("حفظ النشاط", type="primary", use_container_width=True):
    l = 7 if "7" in nash else 15 if "15" in nash else 10 if "10" in nash else 5
    new = {"التاريخ":datetime.now().strftime("%Y-%m-%d"),"الفصل":fasl,"النشاط":nash,"لتر":l}
    try:
        old = pd.read_csv(CSV, encoding="utf-8-sig")
        final = pd.concat([old,pd.DataFrame([new])], ignore_index=True)
    except:
        final = pd.DataFrame([new])
    final.to_csv(CSV,index=False,encoding="utf-8-sig")
    st.balloons()
    st.rerun()

if st.button("تصفير البيانات"):
    if os.path.exists(CSV):
        os.remove(CSV)
    st.rerun()