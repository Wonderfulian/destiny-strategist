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
# [보안] API 키 설정
# ==========================================
try:
    # Streamlit Cloud 배포 시
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # 로컬 테스트용 - 여기에 직접 입력 가능
    MY_API_KEY = "" 

# ==========================================
# [함수] 5대 알고리즘 로직
# ==========================================
def get_real_iching():
    """주역 64괘 전체 리스트"""
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
    except Exception as e:
        return {"text": "계산 불가", "day_master": "갑", "desc": f"사주 계산 오류: {str(e)}"}

def get_real_astrology(year, month, day, hour, minute):
    """ephem으로 천문 계산"""
    try:
        obs = ephem.Observer()
        obs.lat, obs.lon = '37.5665', '126.9780' # Seoul
        obs.date = datetime.datetime(year, month, day, hour, minute) - datetime.timedelta(hours=9)
        sun = ephem.Sun(obs); sun.compute(obs)
        moon = ephem.Moon(obs); moon.compute(obs)
        return {"desc": f"태양[{ephem.constellation(sun)[1]}], 달[{ephem.constellation(moon)[1]}]"}
    except Exception as e:
        return {"desc": f"천문 계산 오류: {str(e)}"}

def get_real_qimen(year, month, day, hour):
    """lunar_python으로 기문둔갑 길방 계산"""
    try:
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        wealth_pos = lunar.getDayPositionCai()
        joy_pos = lunar.getDayPositionXi()
        d_map = {"震":"동(E)","兌":"서(W)","離":"남(S)","坎":"북(N)","巽":"남동(SE)","坤":"남서(SW)","乾":"북서(NW)","艮":"북동(NE)"}
        return {"desc": f"재물 방향: {d_map.get(wealth_pos, wealth_pos)} / 성공 방향: {d_map.get(joy_pos, joy_pos)}"}
    except Exception as e:
        return {"desc": f"기문둔갑 계산 오류: {str(e)}"}

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
    # 1. API 키 확인
    if not MY_API_KEY:
        st.error("🚨 API 키가 설정되지 않았습니다.")
        st.info("💡 Streamlit Settings > Secrets에 'GOOGLE_API_KEY'를 입력하거나, 코드 17번째 줄에 직접 입력하세요.")
    else:
        try:
            # =====================================================
            # 🔥 핵심 수정 부분: 클라이언트 초기화
            # =====================================================
            client = genai.Client(api_key=MY_API_KEY)
            
            # 2. 알고리즘 계산
            now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
            by, bm, bd = b_date.year, b_date.month, b_date.day
            bh, bmin = b_time.hour, b_time.minute
            
            with st.spinner("🔮 운명 데이터를 계산하고 있습니다..."):
                saju = get_real_saju(by, bm, bd, bh, bmin)
                astro = get_real_astrology(by, bm, bd, bh, bmin)
                qimen = get_real_qimen(now.year, now.month, now.day, now.hour)
                iching = get_real_iching()
                tarot = get_real_tarot()
            
            # 3. 대시보드 출력
            st.success("✅ 분석 완료! 정밀 데이터가 산출되었습니다.")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🀄 본원(일간)", saju['day_master'])
            
            # 기문둔갑 데이터 안전하게 파싱
            qimen_wealth = qimen['desc'].split('/')[0].split(':')[1].strip() if '/' in qimen['desc'] else "동쪽"
            col2.metric("🧭 재물 방위", qimen_wealth)
            
            col3.metric("☯️ 주역 괘", iching.split('.')[0] if '.' in iching else iching[:10])
            col4.metric("🃏 타로", tarot.split('(')[0].strip() if '(' in tarot else tarot[:20])
            
            with st.expander("🔍 상세 데이터(Fact Check) 보기"):
                st.code(f"""
[분석 시점] {now.strftime('%Y-%m-%d %H:%M (KST)')}
[사주팔자] {saju['text']} 
           {saju['desc']}
[천문정보] {astro['desc']}
[기문둔갑] {qimen['desc']}
[주역결과] {iching}
[타로결과] {tarot}
                """, language="text")

            # 4. AI 리포트 생성 프롬프트
            prompt = f"""
당신은 '수석 운명 전략가'입니다. 다음 팩트 데이터를 바탕으로 {name} 님의 운명 전략 리포트를 작성하세요.

[팩트 데이터]
- 사주팔자: {saju['text']} ({saju['desc']})
- 천문 정보: {astro['desc']}
- 기문둔갑: {qimen['desc']}
- 주역 64괘: {iching}
- 타로 78장: {tarot}
- 분석 시점: {now.strftime('%Y년 %m월 %d일 %H시 %M분 (KST)')}

[작성 가이드]
- 분량: 1500-2000자 (상세하고 깊이 있게)
- 형식: 마크다운(Markdown) - ##, **, - 등 활용
- 어조: 전문적이면서도 따뜻한 멘토의 말투

[필수 목차]
## 🎯 운세 대시보드
- 오늘의 종합 운세 점수 (100점 만점)
- 애정운, 재물운, 사업운, 건강운 각각 평가

## ⚡ 기문둔갑 시공간 전략
- 오늘의 골든타임 (몇 시가 가장 좋은지 구체적으로)
- 길방 활용법: {qimen['desc']} 이 방향을 어떻게 활용할지
- 구체적인 행동 계획

## 💌 주역과 타로의 심층 메시지
- 주역 {iching}이 전하는 의미와 조언
- 타로 {tarot}의 해석과 실천 방법
- 두 점술의 공통 메시지

## 📋 오늘의 행동 강령
- 꼭 해야 할 일 3가지 (구체적으로)
- 절대 피해야 할 일 3가지
- 오늘의 행운 아이템 (색상, 숫자, 음식, 방향 등)

각 섹션을 풍부하고 구체적으로 작성하되, 실용적이고 실행 가능한 조언을 담아주세요.
"""
            
            st.subheader(f"📜 {name} 님을 위한 심층 전략 리포트")
            
            # =====================================================
            # 🔥 핵심 수정 부분 2: Gemini API 호출 (2026년 1월 방식)
            # =====================================================
            with st.spinner("⚡ Gemini AI가 우주의 기운을 분석 중입니다... (약 10-15초 소요)"):
                try:
                    # 방법 1: gemini-2.5-flash (2026년 1월 권장)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    full_response = response.text
                    
                except Exception as e1:
                    st.warning(f"⚠️ gemini-2.5-flash 오류: {str(e1)[:100]}")
                    st.info("gemini-1.5-pro로 재시도 중...")
                    
                    try:
                        # 방법 2: gemini-1.5-pro (백업)
                        response = client.models.generate_content(
                            model="gemini-1.5-pro",
                            contents=prompt
                        )
                        full_response = response.text
                        
                    except Exception as e2:
                        st.error(f"❌ 모든 모델 접속 실패")
                        st.error(f"오류 상세: {str(e2)}")
                        st.info("""
                        **문제 해결 방법:**
                        1. API 키가 올바른지 확인 (https://aistudio.google.com/apikey)
                        2. API 키에 Gemini API 사용 권한이 있는지 확인
                        3. 할당량(Quota)을 초과하지 않았는지 확인
                        4. 인터넷 연결 상태 확인
                        """)
                        full_response = ""

            # 6. 결과 출력
            if full_response:
                st.markdown(full_response)
                
                # HTML 다운로드 파일 생성
                html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}님의 운세 리포트</title>
    <style>
        body {{
            font-family: 'Noto Serif KR', serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 40px;
            line-height: 1.8;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            padding: 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            border-bottom: 4px solid #764ba2;
            padding-bottom: 20px;
        }}
        h2 {{
            color: #764ba2;
            border-left: 6px solid #667eea;
            padding-left: 15px;
            margin-top: 30px;
        }}
        .data-box {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #667eea;
        }}
        strong {{
            color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 {name}님의 운명 전략 리포트</h1>
        <p style="text-align: center; color: #666;">분석 시점: {now.strftime('%Y년 %m월 %d일 %H시 %M분 (KST)')}</p>
        
        <div class="data-box">
            <h3>📊 팩트 데이터</h3>
            <p><strong>🀄 사주팔자:</strong> {saju['text']}</p>
            <p><strong>📖 사주 해석:</strong> {saju['desc']}</p>
            <p><strong>🌙 천문:</strong> {astro['desc']}</p>
            <p><strong>🧭 기문둔갑:</strong> {qimen['desc']}</p>
            <p><strong>☯️ 주역:</strong> {iching}</p>
            <p><strong>🃏 타로:</strong> {tarot}</p>
        </div>
        
        <hr>
        
        {full_response.replace('##', '<h2>').replace('**', '<strong>').replace('**', '</strong>').replace('- ', '<br>• ').replace('\n', '<br>')}
        
        <br><br>
        <div style="text-align: center; color: #999; font-size: 0.9em; border-top: 2px solid #eee; padding-top: 20px;">
            <p>Powered by Google Gen AI SDK (2026년 1월)</p>
            <p>AI Fortune Master Engine v3.0</p>
        </div>
    </div>
</body>
</html>
"""
                
                st.download_button(
                    label="💾 리포트 다운로드 (HTML)",
                    data=html_content,
                    file_name=f"{name}_Fortune_Report_{now.strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html"
                )
                
                st.success("✅ 분석이 완료되었습니다! 위의 버튼을 클릭하여 리포트를 다운로드하세요.")

        except Exception as e:
            st.error(f"⚠️ 시스템 오류가 발생했습니다.")
            st.error(f"오류 내용: {str(e)}")
            st.info("""
            **디버깅 힌트:**
            - API 키가 올바르게 설정되었는지 확인하세요
            - lunar_python 라이브러리가 설치되었는지 확인하세요
            - 인터넷 연결을 확인하세요
            """)
            
            # 디버깅용 상세 정보
            import traceback
            with st.expander("🔧 개발자용 상세 오류 로그"):
                st.code(traceback.format_exc())

else:
    # 초기 화면
    st.info("👈 왼쪽 사이드바에 정보를 입력하고 '✨ 운명 분석 시작' 버튼을 눌러주세요.")
    
    st.markdown("""
    ### 🌟 이 앱의 특징
    
    - **정확한 사주팔자 계산**: lunar_python 라이브러리 사용
    - **실시간 천문 분석**: ephem으로 태양/달의 위치 계산
    - **기문둔갑 길방 계산**: 오늘의 재물 방향과 성공 방향 제시
    - **주역 64괘**: 전통 동양 철학의 지혜
    - **타로 78장**: 서양 점술의 통찰
    - **AI 종합 분석**: Google Gemini가 모든 정보를 통합하여 맞춤형 조언 제공
    
    ---
    
    #### 📋 사용 방법
    1. 왼쪽 사이드바에 이름과 생년월일시를 입력
    2. '운명 분석 시작' 버튼 클릭
    3. AI가 5가지 점술을 종합하여 리포트 작성
    4. 결과를 확인하고 HTML로 다운로드
    
    #### ⚙️ 설정 방법 (Streamlit Cloud 배포 시)
    1. Streamlit 앱 설정에서 Secrets 메뉴 선택
    2. 다음 형식으로 API 키 입력:
    ```
    GOOGLE_API_KEY = "your-api-key-here"
    ```
    3. API 키 발급: https://aistudio.google.com/apikey
    """)
    
    st.warning("⚠️ 이 앱은 참고용 콘텐츠를 제공하며, 실제 운세나 미래를 예측하는 것이 아닙니다.")