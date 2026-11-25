# -*- coding: utf-8 -*-
"""
BASEBALL MASTER - MLB 야구 도감
Python 3.10+ / Tkinter (표준 라이브러리만 사용)
역사·규칙·기술·선수 기록·연도별 수상자 탐색 프로그램
데이터: SABR Lahman Baseball Database (1871-2025) 비공식 GitHub 미러에서 실행 시 다운로드
"""

import csv
import io
import os
import sys
import threading
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "BASEBALL MASTER | MLB 야구 도감"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__)), "baseball_data")
BASE_URL = "https://raw.githubusercontent.com/cbwinslow/lahman-database-csv/main/data/"
FILES = ["AwardsPlayers.csv", "People.csv", "Batting.csv", "Pitching.csv"]

COLORS = {
    "navy": "#102A43", "blue": "#1769AA", "light": "#EAF3FA",
    "white": "#FFFFFF", "ink": "#172B4D", "muted": "#627D98",
    "gold": "#E0A526", "green": "#2D8659"
}

HISTORY = [
    ("야구의 기원", "야구는 19세기 북미에서 여러 배트·볼 경기의 영향을 받으며 발전했다. 1845년 알렉산더 카트라이트가 정리한 니커보커 규칙은 현대 야구 규칙의 형성에 중요한 역할을 했다. 다만 야구의 기원을 한 사람이나 한 날짜로 단정하기는 어렵다."),
    ("프로야구의 성장", "미국에서는 19세기 후반 프로 구단과 리그가 성장했다. 내셔널리그는 1876년에 출범했고, 아메리칸리그는 1901년 메이저리그로 자리 잡았다. 두 리그는 1903년부터 월드시리즈를 통해 챔피언을 가리기 시작했다."),
    ("현대 MLB", "MLB는 아메리칸리그(AL)와 내셔널리그(NL)로 구성된다. 지명타자 제도, 와일드카드, 비디오 판독 등 경기 방식과 운영 제도는 시대에 따라 변화해 왔다."),
    ("기록의 의미", "야구는 타율, 출루율, 장타율, OPS, 평균자책점(ERA), WHIP, WAR 등 다양한 기록으로 선수의 기여도를 살핀다. 시대와 구장, 리그 환경이 다르므로 단순 수치 비교에는 맥락이 필요하다.")
]

RULES = [
    ("경기 기본", "한 팀은 수비 때 9명의 선수를 배치한다. 공격 팀은 타순에 따라 타격하고, 수비 팀은 아웃 3개를 잡으면 공수 교대가 이루어진다. 정규 경기는 보통 9이닝으로 진행된다."),
    ("스트라이크와 볼", "타자가 스윙했으나 맞히지 못하면 스트라이크다. 스트라이크존을 통과한 공을 치지 않아도 스트라이크가 선언된다. 스트라이크존 밖의 공을 타자가 치지 않으면 볼이다. 볼 4개면 볼넷, 스트라이크 3개면 삼진이다(파울 처리 등 예외 규정 존재)."),
    ("득점과 주루", "타자는 안타·볼넷·실책 등으로 출루할 수 있다. 1루, 2루, 3루를 거쳐 홈을 밟으면 1점을 얻는다. 주자는 투수의 투구 동작과 수비 상황을 읽고 도루를 시도할 수 있다."),
    ("수비 포지션", "투수(P)는 공을 던지고, 포수(C)는 투구를 받고 홈을 지킨다. 내야수는 1루수(1B), 2루수(2B), 3루수(3B), 유격수(SS)다. 외야수는 좌익수(LF), 중견수(CF), 우익수(RF)다."),
    ("지명타자", "지명타자(DH)는 투수를 대신해 타격하는 역할이다. MLB는 2022년부터 양 리그에 지명타자 제도를 적용한다.")
]

TECHNIQUES = [
    ("투구: 포심 패스트볼", "회전과 구속을 활용해 빠르게 던지는 기본 구종. 높은 회전 효율과 릴리스 포인트에 따라 타자에게 떠오르는 듯한 인상을 줄 수 있다."),
    ("투구: 투심·싱커", "포심보다 움직임을 강조하는 빠른 공. 팔 쪽 움직임과 가라앉는 궤적으로 땅볼을 유도하는 데 쓰인다."),
    ("투구: 커브", "큰 낙차와 느린 속도 차이를 활용하는 변화구. 회전축과 릴리스에 따라 궤적이 달라진다."),
    ("투구: 슬라이더·커터", "슬라이더는 옆 방향 움직임과 속도 차이를 활용한다. 커터는 패스트볼에 가까운 속도로 짧게 움직이는 구종이다."),
    ("타격: 준비 자세", "균형 잡힌 스탠스와 편안한 그립을 유지하고, 투수의 릴리스와 공의 궤적을 관찰한다."),
    ("타격: 스윙", "하체 회전과 체중 이동을 이용해 배트 스피드를 만든다. 공을 오래 보고 적절한 타이밍에 배트 중심으로 맞히는 것이 중요하다."),
    ("수비: 풋워크", "낮은 자세와 첫 발 반응이 중요하다. 타구 방향을 빠르게 판단하고 공의 바운드에 맞춰 글러브를 내민다."),
    ("수비: 송구", "송구 전 발과 어깨를 목표 방향으로 정렬하고, 상황에 맞는 릴리스와 송구 강도를 선택한다.")
]

