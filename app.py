import streamlit as st
import google.genai as genai
from google.genai import types
import datetime
import random
import ephem
import pytz
from lunar_python import Lunar, Solar
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# ==========================================
# [기본 설정] 페이지 디자인 & CSS
# ==========================================
st.set_page_config(
    page_title="AI 운명 전략가 (V5.0 Final)",
    page_icon="🔮",
    layout="wide"
)

# [CSS] 미드나잇 골드 테마 (유지)
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #1a1a2e; border-right: 1px solid #444; }
    h1, h2, h3 { color: #ffd700 !important; font-family: 'Times New Roman', serif; text-shadow: 0 0 10px rgba(255, 215, 0, 0.3); }
    div[data-testid="stMetricValue"] { color: #00d2ff !important; font-weight: bold; }
    .stButton>button { background: linear-gradient(90deg, #FFD700 0%, #FDB931 100%); color: #1a1a2e; border: none; border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# [보안] API 키
# ==========================================
try:
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    MY_API_KEY = "" 

# ==========================================
# [함수 1] 주역 64괘 (전체 데이터 복원)
# ==========================================
def get_real_iching():
    """주역 64괘 전체 리스트 (삭제 없음)"""
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

# ==========================================
# [함수 2] 점성술 (실시간 Ephem 계산 복원)
# ==========================================
def get_real_astrology(year, month, day, hour, minute):
    """
    Ephem 라이브러리를 사용하여 실제 행성의 별자리 위치를 계산합니다.
    (단순 텍스트 출력이 아니라 실제 천문 계산 로직 적용)
    """
    try:
        # 관측지 설정 (서울)
        obs = ephem.Observer()
        obs.lat, obs.lon = '37.5665', '126.9780'
        # UTC 변환 (한국시간 - 9시간)
        obs.date = datetime.datetime(year, month, day, hour, minute) - datetime.timedelta(hours=9)
        
        # 태양과 달 객체 생성 및 계산
        sun = ephem.Sun(obs)
        sun.compute(obs)
        moon = ephem.Moon(obs)
        moon.compute(obs)
        
        # 별자리 매핑 (Ephem은 별자리 이름을 바로 주지 않으므로 좌표로 매핑 필요하지만, 
        # 여기서는 ephem.constellation 기능을 사용하여 간략화된 정확한 별자리를 가져옵니다)
        sun_const = ephem.constellation(sun)[1] # (Abbr, Name) 중 Name 반환
        moon_const = ephem.constellation(moon)[1]
        
        return {"desc": f"태양은 {sun_const}자리에, 달은 {moon_const}자리에 위치합니다."}
    except Exception as e:
        return {"desc": f"천문 데이터 계산 중 오류: {str(e)}"}

# ==========================================
# [함수 3] 기문둔갑 (Lunar_python 정밀 계산 복원)
# ==========================================
def get_real_qimen(year, month, day, hour):
    """
    Lunar Python 라이브러리를 사용하여 그날의 정확한 
    재신(God of Wealth)과 희신(God of Joy) 방향을 산출합니다.
    """
    try:
        # 양력을 입력받아 음력/간지 변환 객체 생성
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        
        # 재신(재물)과 희신(기쁨)의 방향 계산
        wealth_pos = lunar.getDayPositionCai() # 예: 震, 兌
        joy_pos = lunar.getDayPositionXi()
        
        # 한자 -> 한글 매핑 (정확한 8방위)
        direction_map = {
            "震": "동쪽(East)", "兌": "서쪽(West)", "離": "남쪽(South)", "坎": "북쪽(North)",
            "巽": "남동쪽(SE)", "坤": "남서쪽(SW)", "乾": "북서쪽(NW)", "艮": "북동쪽(NE)"
        }
        
        wealth_str = direction_map.get(wealth_pos, wealth_pos)
        joy_str = direction_map.get(joy_pos, joy_pos)
        
        return {"desc": f"💰 재물운 방향: {wealth_str} / 🎉 성공운 방향: {joy_str}"}
    except Exception as e:
        return {"desc": "방위 데이터 계산 실패"}

# ==========================================
# [함수 4] 타로 (78장 완전판 유지)
# ==========================================
def get_real_tarot():
    """타로 78장 완전판 (Full Deck)"""
    major = [
        "0. The Fool (바보)", "I. The Magician (마법사)", "II. The High Priestess (여사제)",
        "III. The Empress (여황제)", "IV. The Emperor (황제)", "V. The Hierophant (교황)",
        "VI. The Lovers (연인)", "VII. The Chariot (전차)", "VIII. Strength (힘)",
        "IX. The Hermit (은둔자)", "X. Wheel of Fortune (운명의 수레바퀴)", "XI. Justice (정의)",
        "XII. The Hanged Man (매달린 남자)", "XIII. Death (죽음)", "XIV. Temperance (절제)",
        "XV. The Devil (악마)", "XVI. The Tower (탑)", "XVII. The Star (별)",
        "XVIII. The Moon (달)", "XIX. The Sun (태양)", "XX. Judgement (심판)", "XXI. The World (세계)"
    ]
    suits = {"Wands": "행동", "Cups": "감정", "Swords": "이성", "Pentacles": "물질"}
    ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
    minor = [f"{r} of {s} ({k})" for s, k in suits.items() for r in ranks]
    return random.choice(major + minor)

# ==========================================
# [함수 5] 수비학 & 사주 (기존 로직 유지)
# ==========================================
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
    meanings = {
        1: "개척과 독립의 리더", 2: "조화와 협력의 중재자", 3: "창조와 표현의 예술가",
        4: "안정과 질서의 건축가", 5: "변화와 자유의 모험가", 6: "책임과 봉사의 보호자",
        7: "분석과 통찰의 탐구자", 8: "성취와 권력의 지배자", 9: "완성과 포용의 멘토",
        11: "영적 직관의 마스터", 22: "위대한 실행의 마스터", 33: "헌신적 사랑의 마스터"
    }
    return f"{number} ({meanings.get(number, '알 수 없는 숫자')})"

def get_real_saju(year, month, day, hour, minute):
    try:
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = solar.getLunar()
        bazi = lunar.getBaZi()
        day_master = bazi[2][0] if len(bazi[2]) > 0 else "갑"
        return {"text": f"{bazi[0]}년 {bazi[1]}월 {bazi[2]}일", "day_master": day_master, "desc": f"일간(본질): {day_master}"}
    except:
        return {"text": "정보 없음", "day_master": "갑", "desc": "계산 오류"}

# [시각화 함수] 오행 차트 (랜덤성 유지)
def draw_five_elements_chart(day_master):
    categories = ['목(나무)', '화(불)', '토(흙)', '금(쇠)', '수(물)']
    weights = [3, 3, 3, 3, 3] # 기본 점수
    # 일간에 따른 가중치
    if day_master in ['갑', '을']: weights[0] += 2
    elif day_master in ['병', '정']: weights[1] += 2
    elif day_master in ['무', '기']: weights[2] += 2
    elif day_master in ['경', '신']: weights[3] += 2
    elif day_master in ['임', '계']: weights[4] += 2
    
    values = [min(5, w + random.randint(-1, 1)) for w in weights]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values, theta=categories, fill='toself', name='오행',
        line_color='#ffd700', fillcolor='rgba(255, 215, 0, 0.3)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 6], showticklabels=False, linecolor='#444'), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=40, r=40, t=20, b=20), showlegend=False, height=250
    )
    return fig

def load_lottieurl(url):
    try:
        r = requests.get(url); 
        return r.json() if r.status_code == 200 else None
    except: return None

# ==========================================
# [UI] 사이드바 및 메인
# ==========================================
st.sidebar.title("🔮 AI 운명 전략가")
st.sidebar.caption("Master Engine V5.0 Final")
st.sidebar.markdown("---")

with st.sidebar.form("input_form"):
    name = st.text_input("이름", "방문자")
    col1, col2 = st.columns(2)
    with col1: b_date = st.date_input("생년월일", datetime.date(1990, 1, 1))
    with col2: b_time = st.time_input("태어난 시각", datetime.time(12, 0))
    submitted = st.form_submit_button("✨ 운명 분석 시작")

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title(f"🌌 {name}님을 위한 심층 운명 리포트")
    st.markdown("##### 사주 × 점성술 × 수비학 × 주역 × 기문둔갑 × 타로 통합 분석")
with col_h2:
    lottie_json = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_tijmpky4.json")
    if lottie_json: st_lottie(lottie_json, height=120, key="crystal_ball")

st.divider()

if submitted:
    if not MY_API_KEY:
        st.error("🚨 API 키가 설정되지 않았습니다.")
    else:
        # 데이터 계산
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        by, bm, bd = b_date.year, b_date.month, b_date.day
        bh, bmin = b_time.hour, b_time.minute
        
        # 각 모듈 호출 (완전판 로직 적용됨)
        saju = get_real_saju(by, bm, bd, bh, bmin)
        astro = get_real_astrology(by, bm, bd, bh, bmin)
        qimen = get_real_qimen(now.year, now.month, now.day, now.hour)
        iching = get_real_iching()
        tarot = get_real_tarot()
        life_path = calculate_life_path_number(by, bm, bd)
        personal_day = calculate_personal_day_number(bm, bd, now.year, now.month, now.day)
        
        # 대시보드 출력
        st.success("✅ 정밀 데이터 산출 완료 (All Engines Active)")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("###### 📊 오행 에너지 차트")
            fig = draw_five_elements_chart(saju['day_master'])
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with c2:
            st.markdown("###### 🔑 핵심 운명 코드")
            m1, m2, m3 = st.columns(3)
            m1.metric("일간", saju['day_master'])
            m2.metric("운명수", life_path)
            m3.metric("오늘의 수", personal_day)
            
            st.info(f"🧭 **기문둔갑 방위:** {qimen['desc']}")
            st.info(f"🪐 **점성술 배치:** {astro['desc']}")
            st.info(f"☯️ **주역 괘:** {iching}")

# 4. AI 리포트 생성 (Gemini 2.5 Flash 모델 사용)
        prompt = f"""
        당신은 '대한민국 최고의 수석 운명 전략가'입니다. 
        사용자 {name}님의 데이터를 종합하여 **인생을 바꾸는 하루 전략 리포트**를 작성하세요.

        [분석 데이터]
        - 🀄 사주: {saju['text']} ({saju['desc']})
        - 🔢 수비학: 운명수 {life_path}, 일운수 {personal_day}
        - 🧭 기문둔갑: {qimen['desc']}
        - 🪐 점성술: {astro['desc']}
        - ☯️ 주역: {iching}
        - 🃏 타로: {tarot}

        [작성 필수 가이드]
        ## 1. 🎯 오늘의 종합 운세 (전반적인 흐름과 100점 만점 점수)
        ## 2. 🔢 수비학 × 사주 심층 분석 (에너지 조화 및 상호작용)
        ## 3. ⚡ 기문둔갑 시공간 전략 (골든타임과 방위 활용법)
        ## 4. 💌 주역과 타로가 전하는 핵심 메시지 (두 점술의 연결고리)
        
        ## 5. 📋 오늘의 행동 강령 (실행 가능한 구체적 지침)
        ### ✅ 꼭 해야 할 일 3가지
        1. (예시: "오전 11시경, 서늘한 바람이 부는 곳에서 10분간 명상하기")
        2. (사용자 데이터 기반의 구체적 지시)
        3. (사용자 데이터 기반의 구체적 지시)

        ### ❌ 절대 피해야 할 일 3가지
        1. (예시: "오후 3시에서 5시 사이, 중요한 금전 계약이나 큰 지출은 피할 것")
        2. (구체적 금기 사항)
        3. (구체적 금기 사항)

        ### 🍀 오늘의 행운 아이템
        - **색상:** (오늘의 기운을 보완하는 색)
        - **숫자:** (수비학적 행운의 수)
        - **음식:** (개운에 도움되는 음식)
        - **방향:** {qimen['desc']}를 기반으로 한 최고의 길방
        """
        
        st.subheader(f"📜 {name} 님을 위한 심층 전략 리포트")
        with st.spinner("Gemini 2.5 Flash가 운명의 코드를 정밀 분석 중입니다..."):
            try:
                # 신버전 google-genai SDK 방식 유지
                client = genai.Client(api_key=MY_API_KEY)
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=prompt
                )
                
                # 결과 출력
                if response.text:
                    st.markdown(response.text)
                else:
                    st.warning("AI 리포트 생성에 실패했습니다. 다시 시도해주세요.")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")