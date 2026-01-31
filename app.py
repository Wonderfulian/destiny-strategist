import streamlit as st
from google import genai
from google.genai import types
import datetime
import random
import ephem
import pytz
from lunar_python import Lunar, Solar

# ==========================================
# [기본 설정] 페이지 제목 및 레이아웃
# ==========================================
st.set_page_config(
    page_title="AI 운명 전략가 (Master Engine v3.0)",
    page_icon="🔮",
    layout="wide"
)

# ==========================================
# [보안] API 키 설정 (금고에서 꺼내기)
# ==========================================
try:
    # Streamlit Cloud 배포 후에는 여기서 키를 가져옵니다.
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # 로컬 테스트 용도 (깃허브 올릴 땐 빈칸으로 두세요)
    MY_API_KEY = "" 

# ⚠️ 주의: 여기서 client를 바로 연결하지 않습니다. (에러 방지)
# 버튼을 눌렀을 때 연결합니다.

# ==========================================
# [함수] 5대 알고리즘 로직
# ==========================================
def get_real_iching():
    """주역 64괘 전체 리스트 (Full DB)"""
    hexagrams = [
        "1. 중천건(乾) - 강건함, 리더십, 창조", "2. 중지곤(坤) - 포용, 유순함, 따름",
        "3. 수뢰둔(屯) - 험난한 시작, 인내", "4. 산수몽(蒙) - 교육 필요, 어리석음",
        "5. 수천수(需) - 기다림, 때를 기다림", "6. 천수송(訟) - 다툼, 소송, 물러섬",
        "7. 지수사(師) - 군대, 리더십, 엄격함", "8. 수지비(比) - 친밀함, 협력",
        "9. 풍천소축(小畜) - 잠시 멈춤, 준비", "10. 천택리(履) - 조심스러움, 예의",
        "11. 지천태(泰) - 태평성대, 화합(길)", "12. 천지비(否) - 막힘, 불통",
        "13. 천화동인(同人) - 협동, 동업", "14. 화천대유(大有) - 큰 성공, 풍요(대길)",
        "15. 지산겸(謙) - 겸손, 낮춤", "16. 뇌지예(豫) - 즐거움, 미리 준비",
        "17. 택뢰수(隨) - 따름, 순응", "18. 산풍고(蠱) - 부패, 개혁",
        "19. 지택림(臨) - 군림, 접근", "20. 풍지관(觀) - 관찰, 통찰",
        "21. 화뢰서합(噬嗑) - 방해물 제거", "22. 산화비(賁) - 꾸밈, 장식",
        "23. 산지박(剝) - 깎임, 쇠퇴", "24. 지뢰복(復) - 회복, 돌아옴",
        "25. 천뢰무망(無妄) - 진실, 자연스러움", "26. 산천대축(大畜) - 큰 쌓임",
        "27. 산뢰이(頤) - 기름, 양육", "28. 택풍대과(大過) - 과부하, 무거움",
        "29. 중수감(坎) - 험난함, 함정", "30. 중화리(離) - 밝음, 지혜, 이별",
        "31. 택산함(咸) - 감응, 사랑", "32. 뇌풍항(恒) - 변함없음, 지속",
        "33. 천산둔(遯) - 은둔, 물러남", "34. 뇌천대장(大壯) - 씩씩함, 폭주 조심",
        "35. 화지진(晉) - 나아감, 승진", "36. 지화명이(明夷) - 지혜를 감춤",
        "37. 풍화가인(家人) - 가정, 본분", "38. 화택규(睽) - 어긋남, 반목",
        "39. 수산건(蹇) - 고난, 멈춤", "40. 뇌수해(解) - 해결, 해방",
        "41. 산택손(損) - 덜어냄, 봉사", "42. 풍뢰익(益) - 더함, 이익(길)",
        "43. 택천쾌(夬) - 결단, 제거", "44. 천풍구(姤) - 만남, 유혹 조심",
        "45. 택지췌(萃) - 모임, 번창", "46. 지풍승(升) - 상승, 발전",
        "47. 택수곤(困) - 곤란, 시련", "48. 수풍정(井) - 우물, 변치 않음",
        "49. 택화혁(革) - 혁신, 변화", "50. 화풍정(鼎) - 안정, 쇄신",
        "51. 중뢰진(震) - 벼락, 놀람", "52. 중산간(艮) - 산, 멈춤",
        "53. 풍산점(漸) - 점진적 발전", "54. 뇌택귀매(歸妹) - 어긋난 결혼",
        "55. 뇌화풍(豐) - 풍성함, 전성기", "56. 화산여행(旅) - 여행, 불안정",
        "57. 중풍손(巽) - 겸손, 바람", "58. 중택태(兌) - 기쁨, 연못",
        "59. 풍수환(渙) - 흩어짐, 해소", "60. 수택절(節) - 절제, 규칙",
        "61. 풍택중부(中孚) - 믿음, 진심", "62. 뇌산소과(小過) - 작은 지나침",
        "63. 수화기제(旣濟) - 완성, 성취", "64. 화수미제(未濟) - 미완성, 새출발"
    ]
    return random.choice(hexagrams)

