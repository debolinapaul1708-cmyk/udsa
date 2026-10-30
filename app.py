import hashlib, io, json, os, re
from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ProcureIQ Procurement Portal", page_icon="🏛️", layout="wide")
BASE_DIR=os.path.dirname(__file__)
USERS_FILE=os.path.join(BASE_DIR,"users.json")
UPLOAD_DIR=os.path.join(BASE_DIR,"uploads")
BIDS_FILE=os.path.join(BASE_DIR,"data","sample_bids.csv")
os.makedirs(UPLOAD_DIR,exist_ok=True)
FALLBACK_BIDS="""bid_id,title,department,closing_date,bid_amount,min_turnover,min_experience_years,required_certifications,category
GOV-2026-001,Supply of Medical Equipment,Health Department,2026-11-02,4500000,10000000,5,"ISO 9001; GST",Medical Equipment
GOV-2026-002,Road Maintenance Contract,Public Works Department,2026-11-03,12000000,25000000,8,"GST; Contractor License",Infrastructure
GOV-2026-003,IT Hardware Procurement,Education Department,2026-11-04,2800000,5000000,3,"GST; ISO 27001",IT Hardware
GOV-2026-004,Office Furniture Supply,General Administration,2026-11-05,1500000,3000000,2,"GST",Furniture
GOV-2026-005,Laboratory Chemicals Supply,Science & Technology Department,2026-11-06,2200000,4000000,4,"GST; ISO 9001",Laboratory Supplies
GOV-2026-006,School Uniform Manufacturing,Education Department,2026-11-07,3600000,6000000,3,"GST; ISO 9001",Textiles
GOV-2026-007,Solar Street Light Installation,Urban Development Department,2026-11-08,8900000,15000000,6,"GST; MNRE Empanelment",Renewable Energy
GOV-2026-008,Desktop Computers Supply,Home Department,2026-11-09,5200000,8000000,4,"GST; ISO 27001",IT Hardware
GOV-2026-009,Water Purification Systems,Rural Development Department,2026-11-10,6700000,12000000,5,"GST; BIS Certification",Water Solutions
GOV-2026-010,Security Guard Services,Public Works Department,2026-11-11,4300000,7000000,5,"GST; PSARA License",Manpower Services
GOV-2026-011,Hospital Beds Supply,Health Department,2026-11-12,3100000,5000000,3,"GST; ISO 13485",Medical Equipment
GOV-2026-012,Bridge Repair Works,Public Works Department,2026-11-13,18500000,35000000,10,"GST; Contractor License",Infrastructure
GOV-2026-013,Library Books Supply,Education Department,2026-11-14,900000,1500000,2,"GST",Books & Publications
GOV-2026-014,CCTV Surveillance System,Home Department,2026-11-15,7400000,12000000,6,"GST; ISO 9001",Security Systems
GOV-2026-015,Electric Buses Procurement,Transport Department,2026-11-16,42000000,80000000,12,"GST; ARAI Certification",Electric Vehicles
GOV-2026-016,Waste Management Services,Municipal Corporation,2026-11-17,5600000,9000000,5,"GST; CPCB Authorization",Waste Management
GOV-2026-017,Agricultural Equipment Supply,Agriculture Department,2026-11-18,3800000,6500000,4,"GST; ISO 9001",Agriculture
GOV-2026-018,Cloud Hosting Services,IT Department,2026-11-19,9800000,18000000,7,"GST; ISO 27001",IT Services
GOV-2026-019,Fire Safety Equipment Supply,Home Department,2026-11-20,2400000,4000000,3,"GST; BIS Certification",Safety Equipment
GOV-2026-020,Park Development Works,Urban Development Department,2026-11-21,11200000,20000000,8,"GST; Contractor License",Infrastructure
"""

if "authenticated" not in st.session_state:
    st.session_state.authenticated=False; st.session_state.user=None

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE,encoding="utf-8") as f: return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE,"w",encoding="utf-8") as f: json.dump(users,f,indent=2)

