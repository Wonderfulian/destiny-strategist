# ==========================================
# [기본 설정] 페이지 디자인 & CSS (개선판)
# ==========================================
st.set_page_config(
    page_title="AI 운명 전략가 (V5.0 Final)",
    page_icon="🔮",
    layout="wide"
)

# [CSS] 가독성 최적화 테마
st.markdown("""
    <style>
    /* 메인 배경 */
    .stApp { 
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); 
        color: #ffffff;  /* 기존 #e0e0e0에서 순백으로 변경 */
    }
    
    /* 사이드바 */
    [data-testid="stSidebar"] { 
        background-color: #1a1a2e; 
        border-right: 2px solid #ffd700;  /* 경계선 강조 */
    }
    
    /* 제목 */
    h1, h2, h3 { 
        color: #ffd700 !important; 
        font-family: 'Times New Roman', serif; 
        text-shadow: 0 0 15px rgba(255, 215, 0, 0.5);  /* 그림자 강화 */
        font-weight: bold !important;
    }
    
    /* 일반 텍스트 가독성 향상 */
    p, li, span, div {
        color: #f0f0f0 !important;  /* 거의 흰색 */
        line-height: 1.8;
        font-size: 16px;
    }
    
    /* 본문 폭 제한 (가독성 향상) */
    .block-container {
        max-width: 1200px !important;  /* 기본 넓이 제한 */
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* 마크다운 본문 폭 더 좁게 */
    .stMarkdown {
        max-width: 900px;  /* 본문은 더 좁게 */
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 메트릭 값 */
    div[data-testid="stMetricValue"] { 
        color: #00ffff !important;  /* 청록색으로 더 밝게 */
        font-weight: bold; 
        font-size: 24px !important;
    }
    
    /* 메트릭 라벨 */
    div[data-testid="stMetricLabel"] {
        color: #ffd700 !important;
        font-weight: 600;
    }
    
    /* 버튼 */
    .stButton>button { 
        background: linear-gradient(90deg, #FFD700 0%, #FDB931 100%); 
        color: #000000 !important;  /* 검정색으로 대비 강화 */
        border: none; 
        border-radius: 20px; 
        font-weight: bold;
        font-size: 16px;
        padding: 10px 24px;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #FDB931 0%, #FFD700 100%);
        box-shadow: 0 6px 16px rgba(255, 215, 0, 0.5);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    
    /* Info 박스 */
    .stInfo {
        background-color: rgba(0, 119, 182, 0.2) !important;
        border-left: 4px solid #00d2ff !important;
        color: #ffffff !important;
        padding: 1rem !important;
    }
    
    /* Success 박스 */
    .stSuccess {
        background-color: rgba(0, 200, 83, 0.2) !important;
        border-left: 4px solid #00ff88 !important;
        color: #ffffff !important;
    }
    
    /* Warning 박스 */
    .stWarning {
        background-color: rgba(255, 193, 7, 0.2) !important;
        border-left: 4px solid #ffd700 !important;
        color: #ffffff !important;
    }
    
    /* Error 박스 */
    .stError {
        background-color: rgba(255, 75, 75, 0.2) !important;
        border-left: 4px solid #ff4444 !important;
        color: #ffffff !important;
    }
    
    /* 코드 블록 */
    code {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffd700 !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* 구분선 */
    hr {
        border-color: rgba(255, 215, 0, 0.3) !important;
        margin: 2rem 0;
    }
    
    /* 입력 필드 */
    input, textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 8px !important;
    }
    
    input:focus, textarea:focus {
        border-color: #ffd700 !important;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.3) !important;
    }
    
    /* 라벨 */
    label {
        color: #f0f0f0 !important;
        font-weight: 500 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 215, 0, 0.1) !important;
        color: #ffd700 !important;
        border-radius: 8px;
        font-weight: bold;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 215, 0, 0.2);
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* 테이블 */
    table {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: #f0f0f0 !important;
    }
    
    th {
        background-color: rgba(255, 215, 0, 0.2) !important;
        color: #ffd700 !important;
        font-weight: bold;
    }
    
    /* 링크 */
    a {
        color: #00d2ff !important;
        text-decoration: none;
    }
    
    a:hover {
        color: #ffd700 !important;
        text-decoration: underline;
    }
    
    /* 스피너 */
    .stSpinner > div {
        border-top-color: #ffd700 !important;
    }
    
    /* Form 요소 */
    [data-testid="stForm"] {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 215, 0, 0.2);
    }
    
    /* 메인 타이틀 추가 스타일 */
    .main-title {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, rgba(255,215,0,0.1), rgba(0,210,255,0.1));
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    /* 섹션 구분 */
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent, #ffd700, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* 강조 텍스트 */
    strong, b {
        color: #ffd700 !important;
        font-weight: 700;
    }
    
    /* 리스트 아이템 */
    ul, ol {
        padding-left: 2rem;
    }
    
    li {
        margin-bottom: 0.5rem;
        color: #f0f0f0 !important;
    }
    
    /* 인용구 */
    blockquote {
        border-left: 4px solid #ffd700;
        padding-left: 1rem;
        margin-left: 0;
        color: #f0f0f0 !important;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)