def get_real_tarot():
    """타로 78장 전체"""
    major = [
        "The Fool (0) - 새로운 시작", "The Magician (I) - 창조력", "The High Priestess (II) - 직관",
        "The Empress (III) - 풍요", "The Emperor (IV) - 권위", "The Hierophant (V) - 전통",
        "The Lovers (VI) - 사랑과 선택", "The Chariot (VII) - 승리", "Strength (VIII) - 용기",
        "The Hermit (IX) - 성찰", "Wheel of Fortune (X) - 운명의 전환", "Justice (XI) - 정의",
        "The Hanged Man (XII) - 희생", "Death (XIII) - 변화와 재생", "Temperance (XIV) - 절제",
        "The Devil (XV) - 집착", "The Tower (XVI) - 붕괴와 깨달음", "The Star (XVII) - 희망",
        "The Moon (XVIII) - 환상", "The Sun (XIX) - 기쁨", "Judgement (XX) - 심판", "The World (XXI) - 완성"
    ]
    suits = ["Wands (열정)", "Cups (감정)", "Swords (이성)", "Pentacles (현실)"]
    ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]
    minor = [f"{r} of {s}" for s in suits for r in ranks]
    return random.choice(major + minor)

def get_real_saju(year, month, day, hour, minute):
    """lunar_python으로 정확한 사주팔자 계산"""
    try:
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = solar.getLunar()
        bazi = lunar.getBaZi()
        day_master = bazi[2][0] if len(bazi[2]) > 0 else "갑"
        jieqi = lunar.getJieQi()
        return {
            "text": f"{bazi[0]}년 {bazi[1]}월 {bazi[2]}일 {bazi[3]}시",
            "day_master": day_master,
            "desc": f"본원(日干)은 '{day_master}'이며, 절기는 '{jieqi}'입니다."
        }
    except Exception:
        return {"text": "계산 불가", "day_master": "갑", "desc": "정보 부족"}

def get_real_astrology(year, month, day, hour, minute):
    """ephem으로 천문 계산"""
    try:
        obs = ephem.Observer()
        obs.lat, obs.lon = '37.5665', '126.9780' # Seoul
        obs.date = datetime.datetime(year, month, day, hour, minute) - datetime.timedelta(hours=9)
        sun = ephem.Sun(obs); sun.compute(obs)
        moon = ephem.Moon(obs); moon.compute(obs)
        return {"desc": f"태양[{ephem.constellation(sun)[1]}], 달[{ephem.constellation(moon)[1]}]"}
    except Exception:
        return {"desc": "천문 정보 계산 불가"}

def get_real_qimen(year, month, day, hour):
    """lunar_python으로 기문둔갑 길방 계산"""
    try:
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        wealth_pos = lunar.getDayPositionCai()
        joy_pos = lunar.getDayPositionXi()
        d_map = {"震":"동(E)","兌":"서(W)","離":"남(S)","坎":"북(N)","巽":"남동(SE)","坤":"남서(SW)","乾":"북서(NW)","艮":"북동(NE)"}
        return {"desc": f"재물 방향: {d_map.get(wealth_pos, wealth_pos)} / 성공 방향: {d_map.get(joy_pos, joy_pos)}"}
    except Exception:
        return {"desc": "방위 정보 계산 불가"}

# ==========================================
# [사이드바] 사용자 입력 UI
# ==========================================
st.sidebar.title("🔮 AI 운명 전략가")
st.sidebar.markdown("---")
st.sidebar.subheader("📝 고객 정보 입력")

with st.sidebar.form("input_form"):
    name = st.text_input("이름", "홍길동")
    col1, col2 = st.columns(2)
    with col1:
        b_date = st.date_input("생년월일", datetime.date(1990, 3, 1))
    with col2:
        b_time = st.time_input("태어난 시각", datetime.time(14, 30))
    
    submitted = st.form_submit_button("✨ 운명 분석 시작")

st.sidebar.markdown("---")
st.sidebar.info("v3.0 (2026.01) | Powered by Google Gemini")

# ==========================================
# [메인] 실행 로직
# ==========================================
st.title("🌌 AI 운명 전략가 : Master Engine")
st.markdown("##### 사주명리 × 점성술 × 기문둔갑 × 주역 × 타로 통합 분석")
st.divider()