def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def login_signup():
    st.title("🏛️ ProcureIQ Procurement Portal")
    st.caption("Demonstration procurement portal. Not affiliated with any government platform.")
    login, signup=st.tabs(["Sign in","Create account"])
    with login:
        with st.form("login"):
            email=st.text_input("Email"); password=st.text_input("Password",type="password")
            ok=st.form_submit_button("Sign in",use_container_width=True)
        if ok:
            users=load_users()
            if email in users and users[email]["password"]==hash_password(password):
                st.session_state.authenticated=True
                st.session_state.user={"email":email,"name":users[email]["name"]}
                st.rerun()
            else: st.error("Invalid email or password.")
    with signup:
        with st.form("signup"):
            name=st.text_input("Full name"); company=st.text_input("Company / supplier name")
            email=st.text_input("Email"); password=st.text_input("Create password",type="password")
            confirm=st.text_input("Confirm password",type="password")
            create=st.form_submit_button("Create account",use_container_width=True)
        if create:
            users=load_users()
            if not name or not company or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",email):
                st.error("Enter valid name, company, and email.")
            elif email in users: st.error("Account already exists.")
            elif len(password)<6: st.error("Password must have at least 6 characters.")
            elif password!=confirm: st.error("Passwords do not match.")
            else:
                users[email]={"name":name,"company":company,"password":hash_password(password),"created_at":datetime.now().isoformat()}
                save_users(users); st.success("Account created. Please sign in.")

def load_bids():
    try: return pd.read_csv(BIDS_FILE)
    except FileNotFoundError: return pd.read_csv(io.StringIO(FALLBACK_BIDS))

def supplier_profile():
    with st.sidebar:
        st.header("Supplier profile")
        p=st.session_state.get("profile",{"turnover":12000000,"experience":6,"certifications":"ISO 9001, GST","categories":"Medical Equipment, IT Hardware"})
        turnover=st.number_input("Annual turnover (₹)",0,value=int(p["turnover"]),step=100000)
        experience=st.number_input("Years of experience",0,value=int(p["experience"]))
        certifications=st.text_input("Certifications",p["certifications"])
        categories=st.text_input("Preferred categories",p["categories"])
        st.session_state.profile={"turnover":turnover,"experience":experience,"certifications":certifications,"categories":categories}
        st.divider()
        if st.button("Sign out",use_container_width=True):
            st.session_state.authenticated=False; st.session_state.user=None; st.rerun()
    return st.session_state.profile

def evaluate_bid(bid,p):
    req=[x.strip().lower() for x in str(bid["required_certifications"]).split(";") if x.strip()]
    certs=[x.strip().lower() for x in p["certifications"].split(",") if x.strip()]
    cats=[x.strip().lower() for x in p["categories"].split(",") if x.strip()]
    missing=[x for x in req if x not in certs]
    checks=[
      {"name":"Minimum turnover","status":"Met" if p["turnover"]>=float(bid["min_turnover"]) else "Unmet","detail":f"Required ₹{float(bid['min_turnover']):,.0f}; entered ₹{p['turnover']:,.0f}"},
      {"name":"Minimum experience","status":"Met" if p["experience"]>=int(bid["min_experience_years"]) else "Unmet","detail":f"Required {bid['min_experience_years']} years; entered {p['experience']} years"},
      {"name":"Certifications","status":"Met" if not missing else "Partially met","detail":"All required certifications available" if not missing else "Missing: "+", ".join(missing)},
      {"name":"Category match","status":"Met" if str(bid["category"]).lower() in cats else "Review","detail":f"Bid category: {bid['category']}"}]
    w={"Met":1,"Partially met":.5,"Review":.5,"Unmet":0}
    score=round(sum(w[c["status"]] for c in checks)/len(checks)*100)
    eligibility="Eligible" if score>=85 else "Conditionally eligible" if score>=60 else "Not eligible"
    return score,eligibility,checks

