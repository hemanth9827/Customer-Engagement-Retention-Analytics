import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Customer Retention Analytics", page_icon="📊", layout="wide")
st.title("Customer Engagement & Product Utilization Analytics")
st.caption("Retention strategy dashboard | Descriptive analytics, not a causal churn model")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

uploaded = st.sidebar.file_uploader("Upload bank customer CSV (optional)", type=["csv"])
try:
    df = load_data(uploaded if uploaded is not None else "European_Bank.csv")
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

required = ["CustomerId","Balance","NumOfProducts","IsActiveMember","HasCrCard","Exited","EstimatedSalary"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error("Missing required columns: " + ", ".join(missing)); st.stop()

for c in ["Balance","NumOfProducts","IsActiveMember","HasCrCard","Exited","EstimatedSalary"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df.dropna(subset=["Balance","NumOfProducts","IsActiveMember","Exited"])
df["IsActiveMember"] = df["IsActiveMember"].astype(int)
df["Exited"] = df["Exited"].astype(int)
df["Engagement"] = np.where(df.IsActiveMember.eq(1),"Active","Inactive")
q75 = df.Balance.quantile(.75)
df["RelationshipStrengthScore"] = (df.IsActiveMember*50 + np.minimum(df.NumOfProducts,2)/2*50).round().astype(int)
df["HighValueDisengaged"] = (df.IsActiveMember.eq(0)) & (df.Balance.ge(q75))
df["RiskSegment"] = np.select(
    [df.HighValueDisengaged, (df.IsActiveMember.eq(0)) & (df.NumOfProducts.eq(1)),
     (df.IsActiveMember.eq(1)) & (df.NumOfProducts.eq(1)),
     (df.IsActiveMember.eq(1)) & (df.NumOfProducts.ge(2))],
    ["Inactive high-balance","Inactive single-product","Active single-product","Active multi-product"],
    default="Other")

st.sidebar.header("Filters")
engagement = st.sidebar.multiselect("Engagement", ["Active","Inactive"], default=["Active","Inactive"])
products = st.sidebar.slider("Product count", int(df.NumOfProducts.min()), int(df.NumOfProducts.max()),
                              (int(df.NumOfProducts.min()), int(df.NumOfProducts.max())))
bal_min, bal_max = float(df.Balance.min()), float(df.Balance.max())
balance_range = st.sidebar.slider("Balance range", bal_min, bal_max, (bal_min,bal_max))
sal_min, sal_max = float(df.EstimatedSalary.min()), float(df.EstimatedSalary.max())
salary_range = st.sidebar.slider("Estimated salary range", sal_min, sal_max, (sal_min,sal_max))
geo_opts = sorted(df["Geography"].dropna().unique()) if "Geography" in df else []
geos = st.sidebar.multiselect("Geography", geo_opts, default=geo_opts)

f = df[df.Engagement.isin(engagement) & df.NumOfProducts.between(*products) &
       df.Balance.between(*balance_range) & df.EstimatedSalary.between(*salary_range)]
if "Geography" in f and geos:
    f = f[f.Geography.isin(geos)]
if f.empty:
    st.warning("No customers match these filters."); st.stop()

total=len(f); rate=f.Exited.mean()
active_rate=f.loc[f.IsActiveMember.eq(1),"Exited"].mean()
inactive_rate=f.loc[f.IsActiveMember.eq(0),"Exited"].mean()
c1,c2,c3,c4=st.columns(4)
c1.metric("Customers in selection",f"{total:,}")
c2.metric("Churn rate",f"{rate:.1%}")
c3.metric("Avg. products",f"{f.NumOfProducts.mean():.2f}")
c4.metric("Avg. relationship score",f"{f.RelationshipStrengthScore.mean():.1f}/100")

tab1,tab2,tab3,tab4=st.tabs(["Overview","Product utilization","High-value detector","Relationship strength"])
with tab1:
    st.subheader("Engagement vs churn")
    g=f.groupby("Engagement").Exited.agg(["count","mean"]).reset_index()
    st.bar_chart(g.set_index("Engagement")["mean"])
    st.dataframe(g.rename(columns={"count":"Customers","mean":"Churn rate"}), use_container_width=True)
    if pd.notna(active_rate) and pd.notna(inactive_rate):
        st.info(f"Active churn: {active_rate:.1%} | Inactive churn: {inactive_rate:.1%}")
    if "Geography" in f:
        st.subheader("Churn by geography")
        st.bar_chart(f.groupby("Geography").Exited.mean())
with tab2:
    st.subheader("Churn by number of products")
    p=f.groupby("NumOfProducts").Exited.agg(Customers="size",Churn_Rate="mean").reset_index()
    st.bar_chart(p.set_index("NumOfProducts")["Churn_Rate"])
    st.dataframe(p, use_container_width=True)
    st.caption("Product count is a proxy for relationship depth; the file does not include product names or mix.")
with tab3:
    st.subheader("Inactive customers with high balances")
    st.caption(f"High-balance threshold is the 75th percentile in the loaded data: {q75:,.2f}")
    hv=f[f.HighValueDisengaged].copy()
    a,b=st.columns(2); a.metric("Customers flagged",f"{len(hv):,}"); b.metric("Churn rate in flagged group",f"{hv.Exited.mean():.1%}" if len(hv) else "—")
    display_cols=[c for c in ["CustomerId","Geography","Age","Balance","EstimatedSalary","NumOfProducts","IsActiveMember","Exited"] if c in hv]
    st.dataframe(hv[display_cols].sort_values("Balance",ascending=False),use_container_width=True)
    st.download_button("Download flagged customers",hv.to_csv(index=False).encode("utf-8"),"high_value_disengaged.csv","text/csv")
with tab4:
    st.subheader("Relationship Strength Index")
    st.write("Transparent heuristic: 50 points for active status + up to 50 points for holding at least two products.")
    st.metric("Average score",f"{f.RelationshipStrengthScore.mean():.1f}/100")
    st.bar_chart(f.groupby("RelationshipStrengthScore").Exited.mean())
    st.dataframe(f.groupby("RelationshipStrengthScore").agg(Customers=("Exited","size"),Churn_Rate=("Exited","mean")).reset_index(),use_container_width=True)

st.divider()
st.subheader("Filtered customer data")
st.dataframe(f, use_container_width=True)
st.download_button("Download filtered data", f.to_csv(index=False).encode("utf-8"), "filtered_customers.csv", "text/csv")
st.caption("Use customer-level outputs only under approved access, privacy, fairness and suitability controls.")