GLOSSARY = [
    ("AVG", "타율", "안타 ÷ 타수. 타자가 타수에서 안타를 만들어 낸 비율."),
    ("OBP", "출루율", "안타·볼넷·몸에 맞는 공 등을 반영해 얼마나 자주 출루했는지 나타낸다."),
    ("SLG", "장타율", "총루타 ÷ 타수. 단타와 장타의 가치를 루타 수로 반영한다."),
    ("OPS", "출루율 + 장타율", "타격 생산성을 간단히 비교할 때 널리 쓰는 지표."),
    ("HR", "홈런", "타자가 친 타구로 타자와 모든 주자가 홈까지 들어오는 안타."),
    ("RBI", "타점", "타자의 타격 결과 등으로 주자가 득점했을 때 타자에게 기록되는 점수."),
    ("W", "승리", "투수의 승리 기록. 선발·구원 투수의 승리 인정 조건은 규정에 따른다."),
    ("ERA", "평균자책점", "자책점 × 9 ÷ 투구 이닝. 투수의 9이닝당 자책점."),
    ("WHIP", "이닝당 출루 허용", "(볼넷 + 피안타) ÷ 투구 이닝."),
    ("SO / K", "탈삼진", "투수가 삼진으로 타자를 아웃시킨 횟수."),
    ("SV", "세이브", "구원 투수가 리드를 지키며 경기를 마무리했을 때 주어지는 기록."),
    ("WAR", "대체 선수 대비 승리 기여", "대체 수준 선수와 비교해 팀에 얼마나 많은 승리를 더했는지 추정하는 종합 지표. 산출 방식에 따라 값이 다르다.")
]