if submitted:
    # 1. API 키 확인 (비어있으면 에러)
    if not MY_API_KEY:
        st.error("🚨 API 키가 설정되지 않았습니다.")
        st.info("💡 힌트: Streamlit Settings > Secrets 에 'GOOGLE_API_KEY'를 입력해주세요.")
    else:
        # 클라이언트 초기화 (여기서 연결해야 안전함)
        try:
            client = genai.Client(api_key=MY_API_KEY)
            
            with st.spinner("🔄 5대 알고리즘이 운명의 코드를 해독 중입니다..."):
                
                # 2. 알고리즘 계산
                now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
                by, bm, bd = b_date.year, b_date.month, b_date.day
                bh, bmin = b_time.hour, b_time.minute
                
                saju = get_real_saju(by, bm, bd, bh, bmin)
                astro = get_real_astrology(by, bm, bd, bh, bmin)
                qimen = get_real_qimen(now.year, now.month, now.day, now.hour)
                iching = get_real_iching()
                tarot = get_real_tarot()
                
                # 3. 대시보드 출력 (Fact Data)
                st.success("✅ 분석 완료! 정밀 데이터가 산출되었습니다.")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🀄 본원(일간)", saju['day_master'])
                col2.metric("🧭 재물/성공 방위", qimen['desc'].split('/')[0].split(':')[1])
                col3.metric("☯️ 주역 괘", iching.split('.')[0])
                col4.metric("🃏 타로 카드", tarot.split('(')[0])
                
                with st.expander("🔍 상세 데이터(Fact Check) 보기"):
                    st.code(f"""
                    [분석 시점] {now.strftime('%Y-%m-%d %H:%M')}
                    [사주팔자] {saju['text']} ({saju['desc']})
                    [천문정보] {astro['desc']}
                    [기문둔갑] {qimen['desc']}
                    [주역결과] {iching}
                    [타로결과] {tarot}
                    """)

                # 4. AI 리포트 생성
                prompt = f"""
                당신은 '수석 운명 전략가'입니다. 다음 팩트 데이터를 바탕으로 {name} 님의 운명 전략 리포트를 작성하세요.
                
                [팩트 데이터]
                - 사주: {saju['text']} ({saju['desc']})
                - 천문: {astro['desc']}
                - 기문둔갑: {qimen['desc']}
                - 주역: {iching}
                - 타로: {tarot}
                - 분석 시점: {now.strftime('%Y년 %m월 %d일 %H시 %M분')}
                
                [작성 가이드]
                - 분량: 1500자 내외 (상세하게)
                - 형식: 마크다운(Markdown)
                - 어조: 전문적, 통찰력 있음, 명확함
                
                [목차]
                1. 🎯 운세 대시보드 (종합 점수 및 영역별 평가)
                2. ⚡ 기문둔갑 시공간 전략 (골든타임 & Action Plan)
                3. 💌 주역과 타로의 심층 메시지 (현재 상황과 조언)
                4. 📋 오늘의 구체적 행동 강령 3가지
                """
                
                st.subheader(f"📜 {name} 님을 위한 심층 전략 리포트")
                report_box = st.empty()
                full_response = ""

              try:
    # 복잡한 거 다 빼고, 가장 안정적인 'gemini-pro'로 고정
    response = client.models.generate_content(
        model="gemini-pro", 
        contents=prompt
    )
    full_response = response.text
    
except Exception as e:
    st.error(f"❌ 분석 실패: {e}")

                # 결과 출력
                if full_response:
                    report_box.markdown(full_response)
                    
                    # 5. HTML 다운로드 기능
                    html_content = f"""
                    <html>
                    <head><title>{name}님의 운세 리포트</title></head>
                    <body style="font-family: serif; padding: 40px; line-height: 1.8;">
                        <h1 style="color: #4B0082;">🔮 {name}님의 운명 전략 리포트</h1>
                        <div style="background: #f4f4f4; padding: 20px; border-radius: 10px;">
                            <h3>📊 팩트 데이터</h3>
                            <p>사주: {saju['text']}<br>기문둔갑: {qimen['desc']}<br>주역: {iching}<br>타로: {tarot}</p>
                        </div>
                        <hr>
                        {full_response.replace('**', '<b>').replace('**', '</b>').replace('\n', '<br>')}
                        <br><br>
                        <div style="text-align: center; color: #888;">Powered by AI Fortune Master Engine v3.0</div>
                    </body>
                    </html>
                    """
                    
                    st.download_button(
                        label="💾 리포트 다운로드 (HTML)",
                        data=html_content,
                        file_name=f"{name}_Fortune_Report.html",
                        mime="text/html"
                    )

        except Exception as e:
            st.error(f"⚠️ 연결 오류: {e}")
            st.error("API 키가 올바르지 않거나, 구글 AI 서버 연결에 문제가 있습니다.")

else:
    st.info("👈 왼쪽 사이드바에 정보를 입력하고 '분석 시작' 버튼을 눌러주세요.")