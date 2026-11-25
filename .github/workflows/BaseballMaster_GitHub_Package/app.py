# -*- coding: utf-8 -*-
"""BASEBALL MASTER web edition - Streamlit."""
import csv
import io
import urllib.request
import pandas as pd
import streamlit as st
from baseball_content import HISTORY, RULES, TECHNIQUES, GLOSSARY, TEAMS, AWARD_LABELS, AWARD_START, ALL_TIME

st.set_page_config(page_title="BASEBALL MASTER | MLB 야구 도감", page_icon="⚾", layout="wide")
BASE_URL = "https://raw.githubusercontent.com/cbwinslow/lahman-database-csv/main/data/"
FILES = ["AwardsPlayers.csv", "People.csv", "Batting.csv", "Pitching.csv"]
NAVY = "#102A43"

st.markdown(f"""
<style>
.stApp {{ background: #f3f7fb; }}
[data-testid="stHeader"] {{ background: rgba(243,247,251,.9); }}
.hero {{ background: linear-gradient(115deg,{NAVY},#1769aa); color:white; padding:1.5rem 1.8rem; border-radius:16px; margin-bottom:1rem; }}
.hero h1 {{ color:white; margin:0; }}
.hero p {{ color:#d9e8f5; margin:.45rem 0 0 0; }}
div[data-testid="stMetric"] {{ background:white; border:1px solid #dbe6ef; padding:14px; border-radius:12px; }}
section[data-testid="stSidebar"] {{ background:#eaf3fa; }}
</style>
<div class="hero"><h1>⚾ BASEBALL MASTER</h1><p>메이저리그 역사 · 규칙 · 기술 · 기록 · 연도별 수상자 도감</p></div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400, show_spinner=False)
def load_csv(filename):
    req=urllib.request.Request(BASE_URL+filename, headers={"User-Agent":"BaseballMaster/1.0"})
    with urllib.request.urlopen(req, timeout=40) as response:
        raw=response.read()
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", low_memory=False).fillna("")

@st.cache_data(ttl=86400, show_spinner=False)
def load_all():
    awards=load_csv("AwardsPlayers.csv")
    people=load_csv("People.csv")
    batting=load_csv("Batting.csv")
    pitching=load_csv("Pitching.csv")
    pmap={str(r.playerID): " ".join(x for x in [str(r.get("nameFirst", "")).strip(),str(r.get("nameLast", "")).strip()] if x) for _,r in people.iterrows()}
    return awards, pmap, batting, pitching

with st.sidebar:
    st.title("도감 메뉴")
    page=st.radio("페이지 선택", ["홈", "야구 역사", "기술·규칙", "연도별 수상 기록", "시즌 기록왕", "기록 용어", "MLB 구단 도감"])
    st.divider()
    st.caption("데이터 출처")
    st.markdown("[MLB 공식 Awards](https://www.mlb.com/awards)")
    st.markdown("[SABR Lahman Database](https://sabr.org/lahman-database/)")

if page == "홈":
    st.subheader("메이저리그를 한눈에 살펴보는 야구 백과사전")
    st.write("야구의 역사부터 투구·타격 기술, 시즌별 타이틀, 명예로운 수상 기록까지 탐색하세요.")
    a,b,c,d=st.columns(4)
    for col, title, desc in zip([a,b,c,d],["역사","기술","수상","기록"],["프로 리그부터 현대 MLB까지","구종·타격·수비·경기 규칙","MVP·사이영상·골드글러브","홈런·승리·타율·탈삼진"]):
        with col:
            st.markdown(f"**{title}**")
            st.caption(desc)
    st.subheader("MLB 역대 주요 기록")
    st.dataframe(pd.DataFrame(ALL_TIME,columns=["기록","선수","수치","설명"]),use_container_width=True,hide_index=True)
    st.info("리그 구성·시대·기록 집계 범위에 따라 일부 역사적 기록은 비교 기준이 다를 수 있습니다.")

elif page == "야구 역사":
    st.subheader("MLB 역사")
    for title, body in HISTORY:
        with st.expander(title, expanded=True): st.write(body)

elif page == "기술·규칙":
    st.subheader("야구 기술")
    for title, body in TECHNIQUES:
        with st.expander(title): st.write(body)
    st.subheader("경기 규칙")
    for title, body in RULES:
        with st.expander(title): st.write(body)

elif page == "연도별 수상 기록":
    st.subheader("연도별 개인 수상자")
    st.caption("선택한 상과 연도, 리그에 해당하는 수상자를 표시합니다. 데이터베이스에 수록된 시즌과 분류 기준을 따릅니다.")
    try:
        with st.spinner("수상·선수 데이터를 불러오는 중입니다. 최초 접속에는 시간이 걸릴 수 있습니다."):
            awards, people, batting, pitching=load_all()
        awards=awards.copy()
        awards["수상"] = awards["awardID"].map(AWARD_LABELS).fillna(awards["awardID"])
        awards["선수"] = awards["playerID"].astype(str).map(people).fillna(awards["playerID"])
        years=sorted([str(x) for x in awards["yearID"].unique() if str(x).isdigit()],reverse=True)
        c1,c2,c3=st.columns(3)
        with c1: selected=st.selectbox("수상 종류",["전체"]+list(AWARD_LABELS.values()))
        with c2: year=st.selectbox("연도",["전체"]+years)
        with c3: league=st.selectbox("리그",["전체","AL","NL","ML"])
        filtered=awards
        if selected!="전체": filtered=filtered[filtered["수상"]==selected]
        if year!="전체": filtered=filtered[filtered["yearID"].astype(str)==year]
        if league!="전체": filtered=filtered[filtered["lgID"].astype(str)==league]
        cols=[c for c in ["yearID","수상","lgID","선수","notes"] if c in filtered.columns]
        filtered=filtered[cols].rename(columns={"yearID":"연도","lgID":"리그","notes":"비고 / 포지션"}).sort_values("연도",ascending=False)
        st.metric("검색 결과",f"{len(filtered):,}건")
        st.dataframe(filtered,use_container_width=True,hide_index=True,height=520)
        if selected in AWARD_START: st.caption(AWARD_START[selected])
    except Exception as e:
        st.error(f"온라인 데이터 연결에 실패했습니다: {e}")
        st.info("네트워크 연결을 확인한 뒤 페이지를 새로고침해 주세요. 역사·규칙·구단 도감은 데이터 연결 없이도 볼 수 있습니다.")

elif page == "시즌 기록왕":
    st.subheader("시즌별 타이틀 리더")
    st.caption("홈런·다승·타율·탈삼진의 시즌별 리그 1위를 계산합니다.")
    try:
        with st.spinner("시즌 기록 데이터를 불러오는 중입니다."):
            awards, people, batting, pitching=load_all()
        c1,c2=st.columns(2)
        with c1: kind=st.selectbox("기록",["홈런","다승","타율","탈삼진"])
        with c2: year=st.selectbox("연도",["전체"]+sorted(set((batting if kind in ["홈런","타율"] else pitching)["yearID"].astype(str)),reverse=True))
        source=batting if kind in ["홈런","타율"] else pitching
        source=source[source["lgID"].isin(["AL","NL"])].copy()
        source=source[source["yearID"].astype(str).str.isnumeric()]
        if year!="전체": source=source[source["yearID"].astype(str)==year]
        metric_col={"홈런":"HR","다승":"W","타율":"H","탈삼진":"SO"}[kind]
        source[metric_col]=pd.to_numeric(source[metric_col],errors="coerce").fillna(0)
        if kind=="타율":
            source["AB"]=pd.to_numeric(source["AB"],errors="coerce").fillna(0)
            grouped=source.groupby(["yearID","lgID","playerID"],as_index=False).agg(H=("H","sum"),AB=("AB","sum"),teamID=("teamID","last"))
            grouped=grouped[grouped["AB"]>=100]
            grouped["기록"]=grouped["H"]/grouped["AB"]
        else:
            grouped=source.groupby(["yearID","lgID","playerID"],as_index=False).agg(기록=(metric_col,"sum"),teamID=("teamID","last"))
        if len(grouped):
            maxima=grouped.groupby(["yearID","lgID"])["기록"].transform("max")
            leaders=grouped[grouped["기록"]==maxima].copy()
            leaders["선수"]=leaders["playerID"].astype(str).map(people).fillna(leaders["playerID"])
            leaders=leaders.rename(columns={"yearID":"연도","lgID":"리그","teamID":"팀"})
            if kind=="타율": leaders["기록"]=leaders["기록"].map(lambda x:f"{x:.3f}".replace("0.","."))
            st.dataframe(leaders[["연도","리그","선수","팀","기록"]].sort_values("연도",ascending=False),use_container_width=True,hide_index=True,height=520)
        else: st.warning("선택한 조건에 해당하는 기록이 없습니다.")
        if kind=="타율": st.caption("타율은 데이터 비교용으로 100타수 이상을 대상으로 계산한 참고값이며, 공식 타격왕 규정타석과 다를 수 있습니다.")
        else: st.caption("동률 기록은 모두 표시합니다. 다승·탈삼진·홈런은 정규시즌 리그별 합산 기록입니다.")
    except Exception as e:
        st.error(f"온라인 데이터 연결에 실패했습니다: {e}")

elif page == "기록 용어":
    st.subheader("야구 기록 용어 사전")
    st.dataframe(pd.DataFrame(GLOSSARY,columns=["영문 약어","한국어","설명"]),use_container_width=True,hide_index=True)

elif page == "MLB 구단 도감":
    st.subheader("MLB 30개 구단 도감")
    c1,c2=st.columns(2)
    with c1: lg=st.selectbox("리그",["전체","AL","NL"])
    with c2: div=st.selectbox("지구",["전체","동부","중부","서부"])
    teams=[t for t in TEAMS if (lg=="전체" or t[0]==lg) and (div=="전체" or t[1]==div)]
    labels=[f"{t[4]} | {t[2]}" for t in teams]
    if teams:
        chosen=st.selectbox("구단 선택",labels)
        t=teams[labels.index(chosen)]
        league,division,ko,en,abbr,short,founded,city,c1,c2,symbol,uniform=t
        left,right=st.columns([1,2])
        with left:
            st.markdown(f"<div style='background:{c1};color:white;padding:24px;border-radius:12px;text-align:center;font-size:30px;font-weight:700'>{abbr}</div>",unsafe_allow_html=True)
            st.markdown(f"<div style='display:flex;gap:8px;margin-top:10px'><div style='background:{c1};height:22px;flex:1;border-radius:5px'></div><div style='background:{c2};height:22px;flex:1;border-radius:5px'></div></div>",unsafe_allow_html=True)
            st.caption(f"대표 색상: {c1} / {c2}")
        with right:
            st.markdown(f"### {ko}")
            st.write(f"{en} · {league} 리그 {division}지구")
            st.write(f"**한글 약칭:** {short}")
            st.write(f"**창단/프랜차이즈 시작:** {founded}년")
            st.write(f"**연고지:** {city}")
            st.write(f"**팀 심볼:** {symbol}")
            st.write(f"**유니폼 특징:** {uniform}")
    st.caption("창단 연도는 현재 도시 정착일이 아닌 프랜차이즈 기원 기준입니다.")

st.divider()
st.caption("BASEBALL MASTER · 교육·참고용 도감 | Lahman 데이터베이스는 별도 데이터 출처의 수록 범위와 기준을 따릅니다.")