# MLB 30개 구단 도감: 창단 연도는 현재 도시 정착일이 아닌 프랜차이즈 기원 기준
TEAMS = [
    # AL East
    ("AL", "동부", "볼티모어 오리올스", "Baltimore Orioles", "BAL", "볼티모어", 1901, "볼티모어", "#DF4601", "#000000", "새 모자를 쓴 오리올", "홈: 흰색 바탕·주황/검정 포인트 | 원정: 회색 바탕·검정/주황 포인트"),
    ("AL", "동부", "보스턴 레드삭스", "Boston Red Sox", "BOS", "보스턴", 1901, "보스턴", "#BD3039", "#0C2340", "빨간 양말 한 쌍", "홈: 흰색 바탕·빨간 글씨 | 원정: 회색 바탕·빨강/네이비 포인트"),
    ("AL", "동부", "뉴욕 양키스", "New York Yankees", "NYY", "양키스", 1901, "뉴욕 브롱크스", "#003087", "#E4002B", "인터로킹 NY 모노그램", "홈: 흰색 바탕·네이비 핀스트라이프 | 원정: 회색 바탕·네이비 글씨"),
    ("AL", "동부", "탬파베이 레이스", "Tampa Bay Rays", "TBR", "탬파베이", 1998, "세인트피터즈버그", "#092C5C", "#8FBCE6", "가운데 노란 태양빛이 있는 Rays 로고", "홈: 흰색 바탕·네이비/하늘색 | 원정: 회색 바탕·네이비 포인트"),
    ("AL", "동부", "토론토 블루제이스", "Toronto Blue Jays", "TOR", "토론토", 1977, "토론토", "#134A8E", "#1D2D5C", "파란어치와 붉은 단풍잎", "홈: 흰색 바탕·파랑 글씨 | 원정: 회색 바탕·네이비/블루 포인트"),
    # AL Central
    ("AL", "중부", "시카고 화이트삭스", "Chicago White Sox", "CWS", "시카고 화이트삭스", 1901, "시카고", "#27251F", "#C4CED4", "고딕체로 겹친 SOX", "홈: 흰색 또는 검정 바탕·블랙/실버 | 원정: 회색 바탕·검정 글씨"),
    ("AL", "중부", "클리블랜드 가디언스", "Cleveland Guardians", "CLE", "클리블랜드", 1901, "클리블랜드", "#00385D", "#E50022", "가디언스 오브 트래픽 조각상에서 딴 날개 달린 G", "홈: 흰색 바탕·네이비/빨강 | 원정: 회색 바탕·네이비 포인트"),
    ("AL", "중부", "디트로이트 타이거스", "Detroit Tigers", "DET", "디트로이트", 1901, "디트로이트", "#0C2340", "#FA4616", "고전적인 고딕체 Old English D", "홈: 흰색 바탕·네이비 Old English D | 원정: 회색 바탕·네이비 글씨"),
    ("AL", "중부", "캔자스시티 로열스", "Kansas City Royals", "KCR", "캔자스시티", 1969, "캔자스시티", "#004687", "#BD9B60", "왕관이 얹힌 방패형 KC", "홈: 흰색 바탕·로열 블루 | 원정: 회색 바탕·블루 글씨"),
    ("AL", "중부", "미네소타 트윈스", "Minnesota Twins", "MIN", "미네소타", 1901, "미니애폴리스", "#002B5C", "#D31145", "야구공 안의 TC 모노그램", "홈: 흰색 바탕·네이비/레드 | 원정: 회색 바탕·네이비 포인트"),
    # AL West
    ("AL", "서부", "애슬레틱스", "Athletics", "ATH", "애슬레틱스", 1901, "웨스트 새크라멘토", "#003831", "#EFB21E", "금색 테두리의 A's 모노그램", "홈: 흰색 바탕·그린/골드 | 원정: 회색 바탕·그린 포인트"),
    ("AL", "서부", "휴스턴 애스트로스", "Houston Astros", "HOU", "휴스턴", 1962, "휴스턴", "#002D62", "#EB6E1F", "오렌지색 별과 H", "홈: 흰색 바탕·네이비 글씨 | 원정: 회색 바탕·네이비/오렌지"),
    ("AL", "서부", "로스앤젤레스 에인절스", "Los Angeles Angels", "LAA", "LA 에인절스", 1961, "애너하임", "#BA0021", "#003263", "후광이 얹힌 대문자 A", "홈: 흰색 바탕·레드 글씨 | 원정: 회색 바탕·레드/네이비"),
    ("AL", "서부", "시애틀 매리너스", "Seattle Mariners", "SEA", "시애틀", 1977, "시애틀", "#0C2C56", "#005C5C", "나침반 모양의 북극성 S", "홈: 흰색 바탕·네이비/틸 | 원정: 회색 바탕·네이비 포인트"),
    ("AL", "서부", "텍사스 레인저스", "Texas Rangers", "TEX", "텍사스", 1961, "알링턴", "#003278", "#C0111F", "별이 들어간 원형 T 배지", "홈: 흰색 바탕·블루/레드 | 원정: 회색 바탕·블루 글씨"),
    # NL East
    ("NL", "동부", "애틀랜타 브레이브스", "Atlanta Braves", "ATL", "애틀랜타", 1871, "애틀랜타", "#CE1141", "#13274F", "스크립트 A와 토마호크", "홈: 흰색 바탕·네이비/레드 | 원정: 회색 바탕·네이비/레드"),
    ("NL", "동부", "마이애미 말린스", "Miami Marlins", "MIA", "마이애미", 1993, "마이애미", "#00A3E0", "#000000", "청록색 말린(돛새치) 물고기", "홈: 흰색 바탕·블랙/아쿠아 | 원정: 회색 바탕·아쿠아 포인트"),
    ("NL", "동부", "뉴욕 메츠", "New York Mets", "NYM", "뉴욕", 1962, "뉴욕 퀸스", "#002D72", "#FF5910", "뉴욕 스카이라인과 주황색 야구공 실밥", "홈: 흰색 바탕·블루/오렌지 | 원정: 회색 바탕·블루 글씨"),
    ("NL", "동부", "필라델피아 필리스", "Philadelphia Phillies", "PHI", "필라델피아", 1883, "필라델피아", "#E81828", "#002D72", "파란 별이 들어간 Phillies 워드마크", "홈: 흰색 바탕·레드 핀스트라이프 | 원정: 회색 바탕·레드 글씨"),
    ("NL", "동부", "워싱턴 내셔널스", "Washington Nationals", "WSH", "워싱턴", 1969, "워싱턴 D.C.", "#AB0003", "#14225A", "원형 안의 스크립트 W", "홈: 흰색 바탕·레드 글씨 | 원정: 회색 바탕·네이비/레드"),
    # NL Central
    ("NL", "중부", "시카고 컵스", "Chicago Cubs", "CHC", "시카고 컵스", 1876, "시카고", "#0E3386", "#CC3433", "빨간 C 안의 Cubs 글자", "홈: 흰색 바탕·블루/레드 | 원정: 회색 바탕·블루 글씨"),
    ("NL", "중부", "신시내티 레즈", "Cincinnati Reds", "CIN", "신시내티", 1882, "신시내티", "#C6011F", "#000000", "흰색 C가 들어간 빨간 페넌트", "홈: 흰색 바탕·레드 핀스트라이프 | 원정: 회색 바탕·레드 글씨"),
    ("NL", "중부", "밀워키 브루어스", "Milwaukee Brewers", "MIL", "밀워키", 1969, "밀워키", "#12284B", "#FFC52F", "야구 글러브 안에 공을 숨긴 MB 로고", "홈: 흰색 바탕·네이비/골드 | 원정: 회색 바탕·네이비 글씨"),
    ("NL", "중부", "피츠버그 파이리츠", "Pittsburgh Pirates", "PIT", "피츠버그", 1882, "피츠버그", "#27251F", "#FDBB30", "해적 모자와 P 모노그램", "홈: 흰색 바탕·검정/골드 | 원정: 회색 바탕·검정 글씨"),
    ("NL", "중부", "세인트루이스 카디널스", "St. Louis Cardinals", "STL", "세인트루이스", 1882, "세인트루이스", "#C41E3A", "#0C2340", "방망이에 앉은 두 마리 추기새와 STL", "홈: 흰색 바탕·레드 글씨 | 원정: 회색 바탕·레드/네이비"),
    # NL West
    ("NL", "서부", "애리조나 다이아몬드백스", "Arizona Diamondbacks", "ARI", "애리조나", 1998, "피닉스", "#A71930", "#E3D4AD", "방울뱀 머리와 A 모노그램", "홈: 흰색 바탕·세도나 레드/검정 | 원정: 회색 바탕·레드 포인트"),
    ("NL", "서부", "콜로라도 로키스", "Colorado Rockies", "COL", "콜로라도", 1993, "덴버", "#333366", "#C4CED4", "산봉우리 실루엣과 CR 모노그램", "홈: 흰색 바탕·보라/검정 | 원정: 회색 바탕·보라 글씨"),
    ("NL", "서부", "로스앤젤레스 다저스", "Los Angeles Dodgers", "LAD", "LA 다저스", 1883, "로스앤젤레스", "#005A9C", "#EF3E42", "빨간 야구공 궤적이 있는 스크립트 Dodgers", "홈: 흰색 바탕·다저 블루 글씨 | 원정: 회색 바탕·블루 글씨"),
    ("NL", "서부", "샌디에이고 파드리스", "San Diego Padres", "SDP", "샌디에이고", 1969, "샌디에이고", "#2F241D", "#FFC425", "SD 모노그램", "홈: 흰색 바탕·브라운/골드 | 원정: 회색 바탕·브라운 글씨"),
    ("NL", "서부", "샌프란시스코 자이언츠", "San Francisco Giants", "SFG", "샌프란시스코", 1883, "샌프란시스코", "#FD5A1E", "#27251F", "오렌지색 SF 모노그램", "홈: 크림색 바탕·오렌지/블랙 | 원정: 회색 바탕·블랙 글씨"),
]

