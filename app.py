import streamlit as st
from openai import OpenAI
import time

# -------------------------------------------------------------------------
# 1. 페이지 기본 설정
# -------------------------------------------------------------------------
st.set_page_config(page_title="가나다벗 - AI 글쓰기 도우미", layout="wide")

# -------------------------------------------------------------------------
# 2. 비밀번호 및 API 설정
# -------------------------------------------------------------------------
try:
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None
except FileNotFoundError:
    st.error("secrets.toml 파일을 찾을 수 없습니다.")
    st.stop()
except KeyError:
    st.error("secrets.toml 설정 오류")
    st.stop()

# -------------------------------------------------------------------------
# 3. 디자인 CSS (요청하신 사항 완벽 반영)
# -------------------------------------------------------------------------
st.markdown("""
<style>
    /* 폰트 설정 */
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }

    /* 전체 배경 흰색 */
    .stApp {
        background-color: #ffffff;
    }
    
    /* 헤더 숨김 */
    header {visibility: hidden;}

    /* -----------------------
       입력창 스타일 (로그인 & 메인 공통)
       ----------------------- */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff;
        border: 1px solid #e0e0e0 !important;
        border-radius: 4px !important;
        color: #333333;
        padding: 12px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #000000 !important;
        box-shadow: none !important;
    }

    /* -----------------------
       버튼 스타일 (기본: 검은색)
       ----------------------- */
    div.stButton > button {
        width: 100%;
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 4px !important; /* 사각형에 가깝게 수정 */
        height: 50px;
        font-weight: 600;
        border: none;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }

    /* -----------------------
       [중요] 비활성화 버튼 스타일 (회색)
       Streamlit이 disabled 처리할 때 이 스타일을 따라갑니다.
       ----------------------- */
    div.stButton > button:disabled {
        background-color: #f0f0f0 !important;
        color: #aaaaaa !important;
        cursor: not-allowed;
        border: 1px solid #e0e0e0 !important;
    }

    /* -----------------------
       탭 스타일
       ----------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #e0e0e0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 0px;
        color: #999999;
        font-size: 16px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #000000 !important;
        font-weight: 700;
        border-bottom: 2px solid #000000 !important;
    }

    /* -----------------------
       로그인 타이틀 스타일
       ----------------------- */
    .login-container {
        margin-top: 120px; /* 상단 여백 확보 */
        text-align: center;
        margin-bottom: 40px;
    }
    .login-title {
        font-size: 36px; /* 폰트 사이즈 키움 */
        font-weight: 700;
        color: #000000;
        margin-bottom: 12px;
        letter-spacing: -0.5px;
    }
    .login-subtitle {
        font-size: 15px;
        color: #888888;
        font-weight: 400;
    }
    
    /* 저작권 문구 */
    .footer-text {
        font-size: 12px;
        color: #cccccc;
        text-align: center;
        margin-top: 80px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 4. 세션 상태 관리
# -------------------------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# -------------------------------------------------------------------------
# 5. 화면 로직
# -------------------------------------------------------------------------

if not st.session_state.authenticated:
    # === [로그인 화면] ===
    
    # 1. 가로폭 조정: 중앙 컬럼(col2)을 1.5로 늘려서 타이틀 줄바꿈 방지
    col1, col2, col3 = st.columns([1, 1.5, 1]) 

    with col2:
        # 타이틀 영역
        st.markdown("""
            <div class='login-container'>
                <div class='login-title'>AI 글쓰기 도우미, 가나다벗</div>
                <div class='login-subtitle'>브랜드 보이스 관리를 위한 AI 어시스턴트</div>
            </div>
        """, unsafe_allow_html=True)

        # 2. 로그인 입력창 (비밀번호만 남김)
        # label_visibility="collapsed"로 라벨 숨김
        password_input = st.text_input("Password", type="password", placeholder="비밀번호를 입력하세요", label_visibility="collapsed")
        
        st.write("") # 간격 조절
        
        # 3. 버튼 활성화 로직
        # 비밀번호가 비어있으면(False) -> 버튼 disabled=True (비활성)
        # 비밀번호가 있으면(True) -> 버튼 disabled=False (활성)
        is_disabled = (password_input == "")

        if st.button("시작하기 →", disabled=is_disabled):
            if password_input == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")

        # 4. 하단 링크 삭제됨 (저작권 문구만 남김)
        st.markdown("<div class='footer-text'>© 2024 BrandSite Inc. All rights reserved.</div>", unsafe_allow_html=True)


else:
    # === [메인 앱 화면] (기존 유지) ===
    
    h_col1, h_col2 = st.columns([8, 1])
    with h_col1:
        st.markdown("<div style='font-size: 20px; font-weight: 700; color: #000;'>AI 글쓰기 도우미, 가나다벗</div>", unsafe_allow_html=True)
    with h_col2:
        if st.button("로그아웃"):
            st.session_state.authenticated = False
            st.rerun()

    st.write("") 

    tab1, tab2, tab3 = st.tabs(["초안 검토", "초안 작성", "라이팅 가이드라인"])

    # --- TAB 1 ---
    with tab1:
        st.markdown("<h1 style='font-size: 32px; font-weight: 700; margin-top: 20px;'>Draft Review</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; margin-bottom: 40px;'>작성하신 글을 입력하면 가이드라인에 맞춰 수정해드립니다.</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; height: 1px; background: #333; margin-bottom: 30px;'>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("##### **나의 초안**")
            user_text = st.text_area("입력창", placeholder="여기에 초안을 입력하세요...", height=400, label_visibility="collapsed")
            st.write("")
            if st.button("검토 요청"):
                if user_text:
                    if client:
                        with st.spinner("AI가 분석 중입니다..."):
                            time.sleep(1) 
                            st.session_state['review_result'] = "AI 수정 결과 예시입니다.\n\nAPI가 연결되면 실제 답변이 나옵니다."
                    else:
                        st.error("API Key가 없습니다.")
                else:
                    st.warning("내용을 입력해주세요.")

        with col_right:
            st.markdown("##### **AI 제안 문구**")
            res_container = st.container(border=True)
            with res_container:
                if 'review_result' in st.session_state:
                    st.write(st.session_state['review_result'])
                else:
                    st.markdown("""
                        <div style='height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #aaa;'>
                            <div style='font-size: 40px;'>✨</div>
                            <div style='margin-top: 10px;'>검토 요청 결과가<br>여기에 표시됩니다.</div>
                        </div>
                    """, unsafe_allow_html=True)

    # --- TAB 2 ---
    with tab2:
        st.markdown("<h1 style='font-size: 32px; font-weight: 700; margin-top: 20px;'>Draft Generation</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666; margin-bottom: 40px;'>키워드를 입력하면 초안을 만들어드립니다.</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; height: 1px; background: #333; margin-bottom: 30px;'>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### **주제 / 키워드**")
            st.text_area("키워드", height=400, label_visibility="collapsed")
            st.write("")
            st.button("작성하기 →")
        with c2:
            st.markdown("##### **결과물**")
            st.container(border=True).markdown("<div style='height: 400px;'></div>", unsafe_allow_html=True)

    # --- TAB 3 ---
    with tab3:
        st.markdown("<h1 style='font-size: 32px; font-weight: 700; margin-top: 20px;'>Guidelines</h1>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; height: 3px; background: #000; margin-bottom: 30px;'>", unsafe_allow_html=True)
        st.write("가이드라인 내용...")
