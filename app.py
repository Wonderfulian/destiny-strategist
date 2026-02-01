import streamlit as st
import google.genai as genai
from google.genai import types
import datetime
import random
import ephem
import pytz
from lunar_python import Lunar, Solar
import plotly.graph_objects as go
import requests
import markdown
import numpy as np # 텍스처 생성용 (혹시 모를 에러 방지)

# ==========================================
# [기본 설정] 페이지 디자인
# ==========================================
st.set_page_config(
    page_title="운세 전략가 (Final Ver.)",
    page_icon="🔮",
    layout="wide"
)

# ==========================================
# [설정] 배경 이미지 적용 🖼️
# ==========================================
# 사용자 제공 이미지 (Imgur 직접 링크로 변환 적용)
CUSTOM_BG_URL = "https://i.imgur.com/W4o6mLu.jpeg"

# 배경 CSS 결정
bg_image_css = f"url('{CUSTOM_BG_URL}')"
bg_size_css = "cover"
bg_repeat_css = "no-repeat"
bg_attachment = "fixed"

# ==========================================
# [디자인 시스템] CSS 적용 (Freshman Style)
# ==========================================
st.markdown(f"""
    <style>
    /* 1. 폰트 로드 */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@400;500;700&display=swap');

    /* 2. 전체 배경 적용 */
    .stApp {{
        background-image: {bg_image_css};
        background-size: {bg_size_css};
        background-repeat: {bg_repeat_css};
        background-attachment: {bg_attachment};
        background-position: center center;
        color: #F0F0F0; 
        font-family: 'DM Sans', sans-serif;
    }}

    /* 3. 사이드바 (배경과 어우러지는 어두운 톤) */
    [data-testid="stSidebar"] {{
        background-color: rgba(20, 20, 20, 0.85); 
        border-right: 1px solid #333;
        backdrop-filter: blur(10px);
    }}

    /* 4. 제목 스타일 (거대한 명조체) */
    h1 {{
        font-family: 'Playfair Display', serif !important;
        color: #FFFFFF !important;
        font-size: 5rem !important;
        font-weight: 400 !important;
        text-transform: uppercase;
        margin-bottom: 0px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }}
    
    h2, h3 {{
        font-family: 'Playfair Display', serif !important;
        color: #E0E0E0 !important;
        margin-top: 30px;
        padding-top: 10px;
        border-top: 1px solid rgba(255,255,255,0.2);
    }}

    /* 5. 입력창 커스텀 (어두운 반투명) */
    .stTextInput > div > div > input {{
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #FFFFFF !important;
        border: 1px solid #555 !important;
        border-radius: 0px !important;
        padding: 12px !important;
        font-family: 'DM Sans', sans-serif !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #FFF !important;
        background-color: rgba(0, 0, 0, 0.8) !important;
    }}
    .stTextInput label {{
        color: #CCC !important;
        font-family: 'DM Sans', sans-serif;
        text-transform: uppercase;
        font-size: 0.9rem;
        letter-spacing: 2px;
    }}

    /* 6. 버튼 스타일 (심플한 화이트 라인) */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {{
        width: 100%;
        background-color: transparent !important;
        color: #FFFFFF !important;
        font-family: 'DM Sans', sans-serif;
        text-transform: uppercase;
        font-weight: 700;
        padding: 15px 0;
        border: 2px solid #FFFFFF;
        border-radius: 0px;
        letter-spacing: 2px;
        margin-top: 20px;
        transition: all 0.3s;
    }}
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }}

    /* 7. 결과 카드 (흰색 박스 제거 -> 어두운 유리 효과) */
    .result-card {{
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 30px;
        margin-bottom: 30px;
        background-color: rgba(0, 0, 0, 0.6); /* 어둡게 변경 */
        backdrop-filter: blur(10px);
    }}

    /* 8. 메트릭 스타일 */
    div[data-testid="stMetricValue"] {{
        font-family: 'Playfair Display', serif;
        color: #FFF !important;
        font-size: 40px !important;
        text-shadow: 0 0 10px rgba(0,0,0,0.5);
    }}
    div[data-testid="stMetricLabel"] {{
        color: #AAA !important;
        font-family: 'DM Sans', sans-serif;
        font-size: 12px;
        letter-spacing: 1px;
    }}

    /* 9. 텍스트 가독성 */
    .stMarkdown p, .stMarkdown li {{
        color: #EEE !important;
        font-size: 16px;
        line-height: 1.8;
    }}
    strong {{
        color: #FFD700; /* 골드 포인트 */
        font-weight: 700;
    }}
    
    /* 10. 알림 박스 */
    .stInfo, .stSuccess, .stWarning, .stError {{
        background-color: rgba(0,0,0,0.5) !important;
        border: 1px solid #777 !important;
        color: #DDD !important;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# [보안] API 키 설정
# ==========================================
try:
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    MY_API_KEY = ""

# ==========================================
# [함수] 로직 및 데이터 (V5.0 Final과 동일)
# ==========================================
def get_real_iching():
    hexagrams = [
        "1. 중천건(乾) - 위대한 하늘, 강건함, 창조적 에너지", "2. 중지곤(坤) - 포용하는 땅, 유순함, 어머니의 품",
        "3. 수뢰둔(屯) - 험난한 시작, 인내하며 싹을 틔움", "4. 산수몽(蒙) - 어리석음을 깨우침, 배움의 시기",
        "5. 수천수(需) - 때를 기다림, 인내와 준비", "6. 천수송(訟) - 다툼과 소송, 물러서서 타협해야 함",
        "7. 지수사(師) - 군대를 이끄는 리더십, 엄격한 규율", "8. 수지비(比) - 사람들과 친밀하게 어울림, 협력",
        "9. 풍천소축(小畜) - 잠시 멈춤, 구름은 끼었으나 비는 아직 안 옴", "10. 천택리(履) - 호랑이 꼬리를 밟음, 예의와 조심성",
        "11. 지천태(泰) - 태평성대, 하늘과 땅의 화합 (길)", "12. 천지비(否) - 막혀있는 운세, 소통이 필요함",
        "13. 천화동인(同人) - 뜻을 같이하는 동료, 협동", "14. 화천대유(大有) - 크게 가짐, 태양이 하늘에 뜸 (대길)",
        "15. 지산겸(謙) - 겸손하면 형통함, 자신을 낮춤", "16. 뇌지예(豫) - 미리 준비하고 즐거워함",
        "17. 택뢰수(隨) - 흐름을 따름, 임기응변", "18. 산풍고(蠱) - 부패를 척결하고 새롭게 함",
        "19. 지택림(臨) - 군자가 다가옴, 성대한 기운", "20. 풍지관(觀) - 냉철한 관찰, 본보기가 됨",
        "21. 화뢰서합(噬嗑) - 방해물을 씹어 없앰, 법 집행", "22. 산화비(賁) - 아름답게 꾸밈, 외면의 화려함",
        "23. 산지박(剝) - 깎여나감, 쇠퇴기, 기초를 다져야 함", "24. 지뢰복(復) - 다시 돌아옴, 회복의 기운",
        "25. 천뢰무망(無妄) - 거짓 없이 진실함, 자연스러움", "26. 산천대축(大畜) - 크게 쌓음, 인재를 기름",
        "27. 산뢰이(頤) - 올바른 양육, 말조심과 음식 조절", "28. 택풍대과(大過) - 기둥이 휨, 과도한 부담",
        "29. 중수감(坎) - 첩첩산중, 험난한 물, 지혜로 극복", "30. 중화리(離) - 타오르는 불, 지혜와 문명, 이별",
        "31. 택산함(咸) - 마음이 통함, 감동과 사랑", "32. 뇌풍항(恒) - 변함없이 꾸준함, 지속성",
        "33. 천산둔(遯) - 물러나서 은둔함, 때를 기다리는 지혜", "34. 뇌천대장(大壯) - 용맹하고 씩씩함, 폭주 주의",
        "35. 화지진(晉) - 나아가 승진함, 밝은 해가 떠오름", "36. 지화명이(明夷) - 빛이 땅에 가려짐, 고난 속의 지혜",
        "37. 풍화가인(家人) - 가정의 화목, 본분에 충실", "38. 화택규(睽) - 서로 어긋나고 반목함, 다름을 인정",
        "39. 수산건(蹇) - 가다가 멈춤, 어려움에 직면", "40. 뇌수해(解) - 어려움이 풀림, 해결의 실마리",
        "41. 산택손(損) - 덜어냄, 봉사와 희생 후의 이익", "42. 풍뢰익(益) - 더함, 바람과 우뢰가 도움 (길)",
        "43. 택천쾌(夬) - 결단하여 제거함, 과감한 결정", "44. 천풍구(姤) - 우연한 만남, 유혹을 조심",
        "45. 택지췌(萃) - 사람들이 모여듦, 번창과 축제", "46. 지풍승(升) - 땅 속에서 나무가 자람, 상승운",
        "47. 택수곤(困) - 곤란함, 물이 말라버린 연못", "48. 수풍정(井) - 마르지 않는 우물, 변치 않는 덕",
        "49. 택화혁(革) - 옛것을 버리고 새롭게 고침, 혁신", "50. 화풍정(鼎) - 솥에 음식을 끓임, 안정과 쇄신",
        "51. 중뢰진(震) - 우르릉 쾅쾅, 놀라지만 깨달음이 있음", "52. 중산간(艮) - 산처럼 멈춰 서서 안정을 찾음",
        "53. 풍산점(漸) - 차근차근 나아감, 순서대로 진행", "54. 뇌택귀매(歸妹) - 순서가 뒤바뀜, 불안정한 관계",
        "55. 뇌화풍(豐) - 풍요롭고 성대함, 전성기", "56. 화산여행(旅) - 나그네의 여행, 불안정하지만 자유로움",
        "57. 중풍손(巽) - 공손하게 스며듦, 바람 같은 유연함", "58. 중택태(兌) - 기쁨과 즐거움, 연못과 소녀",
        "59. 풍수환(渙) - 흩어짐, 근심 해소, 멀리 나아감", "60. 수택절(節) - 대나무 마디, 절제와 규칙",
        "61. 풍택중부(中孚) - 마음속의 진실, 믿음", "62. 뇌산소과(小過) - 작은 새가 나는 형상, 겸손해야 함",
        "63. 수화기제(旣濟) - 이미 건너감, 완성, 성취", "64. 화수미제(未濟) - 아직 건너지 못함, 미완성, 새로운 시작"
    ]
    return random.choice(hexagrams)

def get_real_astrology(year, month, day, hour, minute):
    try:
        obs = ephem.Observer()
        obs.lat, obs.lon = '37.5665', '126.9780'
        obs.date = datetime.datetime(year, month, day, hour, minute) - datetime.timedelta(hours=9)
        sun = ephem.Sun(obs); sun.compute(obs); moon = ephem.Moon(obs); moon.compute(obs)
        return {"desc": f"태양[{ephem.constellation(sun)[1]}], 달[{ephem.constellation(moon)[1]}]"}
    except: return {"desc": "천문 정보 계산 불가"}

def get_real_qimen(year, month, day, hour):
    try:
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        wealth_pos = lunar.getDayPositionCai()
        joy_pos = lunar.getDayPositionXi()
        d_map = {"震":"동(E)","兌":"서(W)","離":"남(S)","坎":"북(N)","巽":"남동(SE)","坤":"남서(SW)","乾":"북서(NW)","艮":"북동(NE)"}
        return {"desc": f"재물:{d_map.get(wealth_pos, wealth_pos)} / 성공:{d_map.get(joy_pos, joy_pos)}"}
    except: return {"desc": "방위 정보 계산 불가"}

def get_real_tarot():
    major = ["0.Fool","I.Magician","II.High Priestess","III.Empress","IV.Emperor","V.Hierophant","VI.Lovers","VII.Chariot","VIII.Strength","IX.Hermit","X.Wheel","XI.Justice","XII.Hanged Man","XIII.Death","XIV.Temperance","XV.Devil","XVI.Tower","XVII.Star","XVIII.Moon","XIX.Sun","XX.Judgement","XXI.World"]
    suits = {"Wands":"열정","Cups":"감정","Swords":"이성","Pentacles":"현실"}
    ranks = ["Ace","2","3","4","5","6","7","8","9","10","Page","Knight","Queen","King"]
    minor = [f"{r} of {s}" for s in suits for r in ranks]
    return random.choice(major + minor)

def reduce_to_single_digit(num, check_master=True):
    while num > 9:
        if check_master and num in [11, 22, 33, 44]: return num
        num = sum(int(digit) for digit in str(num))
    return num

def calculate_life_path_number(year, month, day):
    total = sum(int(d) for d in str(year)) + sum(int(d) for d in str(month)) + sum(int(d) for d in str(day))
    return reduce_to_single_digit(total, check_master=True)

def calculate_personal_day_number(birth_month, birth_day, current_year, current_month, current_day):
    total = (birth_month + birth_day) + sum(int(d) for d in str(current_year)) + (current_month + current_day)
    return reduce_to_single_digit(total, check_master=False)

def get_numerology_meaning(number, is_life_path=True):
    meanings = {1:"리더",2:"중재자",3:"예술가",4:"건축가",5:"모험가",6:"보호자",7:"탐구자",8:"지배자",9:"인도주의자",11:"직관",22:"실행",33:"헌신"}
    return f"{number} ({meanings.get(number, '')})"

def get_real_saju(year, month, day, hour, minute):
    try:
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = solar.getLunar()
        bazi = lunar.getBaZi()
        day_master = bazi[2][0] if len(bazi[2]) > 0 else "갑"
        return {"text": f"{bazi[0]}년 {bazi[1]}월 {bazi[2]}일", "day_master": day_master, "desc": f"일간:{day_master}"}
    except: return {"text": "정보 없음", "day_master": "갑", "desc": "오류"}

def draw_five_elements_chart(day_master):
    categories = ['목', '화', '토', '금', '수']
    values = [random.randint(2, 5) for _ in range(5)]
    fig = go.Figure()
    # 차트 색상: 화이트 라인 (배경과 대비)
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself', 
        line_color='#FFFFFF', fillcolor='rgba(255, 255, 255, 0.15)' 
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False, linecolor='#888'),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#FFF', size=14),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        height=300
    )
    return fig

# ==========================================
# [UI] 사이드바 및 메인
# ==========================================
st.sidebar.title("🔮 운세 전략가")
st.sidebar.markdown("---")

with st.sidebar.form("input_form", enter_to_submit=False):
    st.markdown("### 📝 BASIC INFO")
    name = st.text_input("Name", placeholder="이름을 입력하세요")
    col1, col2 = st.columns(2)
    with col1: 
        b_date_str = st.text_input("Birth Date", placeholder="19900101")
    with col2: 
        b_time_str = st.text_input("Birth Time", placeholder="14:30")
    
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button("ANALYZE DESTINY")

# Main Header (Lottie 제거)
st.markdown("""
# DESTINY<br>STRATEGIST
### 당신을 위한 6차원 심층 분석 리포트
---
""")

# st_lottie 제거됨

st.divider()

if submitted:
    if not MY_API_KEY:
        st.error("🚨 API KEY NOT FOUND")
    else:
        # 날짜/시간 포맷 파싱
        try:
            b_date = datetime.datetime.strptime(b_date_str, "%Y%m%d").date()
            b_time = datetime.datetime.strptime(b_time_str, "%H:%M").time()
        except ValueError:
            st.error("❌ 날짜/시간 형식을 확인해주세요. (예: 19900101, 14:30)")
            st.stop()

        # 데이터 계산
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        by, bm, bd = b_date.year, b_date.month, b_date.day
        bh, bmin = b_time.hour, b_time.minute
        
        saju = get_real_saju(by, bm, bd, bh, bmin)
        astro = get_real_astrology(by, bm, bd, bh, bmin)
        qimen = get_real_qimen(now.year, now.month, now.day, now.hour)
        iching = get_real_iching()
        tarot = get_real_tarot()
        life_path = calculate_life_path_number(by, bm, bd)
        personal_day = calculate_personal_day_number(bm, bd, now.year, now.month, now.day)
        
        # [결과 대시보드]
        st.markdown(f"### 👋 HELLO, {name}")
        st.success("ANALYSIS COMPLETED")
        
        # 흰색 박스 제거됨 -> 어두운 유리 카드(result-card) 사용
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        # 2단 레이아웃
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### 01. ENERGY BALANCE")
            fig = draw_five_elements_chart(saju['day_master'])
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with c2:
            st.markdown("#### 02. KEY CODES")
            st.markdown(f"""
            - **DAY MASTER:** {saju['day_master']} (일간)
            - **LIFE PATH:** {life_path} (운명수)
            - **PERSONAL DAY:** {personal_day} (오늘의 수)
            """)
            st.markdown("---")
            st.markdown(f"**🧭 DIRECTION:** {qimen['desc']}")
            st.markdown(f"**☯️ ICHING:** {iching.split('-')[0]}")
            st.markdown(f"**🃏 TAROT:** {tarot}")
            
        st.markdown('</div>', unsafe_allow_html=True)

        # AI 프롬프트 (기존 최적화된 내용 유지)
        prompt = f"""
        저는 대한민국 최고의 운세 전략가입니다. {name}님을 위한 오늘 하루 실전 가이드를 작성해드립니다.
        
        [데이터]
        - 🀄 사주: {saju['text']} ({saju['desc']})
        - 🔢 수비학: 운명수 {life_path} / 일운수 {personal_day}
        - 🧭 기문둔갑: {qimen['desc']}
        - 🪐 점성술: {astro['desc']}
        - ☯️ 주역: {iching}
        - 🃏 타로: {tarot}
        
        [작성 원칙]
        - 말투: 명확하고 세련되게 (잡지 에디터처럼)
        - 제목 반복 금지. 본문 바로 시작.
        - 점수와 한 줄 요약 사이에는 반드시 한 줄 띄울 것.
        - 구체적인 행동 강령 포함 (해야 할 일, 피해야 할 일, 행운 아이템)
        
        ---
        ## 🎯 DAILY SUMMARY
        **점수:** ___/100
        
        **KEYWORD:** (오늘을 관통하는 핵심 단어)
        
        (전체적인 운세 흐름 요약...)
        
        ## 📋 ACTION PLAN
        ### ✅ TO DO (3가지)
        1. 
        2. 
        3. 
        ### ❌ NOT TO DO (3가지)
        1. 
        2. 
        3. 
        ### 🍀 LUCKY ITEMS
        - **COLOR:**
        - **NUMBER:**
        - **FOOD:**
        - **DIRECTION:**
        """

        st.subheader("📜 STRATEGIC REPORT")
        with st.spinner("GENERATING REPORT..."):
            try:
                client = genai.Client(api_key=MY_API_KEY)
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=prompt
                )
                
                if response.text:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # [HTML 다운로드]
                    st.markdown("---")
                    html_content = f"""
                    <html>
                    <head>
                        <style>
                            @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');
                            body {{ font-family: 'DM Sans', sans-serif; padding: 40px; background-color: #787D73; color: #F0F0F0; }}
                            h1 {{ font-family: 'Playfair Display', serif; border-bottom: 3px solid #FFF; padding-bottom: 10px; text-transform: uppercase; }}
                            h2 {{ font-family: 'Playfair Display', serif; margin-top: 30px; border-top: 1px dashed #FFF; padding-top: 10px; }}
                            .box {{ border: 2px solid #FFF; padding: 20px; margin-bottom: 20px; background: rgba(0,0,0,0.1); }}
                            strong {{ color: #FFCC00; }}
                        </style>
                    </head>
                    <body>
                        <h1>🔮 {name}'s DESTINY REPORT</h1>
                        <div class="box">
                            <p><strong>DATE:</strong> {datetime.datetime.now().strftime('%Y-%m-%d')}</p>
                            <p><strong>KEY CODES:</strong> LP {life_path}, PD {personal_day}, {saju['day_master']}</p>
                        </div>
                        {markdown.markdown(response.text) if 'markdown' in locals() else response.text.replace('\n', '<br>')}
                    </body>
                    </html>
                    """
                    st.download_button(
                        label="📄 SAVE REPORT (HTML/PDF)",
                        data=html_content,
                        file_name=f"{name}_report.html",
                        mime="text/html"
                    )
                    
                else:
                    st.warning("AI 생성 실패. 다시 시도해주세요.")
                
            except Exception as e:
                st.error(f"SYSTEM ERROR: {e}")