AWARD_LABELS = {
    "Most Valuable Player": "MVP",
    "Cy Young Award": "사이영상",
    "Rookie of the Year": "신인왕",
    "Gold Glove": "골드글러브",
    "Silver Slugger": "실버슬러거",
    "All-Star Game MVP": "올스타전 MVP",
    "Hank Aaron Award": "행크 애런상",
    "Comeback Player of the Year": "올해의 재기 선수상",
    "Manager of the Year": "올해의 감독상"
}
AWARD_START = {
    "MVP": "1931년부터 현재 형식의 AL/NL MVP. 그 이전에는 다른 형태의 MVP 상이 존재.",
    "사이영상": "1956년 시작. 1967년부터 AL과 NL에서 각각 수상.",
    "신인왕": "1947년 시작. 1947~1948년 단일 수상, 1949년부터 AL/NL 각각 수상.",
    "골드글러브": "1957년 시작. 포지션별 수상자 기록.",
    "실버슬러거": "1980년 시작. 포지션별 공격상.",
}

ALL_TIME = [
    ("통산 홈런", "배리 본즈", "762", "MLB 통산 홈런 1위"),
    ("통산 승리", "사이 영", "511", "MLB 통산 승리 1위"),
    ("통산 탈삼진", "놀란 라이언", "5,714", "MLB 통산 탈삼진 1위"),
    ("통산 도루", "리키 헨더슨", "1,406", "MLB 통산 도루 1위"),
    ("단일 시즌 홈런", "배리 본즈", "73 (2001)", "현대 MLB 단일 시즌 기록"),
    ("통산 안타", "피트 로즈", "4,256", "MLB 통산 안타 1위"),
    ("통산 타율", "타이 콥", ".366", "MLB 통산 타율 대표 기록(기록 범위·공식 집계 기준 참고)")
]

