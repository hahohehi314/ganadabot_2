import streamlit as st
from openai import OpenAI
import time

# [중요] 이 설정이 가장 먼저 와야 합니다!
st.set_page_config(page_title="UX 라이팅 교정 툴", layout="wide")

# =========================
# 1. 기본 설정 값
# =========================

# 비밀번호를 secrets에서 가져옴 (보안 강화)
APP_PASSWORD = st.secrets["APP_PASSWORD"]

# 👉 OpenAI Playground에서 만든 Assistant ID
ASSISTANT_ID = "asst_ACbvsCz6RBpAJVUQwDjR0zVv"

# =========================
# 2. OpenAI Client 생성
# =========================

# st.secrets 에서 API Key 불러오기
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def ask_assistant(user_input: str) -> str:
    """
    OpenAI Assistants API를 사용해서
    사용자 입력을 Assistant에게 보내고
    최종 답변 텍스트만 반환하는 함수
    """

    # 1) Thread 생성
    thread = client.beta.threads.create()

    # 2) 사용자 메시지 추가
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # 3) Run 실행
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    # 4) Run 완료될 때까지 대기
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        time.sleep(0.5)

    # 5) 메시지 가져오기 (Assistant의 마지막 답변)
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # 가장 마지막 assistant 메시지 추출
    for msg in messages.data:
        if msg.role == "assistant":
            return msg.content[0].text.value

    return "응답을 가져오지 못했습니다."


# =========================
# 3. 로그인 화면
# =========================

# 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.title("✍️ UX 라이팅 교정 툴")

# 로그인 안 된 상태
if not st.session_state.authenticated:
    password = st.text_input("비밀번호를 입력하세요", type="password")

    if password:
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("접근 권한이 없습니다")

    # 로그인 실패 시 여기서 종료
    st.stop()


# =========================
# 4. 메인 탭 레이아웃
# =========================

tabs = st.tabs(["초안 검토", "초안 작성", "가이드라인"])


# =========================
# 5. 초안 검토 탭
# =========================
with tabs[0]:
    st.subheader("🧐 초안 검토")

    col1, col2 = st.columns(2)

    with col1:
        original_text = st.text_area(
            "원본 텍스트를 입력하세요",
            height=300,
            placeholder="검토할 UX 문구를 붙여넣어 주세요"
        )

        review_button = st.button("검토 요청")

    with col2:
        st.markdown("### ✨ 수정 제안 결과")

        if review_button and original_text:
            with st.spinner("AI가 문구를 다듬고 있어요..."):
                prompt = f"""
너는 10년차 UX 라이터의 관점에서 문구를 교정하는 전문가야.
아래 UX 문구를 더 명확하고, 친절하고, 사용자 중심적으로 다듬어줘.

[원문]
{original_text}
"""
                result = ask_assistant(prompt)

            st.text_area(
                "AI 수정 결과",
                value=result,
                height=300
            )


# =========================
# 6. 초안 작성 탭
# =========================
with tabs[1]:
    st.subheader("✏️ 초안 작성")

    topic = st.text_area(
        "주제 또는 키워드를 입력하세요",
        height=150,
        placeholder="예: 회원가입 완료 안내 문구"
    )

    write_button = st.button("초안 생성")

    if write_button and topic:
        with st.spinner("초안을 작성 중입니다..."):
            prompt = f"""
너는 시니어 UX 라이터야.
아래 주제에 맞는 UX 라이팅 초안을 작성해줘.
톤은 친절하고 명확하게.

[주제]
{topic}
"""
            draft = ask_assistant(prompt)

        st.text_area(
            "작성된 초안",
            value=draft,
            height=300
        )


# =========================
# 7. 가이드라인 탭
# =========================
with tabs[2]:
    st.subheader("📘 가이드라인")

    st.write("현재 등록된 가이드라인입니다.")

    # 예시용 PDF (실제 파일로 교체 가능)
    pdf_bytes = b"%PDF-1.4\n% Dummy PDF file"

    st.download_button(
        label="가이드라인 PDF 다운로드",
        data=pdf_bytes,
        file_name="ux_writing_guideline.pdf",
        mime="application/pdf"
    )