def dashboard():
    p=supplier_profile(); bids=load_bids()
    st.title("📊 Bidder Dashboard")
    st.caption(f"Welcome, {st.session_state.user['name']} — {st.session_state.user['email']}")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Active bids",len(bids)); c2.metric("Closing in November",int(bids["closing_date"].str.startswith("2026-11").sum()))
    c3.metric("Experience",f"{p['experience']} years"); c4.metric("Turnover",f"₹{p['turnover']:,.0f}")
    st.divider(); st.subheader("Available tenders")
    s,d,cat=st.columns([2,1,1])
    search=s.text_input("Search title, department, or category")
    departments=["All departments"]+sorted(bids["department"].unique()); categories=["All categories"]+sorted(bids["category"].unique())
    dept=d.selectbox("Department",departments); category=cat.selectbox("Category",categories)
    f=bids.copy()
    if search: f=f[f["title"].str.contains(search,case=False,na=False)|f["department"].str.contains(search,case=False,na=False)|f["category"].str.contains(search,case=False,na=False)]
    if dept!="All departments": f=f[f["department"]==dept]
    if category!="All categories": f=f[f["category"]==category]
    st.dataframe(f[["bid_id","title","department","closing_date","bid_amount","category"]],use_container_width=True,hide_index=True)
    st.divider(); st.subheader("Analyze and submit documents")
    options=f["bid_id"]+" — "+f["title"]; selected=st.selectbox("Select a bid",options)
    bid_id=selected.split(" — ")[0]; bid=bids[bids["bid_id"]==bid_id].iloc[0]
    score,eligibility,checks=evaluate_bid(bid,p)
    with st.container(border=True):
        a,b,c=st.columns([4,1.2,1.2])
        with a:
            st.markdown(f"### {bid['title']}")
            st.write(f"**Bid ID:** {bid['bid_id']} | **Department:** {bid['department']}")
            st.write(f"**Category:** {bid['category']} | **Value:** ₹{float(bid['bid_amount']):,.0f}")
            st.write(f"**Closing:** {bid['closing_date']}")
        with b: st.metric("Trust score",f"{score}/100"); st.write(f"**{eligibility}**")
        with c:
            days=(datetime.strptime(str(bid['closing_date']),"%Y-%m-%d").date()-date.today()).days
            st.metric("Days remaining",max(days,0))
        st.markdown("#### Eligibility checks")
        for x in checks:
            icon={"Met":"✅","Partially met":"🟡","Review":"🔍","Unmet":"❌"}[x["status"]]
            st.markdown(f"- {icon} **{x['name']}** — {x['status']}. {x['detail']}")
    st.markdown("#### Upload bid documents")
    docs=st.file_uploader("Upload supporting documents",type=["pdf","docx","jpg","jpeg","png","xlsx","csv"],accept_multiple_files=True)
    required={"Company registration":["registration","incorporation","company"],"GST certificate":["gst"],"Turnover certificate":["turnover","financial","balance"],"Experience certificate":["experience","work","completion"],"Technical specification sheet":["technical","specification","catalog"]}
    names=[x.name.lower() for x in docs] if docs else []
    status=[{"Document":k,"Status":"Uploaded" if any(any(y in n for y in v) for n in names) else "Pending"} for k,v in required.items()]
    st.dataframe(pd.DataFrame(status),use_container_width=True,hide_index=True)
    if docs:
        saved=[]
        for doc in docs:
            safe=re.sub(r"[^A-Za-z0-9_.-]","_",doc.name)
            path=os.path.join(UPLOAD_DIR,f"{st.session_state.user['email'].replace('@','_')}__{bid_id}__{safe}")
            with open(path,"wb") as out: out.write(doc.getbuffer())
            saved.append(doc.name)
        st.success(f"Uploaded {len(saved)} document(s): "+", ".join(saved))
    else: st.info("Upload required documents to complete submission.")
    pending=[x["Document"] for x in status if x["Status"]=="Pending"]
    if st.button("Submit bid",type="primary",use_container_width=True):
        if pending: st.error("Cannot submit. Pending: "+", ".join(pending))
        elif eligibility=="Not eligible": st.error("Cannot submit. Mandatory eligibility requirements are unmet.")
        else: st.success("Bid submitted successfully for review.")
    st.divider(); st.subheader("Payment SLA milestone checklist")
    for stage,status,due in [("Delivered","Completed","2026-10-12"),("Accepted","Completed","2026-10-18"),("Invoice raised","Completed","2026-10-20"),("Payment due","Pending","2026-11-19")]:
        st.markdown(f"- {'✅' if status=='Completed' else '⏳'} **{stage}** — {status} — due {due}")

if not st.session_state.authenticated: login_signup()
else: dashboard()