def fetch_csv(name):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path) and os.path.getsize(path) > 100:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    url = BASE_URL + name
    req = urllib.request.Request(url, headers={"User-Agent": "BaseballMaster/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    with open(path, "wb") as f:
        f.write(raw)
    text = raw.decode("utf-8-sig", errors="replace")
    return list(csv.DictReader(io.StringIO(text)))

def safe_int(value, default=0):
    try:
        return int(float(value or 0))
    except (ValueError, TypeError):
        return default

class BaseballMaster:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x760")
        self.root.minsize(920, 620)
        self.root.configure(bg=COLORS["light"])
        self.awards = []
        self.people = {}
        self.batting = []
        self.pitching = []
        self.data_ready = False
        self._style()
        self._build()
        self.root.after(700, self.load_data_async)

    def _style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=27, font=("맑은 고딕", 9), background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("맑은 고딕", 9, "bold"), background="#D8E8F5", foreground=COLORS["navy"])
        style.configure("TNotebook.Tab", padding=(14, 8), font=("맑은 고딕", 9, "bold"))
        style.configure("TButton", font=("맑은 고딕", 9), padding=6)

    def _build(self):
        header = tk.Frame(self.root, bg=COLORS["navy"], height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="⚾  BASEBALL MASTER", bg=COLORS["navy"], fg="white",
                 font=("맑은 고딕", 22, "bold")).pack(anchor="w", padx=22, pady=(12, 0))
        tk.Label(header, text="메이저리그 역사 · 규칙 · 기술 · 기록 · 연도별 수상자 도감",
                 bg=COLORS["navy"], fg="#C9DDEE", font=("맑은 고딕", 10)).pack(anchor="w", padx=25)

        self.status = tk.StringVar(value="역사·규칙 자료 준비 완료 | 연도별 수상자와 기록 통계 데이터 연결 중...")
        tk.Label(self.root, textvariable=self.status, bg=COLORS["light"], fg=COLORS["muted"],
                 anchor="w", font=("맑은 고딕", 9)).pack(fill="x", padx=18, pady=(8, 2))

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=14, pady=10)
        self.home_tab = ttk.Frame(self.nb)
        self.history_tab = ttk.Frame(self.nb)
        self.tech_tab = ttk.Frame(self.nb)
        self.award_tab = ttk.Frame(self.nb)
        self.leader_tab = ttk.Frame(self.nb)
        self.gloss_tab = ttk.Frame(self.nb)
        self.teams_tab = ttk.Frame(self.nb)
        self.nb.add(self.home_tab, text="홈")
        self.nb.add(self.history_tab, text="야구 역사")
        self.nb.add(self.tech_tab, text="기술·규칙")
        self.nb.add(self.award_tab, text="연도별 수상 기록")
        self.nb.add(self.leader_tab, text="시즌 기록왕")
        self.nb.add(self.gloss_tab, text="기록 용어")
        self.nb.add(self.teams_tab, text="MLB 구단 도감")

        self._home()
        self._text_page(self.history_tab, "MLB 역사", HISTORY)
        self._text_page(self.tech_tab, "야구 기술과 경기 규칙", TECHNIQUES + RULES)
        self._awards_page()
        self._leaders_page()
        self._glossary_page()
        self._teams_page()

        footer = tk.Frame(self.root, bg=COLORS["light"])
        footer.pack(fill="x", padx=16, pady=(0, 8))
        tk.Button(footer, text="MLB 공식 Awards", command=lambda: webbrowser.open("https://www.mlb.com/awards"),
                  bg=COLORS["blue"], fg="white", relief="flat").pack(side="left")
        tk.Button(footer, text="SABR Lahman 데이터 출처", command=lambda: webbrowser.open("https://sabr.org/lahman-database/"),
                  bg=COLORS["navy"], fg="white", relief="flat").pack(side="left", padx=8)
        tk.Label(footer, text="자료 기준: Lahman DB 1871–2025 · 네트워크 연결 시 최신 데이터 갱신",
                 bg=COLORS["light"], fg=COLORS["muted"], font=("맑은 고딕", 8)).pack(side="right")

    def _home(self):
        frame = self.home_tab
        hero = tk.Frame(frame, bg="#E7F1F8", padx=22, pady=20)
        hero.pack(fill="x", padx=18, pady=18)
        tk.Label(hero, text="메이저리그를 한눈에 살펴보는 야구 백과사전",
                 bg="#E7F1F8", fg=COLORS["navy"], font=("맑은 고딕", 19, "bold")).pack(anchor="w")
        tk.Label(hero, text="야구의 역사부터 투구·타격 기술, 시즌별 타이틀, 명예로운 수상 기록까지 탐색하세요.",
                 bg="#E7F1F8", fg=COLORS["ink"], font=("맑은 고딕", 10)).pack(anchor="w", pady=(8, 0))
        cards = [
            ("역사", "1870년대 프로 리그부터 현대 MLB까지"),
            ("기술", "구종·타격·수비·경기 규칙"),
            ("수상", "MVP·사이영상·골드글러브 등 연도별"),
            ("기록", "홈런·승리·타율·탈삼진 시즌 리더")
        ]
        grid = tk.Frame(frame, bg="white")
        grid.pack(fill="x", padx=18, pady=4)
        for i, (title, desc) in enumerate(cards):
            card = tk.Frame(grid, bg="white", highlightbackground="#D5E2EC", highlightthickness=1, padx=14, pady=14)
            card.grid(row=i//2, column=i%2, sticky="nsew", padx=7, pady=7)
            tk.Label(card, text=title, bg="white", fg=COLORS["blue"], font=("맑은 고딕", 13, "bold")).pack(anchor="w")
            tk.Label(card, text=desc, bg="white", fg=COLORS["ink"], font=("맑은 고딕", 9)).pack(anchor="w", pady=(5, 0))
        grid.columnconfigure(0, weight=1); grid.columnconfigure(1, weight=1)
        box = tk.LabelFrame(frame, text="MLB 역대 주요 기록", padx=10, pady=8, font=("맑은 고딕", 10, "bold"))
        box.pack(fill="both", expand=True, padx=18, pady=14)
        for category, player, record, note in ALL_TIME:
            tk.Label(box, text=f"• {category}: {player} — {record}  |  {note}",
                     anchor="w", font=("맑은 고딕", 9), fg=COLORS["ink"]).pack(fill="x", pady=3)
        tk.Label(frame, text="※ 리그 구성·시대·기록 집계 범위에 따라 일부 역사적 기록은 비교 기준이 다를 수 있습니다.",
                 fg=COLORS["muted"], font=("맑은 고딕", 8)).pack(anchor="w", padx=20, pady=(0, 10))

    def _text_page(self, tab, title, items):
        outer = ttk.Frame(tab, padding=14); outer.pack(fill="both", expand=True)
        tk.Label(outer, text=title, font=("맑은 고딕", 16, "bold"), fg=COLORS["navy"]).pack(anchor="w", pady=(0, 10))
        canvas = tk.Canvas(outer, bg="white", highlightthickness=0)
        scroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="white")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(1, width=e.width))
        for heading, body in items:
            block = tk.Frame(inner, bg="white", padx=16, pady=11)
            block.pack(fill="x", padx=8, pady=5)
            tk.Label(block, text=heading, bg="white", fg=COLORS["blue"], font=("맑은 고딕", 11, "bold")).pack(anchor="w")
            tk.Label(block, text=body, bg="white", fg=COLORS["ink"], font=("맑은 고딕", 9),
                     justify="left", wraplength=950).pack(anchor="w", pady=(5, 0))

    def _awards_page(self):
        outer = ttk.Frame(self.award_tab, padding=12); outer.pack(fill="both", expand=True)
        tk.Label(outer, text="연도별 개인 수상자", font=("맑은 고딕", 15, "bold"), fg=COLORS["navy"]).pack(anchor="w")
        tk.Label(outer, text="선택한 상과 연도, 리그에 해당하는 수상자를 표시합니다. 골드글러브는 포지션별 수상자를 포함합니다.",
                 font=("맑은 고딕", 9), fg=COLORS["muted"]).pack(anchor="w", pady=(4, 10))
        controls = ttk.Frame(outer); controls.pack(fill="x", pady=4)
        self.award_choice = tk.StringVar(value="전체")
        self.award_year = tk.StringVar(value="전체")
        self.award_league = tk.StringVar(value="전체")
        ttk.Label(controls, text="수상 종류").pack(side="left")
        self.award_combo = ttk.Combobox(controls, textvariable=self.award_choice, state="readonly", width=23,
                                        values=["전체"] + list(AWARD_LABELS.values()))
        self.award_combo.pack(side="left", padx=6)
        ttk.Label(controls, text="연도").pack(side="left", padx=(12, 0))
        self.year_combo = ttk.Combobox(controls, textvariable=self.award_year, state="readonly", width=10, values=["전체"])
        self.year_combo.pack(side="left", padx=6)
        ttk.Label(controls, text="리그").pack(side="left", padx=(12, 0))
        ttk.Combobox(controls, textvariable=self.award_league, state="readonly", width=10,
                     values=["전체", "AL", "NL", "ML"]).pack(side="left", padx=6)
        ttk.Button(controls, text="검색", command=self.filter_awards).pack(side="left", padx=8)
        cols = ("year", "award", "league", "player", "notes")
        self.award_tree = ttk.Treeview(outer, columns=cols, show="headings")
        names = {"year":"연도","award":"수상","league":"리그","player":"선수","notes":"비고 / 포지션"}
        widths = {"year":70,"award":160,"league":70,"player":220,"notes":180}
        for c in cols:
            self.award_tree.heading(c, text=names[c]); self.award_tree.column(c, width=widths[c], anchor="center")
        self.award_tree.pack(fill="both", expand=True, pady=8)
        self.award_note = tk.StringVar(value="데이터를 불러오는 중입니다. 첫 실행에는 인터넷 연결이 필요합니다.")
        tk.Label(outer, textvariable=self.award_note, fg=COLORS["muted"], font=("맑은 고딕", 8)).pack(anchor="w")
        self.award_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_awards())

    def _leaders_page(self):
        outer = ttk.Frame(self.leader_tab, padding=12); outer.pack(fill="both", expand=True)
        tk.Label(outer, text="시즌별 타이틀 리더", font=("맑은 고딕", 15, "bold"), fg=COLORS["navy"]).pack(anchor="w")
        tk.Label(outer, text="홈런·다승·타율·탈삼진의 시즌별 리그 1위를 계산합니다. 타격·투수 기록은 Lahman 정규시즌 데이터를 사용합니다.",
                 font=("맑은 고딕", 9), fg=COLORS["muted"]).pack(anchor="w", pady=(4, 10))
        bar = ttk.Frame(outer); bar.pack(fill="x")
        self.leader_type = tk.StringVar(value="홈런")
        ttk.Label(bar, text="기록").pack(side="left")
        ttk.Combobox(bar, textvariable=self.leader_type, state="readonly", width=12,
                     values=["홈런","다승","타율","탈삼진"]).pack(side="left", padx=6)
        self.leader_from = tk.StringVar(value="전체")
        ttk.Label(bar, text="연도").pack(side="left", padx=(12,0))
        self.leader_year = ttk.Combobox(bar, textvariable=self.leader_from, state="readonly", width=10, values=["전체"])
        self.leader_year.pack(side="left", padx=6)
        ttk.Button(bar, text="검색", command=self.show_leaders).pack(side="left", padx=8)
        self.leader_tree = ttk.Treeview(outer, columns=("year","league","player","team","value"), show="headings")
        for c, label, width in [("year","연도",80),("league","리그",80),("player","선수",220),("team","팀",150),("value","기록",120)]:
            self.leader_tree.heading(c,text=label); self.leader_tree.column(c,width=width,anchor="center")
        self.leader_tree.pack(fill="both",expand=True,pady=10)
        self.leader_note = tk.StringVar(value="데이터 로딩 후 검색할 수 있습니다.")
        tk.Label(outer,textvariable=self.leader_note,fg=COLORS["muted"],font=("맑은 고딕",8)).pack(anchor="w")

    def _glossary_page(self):
        outer = ttk.Frame(self.gloss_tab, padding=14); outer.pack(fill="both", expand=True)
        tk.Label(outer, text="야구 기록 용어 사전", font=("맑은 고딕", 15, "bold"), fg=COLORS["navy"]).pack(anchor="w", pady=(0, 10))
        tree = ttk.Treeview(outer, columns=("abbr","korean","meaning"), show="headings")
        for c, label, width in [("abbr","영문 약어",120),("korean","한국어",180),("meaning","설명",700)]:
            tree.heading(c,text=label); tree.column(c,width=width,anchor="w")
        for row in GLOSSARY: tree.insert("", "end", values=row)
        tree.pack(fill="both",expand=True)


    def _teams_page(self):
        outer = ttk.Frame(self.teams_tab, padding=12)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text="MLB 30개 구단 도감", font=("맑은 고딕", 16, "bold"), fg=COLORS["navy"]).pack(anchor="w")
        tk.Label(outer, text="리그·지구별 구단을 선택하면 창단 연도, 연고지, 유니폼, 팀 심볼과 대표 색상을 확인할 수 있습니다.",
                 font=("맑은 고딕", 9), fg=COLORS["muted"]).pack(anchor="w", pady=(3, 9))
        filters = ttk.Frame(outer); filters.pack(fill="x", pady=(0, 8))
        self.team_league = tk.StringVar(value="전체")
        self.team_division = tk.StringVar(value="전체")
        ttk.Label(filters, text="리그").pack(side="left")
        league_box = ttk.Combobox(filters, textvariable=self.team_league, state="readonly", width=9,
                                  values=["전체", "AL", "NL"])
        league_box.pack(side="left", padx=5)
        ttk.Label(filters, text="지구").pack(side="left", padx=(10, 0))
        division_box = ttk.Combobox(filters, textvariable=self.team_division, state="readonly", width=9,
                                    values=["전체", "동부", "중부", "서부"])
        division_box.pack(side="left", padx=5)
        ttk.Button(filters, text="필터 적용", command=self._filter_teams).pack(side="left", padx=8)
        body = ttk.Frame(outer); body.pack(fill="both", expand=True)
        left = ttk.Frame(body); left.pack(side="left", fill="both", expand=True)
        cols = ("league", "division", "abbr", "short", "founded", "team")
        self.team_tree = ttk.Treeview(left, columns=cols, show="headings", height=18)
        headers = {"league":"리그", "division":"지구", "abbr":"약자", "short":"한글 약칭", "founded":"창단", "team":"구단명"}
        widths = {"league":48, "division":55, "abbr":55, "short":105, "founded":60, "team":190}
        for c in cols:
            self.team_tree.heading(c, text=headers[c]); self.team_tree.column(c, width=widths[c], anchor="center")
        yscroll = ttk.Scrollbar(left, orient="vertical", command=self.team_tree.yview)
        self.team_tree.configure(yscrollcommand=yscroll.set)
        self.team_tree.pack(side="left", fill="both", expand=True); yscroll.pack(side="right", fill="y")
        self.team_tree.bind("<<TreeviewSelect>>", self._show_team_detail)
        right = tk.Frame(body, bg="white", highlightbackground="#D5E2EC", highlightthickness=1, padx=16, pady=14, width=350)
        right.pack(side="right", fill="y", padx=(12, 0)); right.pack_propagate(False)
        self.team_badge = tk.Label(right, text="MLB", bg=COLORS["navy"], fg="white", font=("맑은 고딕", 22, "bold"), width=8, pady=8)
        self.team_badge.pack(anchor="w", pady=(0, 10))
        self.team_name_label = tk.Label(right, text="구단을 선택하세요", bg="white", fg=COLORS["navy"], font=("맑은 고딕", 14, "bold"), wraplength=300, justify="left")
        self.team_name_label.pack(anchor="w")
        self.team_en_label = tk.Label(right, text="", bg="white", fg=COLORS["muted"], font=("맑은 고딕", 9), wraplength=300, justify="left")
        self.team_en_label.pack(anchor="w", pady=(2, 10))
        self.team_info_label = tk.Label(right, text="", bg="white", fg=COLORS["ink"], font=("맑은 고딕", 9), justify="left", anchor="w", wraplength=310)
        self.team_info_label.pack(anchor="w", fill="x")
        tk.Label(right, text="대표 팀 컬러", bg="white", fg=COLORS["navy"], font=("맑은 고딕", 10, "bold")).pack(anchor="w", pady=(14, 5))
        swatches = tk.Frame(right, bg="white"); swatches.pack(anchor="w")
        self.team_swatch1 = tk.Label(swatches, text="   ", bg="#003087", width=8, relief="solid", bd=1); self.team_swatch1.pack(side="left", padx=(0, 6))
        self.team_swatch2 = tk.Label(swatches, text="   ", bg="#E4002B", width=8, relief="solid", bd=1); self.team_swatch2.pack(side="left")
        self.team_color_label = tk.Label(right, text="", bg="white", fg=COLORS["muted"], font=("맑은 고딕", 8))
        self.team_color_label.pack(anchor="w", pady=(4, 0))
        self._filter_teams()

    def _filter_teams(self):
        if not hasattr(self, "team_tree"):
            return
        for item in self.team_tree.get_children(): self.team_tree.delete(item)
        league, division = self.team_league.get(), self.team_division.get()
        for idx, team in enumerate(TEAMS):
            lg, div, ko, en, abbr, short, founded = team[:7]
            if league != "전체" and lg != league: continue
            if division != "전체" and div != division: continue
            self.team_tree.insert("", "end", iid=str(idx), values=(lg, div, abbr, short, founded, ko))
        children = self.team_tree.get_children()
        if children:
            self.team_tree.selection_set(children[0]); self.team_tree.focus(children[0]); self._show_team_detail()

    def _show_team_detail(self, _event=None):
        selected = self.team_tree.selection()
        if not selected: return
        t = TEAMS[int(selected[0])]
        lg, div, ko, en, abbr, short, founded, city, c1, c2, symbol, uniform = t
        self.team_badge.configure(text=abbr, bg=c1, fg="white")
        self.team_name_label.configure(text=ko)
        self.team_en_label.configure(text=f"{en}  |  {lg} 리그 {div}지구")
        self.team_info_label.configure(text=f"한글 약칭: {short}\n창단/프랜차이즈 시작: {founded}년\n연고지: {city}\n\n팀 심볼\n{symbol}\n\n유니폼 특징\n{uniform}")
        self.team_swatch1.configure(bg=c1); self.team_swatch2.configure(bg=c2)
        self.team_color_label.configure(text=f"{c1}   {c2}")

    def load_data_async(self):
        self.status.set("연도별 기록 데이터 다운로드 중... (최초 실행은 인터넷 연결이 필요합니다)")
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        try:
            awards = fetch_csv("AwardsPlayers.csv")
            people = fetch_csv("People.csv")
            batting = fetch_csv("Batting.csv")
            pitching = fetch_csv("Pitching.csv")
            pmap = {}
            for p in people:
                pid = p.get("playerID")
                name = " ".join(x for x in [p.get("nameFirst",""), p.get("nameLast","")] if x).strip()
                if pid: pmap[pid] = name or pid
            self.awards, self.people, self.batting, self.pitching = awards, pmap, batting, pitching
            self.data_ready = True
            self.root.after(0, self._data_loaded)
        except Exception as exc:
            error_text = str(exc)[:150]
            self.root.after(0, lambda msg=error_text: self.status.set("온라인 데이터 연결 실패: 기본 도감은 사용 가능 | " + msg))
            self.root.after(0, lambda: self.award_note.set("연도별 기록은 인터넷 연결 후 '데이터 다시 불러오기'를 실행하세요."))
            self.root.after(0, lambda: self._add_retry_button())

    def _add_retry_button(self):
        if not hasattr(self, "retry_btn"):
            self.retry_btn = ttk.Button(self.award_tab, text="데이터 다시 불러오기", command=self.load_data_async)
            self.retry_btn.pack(anchor="e", padx=15, pady=4)

    def _data_loaded(self):
        self.status.set(f"데이터 연결 완료 | 수상 기록 {len(self.awards):,}건 | 선수 {len(self.people):,}명 | Lahman 1871–2025")
        years = sorted({str(r.get("yearID")) for r in self.awards if r.get("yearID","").isdigit()}, reverse=True)
        self.year_combo["values"] = ["전체"] + years
        self.leader_year["values"] = ["전체"] + years
        self.award_note.set(f"총 {len(self.awards):,}건의 수상 기록을 불러왔습니다. 데이터베이스에 수록된 시즌까지 표시합니다.")
        self.filter_awards()

    def filter_awards(self):
        if not self.data_ready: return
        for item in self.award_tree.get_children(): self.award_tree.delete(item)
        selected = self.award_choice.get()
        year = self.award_year.get()
        league = self.award_league.get()
        reverse = {v:k for k,v in AWARD_LABELS.items()}
        rows = []
        for r in self.awards:
            raw_award = r.get("awardID","")
            label = AWARD_LABELS.get(raw_award, raw_award)
            if selected != "전체" and label != selected: continue
            if year != "전체" and r.get("yearID") != year: continue
            lg = r.get("lgID","")
            if league != "전체" and lg != league: continue
            pid = r.get("playerID","")
            name = self.people.get(pid, pid)
            rows.append((safe_int(r.get("yearID")), label, lg, name, r.get("notes","")))
        rows.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)
        for row in rows: self.award_tree.insert("", "end", values=row)
        self.award_note.set(f"검색 결과: {len(rows):,}건 | 일부 상은 Lahman 데이터베이스의 수록 범위 및 분류 기준을 따릅니다.")

    def show_leaders(self):
        if not self.data_ready:
            self.leader_note.set("데이터를 불러오는 중입니다."); return
        for item in self.leader_tree.get_children(): self.leader_tree.delete(item)
        kind = self.leader_type.get()
        selected_year = self.leader_from.get()
        source = self.batting if kind in ("홈런","타율") else self.pitching
        sums = {}
        for r in source:
            year = r.get("yearID","")
            lg = r.get("lgID","")
            if not year.isdigit() or lg not in ("AL","NL"): continue
            if selected_year != "전체" and year != selected_year: continue
            pid = r.get("playerID","")
            key = (year,lg,pid)
            if key not in sums: sums[key] = {"value":0.0,"team":r.get("teamID","")}
            if kind == "홈런": sums[key]["value"] += safe_int(r.get("HR"))
            elif kind == "타율":
                sums[key]["H"] = sums[key].get("H",0) + safe_int(r.get("H"))
                sums[key]["AB"] = sums[key].get("AB",0) + safe_int(r.get("AB"))
            elif kind == "다승": sums[key]["value"] += safe_int(r.get("W"))
            elif kind == "탈삼진": sums[key]["value"] += safe_int(r.get("SO"))
        leaders = {}
        for (year,lg,pid), data in sums.items():
            if kind == "타율":
                ab = data.get("AB",0); h = data.get("H",0)
                # 규정 타석을 완전히 재현하지 않고 최소 100타수 기준의 참고 리더로 계산
                if ab < 100: continue
                value = h / ab if ab else 0
                display = f"{value:.3f}".replace("0.",".")
            else:
                value = data["value"]; display = str(int(value))
            key = (year,lg)
            if key not in leaders or value > leaders[key][0]:
                leaders[key] = (value, [(pid,data["team"],display)])
            elif value == leaders[key][0]:
                leaders[key][1].append((pid,data["team"],display))
        for (year,lg), (value, players) in sorted(leaders.items(), reverse=True):
            for pid, team, display in players:
                self.leader_tree.insert("", "end", values=(year,lg,self.people.get(pid,pid),team,display))
        note = "타율은 데이터 비교용으로 100타수 이상을 대상으로 계산한 참고값이며, 공식 타격왕 규정타석과 다를 수 있습니다."
        if kind != "타율": note = "동률 기록은 모두 표시합니다. 다승·탈삼진·홈런은 정규시즌 리그별 합산 기록입니다."
        self.leader_note.set(note)

def main():
    root = tk.Tk()
    app = BaseballMaster(root)
    root.mainloop()

if __name__ == "__main__":
    main()
