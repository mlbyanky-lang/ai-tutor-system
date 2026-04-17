import streamlit as st
import google.generativeai as genai
import pandas as pd
import random
import os

# ==========================================
# 1. 초기 설정 및 API 연동
# ==========================================
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="김영편입 노량진 - 종합 AI 튜터", page_icon="📖", layout="wide")

# 단어 데이터 로드 함수
def load_vocab():
    if os.path.exists("voca.csv"):
        df = pd.read_csv("voca.csv")
        # 단어와 뜻을 딕셔너리 형태로 변환
        return dict(zip(df['word'], df['meaning']))
    else:
        return {"Error": "voca.csv 파일을 찾을 수 없습니다."}

# ==========================================
# 2. 사이드바 메뉴
# ==========================================
st.sidebar.title("종합 학습 시스템")
menu = st.sidebar.radio("메뉴 이동", ["📝 일일 어휘 테스트", "📖 AI 구문 분석 튜터"])

# ==========================================
# 3. [메뉴 1] 일일 어휘 테스트 (CSV 연동형)
# ==========================================
if menu == "📝 일일 어휘 테스트":
    st.title("📝 일일 어휘 테스트")
    
    vocab_db = load_vocab()
    
    if "Error" in vocab_db:
        st.error(vocab_db["Error"])
    else:
        if 'current_word' not in st.session_state:
            st.session_state.current_word = random.choice(list(vocab_db.keys()))
            
        st.subheader(f"Q. 다음 단어의 뜻은? : **{st.session_state.current_word}**")
        
        with st.form(key='vocab_form'):
            user_answer = st.text_input("정답 입력:")
            submit_button = st.form_submit_button("제출 및 채점")
            
        if submit_button:
            correct_answer = vocab_db[st.session_state.current_word]
            if user_answer.strip() == str(correct_answer):
                st.success("🎉 정답입니다!")
            else:
                st.error(f"❌ 틀렸습니다. 정답은 '{correct_answer}' 입니다.")
                
        if st.button("🔄 다음 문제 뽑기"):
            st.session_state.current_word = random.choice(list(vocab_db.keys()))
            st.rerun()

# ==========================================
# 4. [메뉴 2] AI 구문 분석 튜터
# ==========================================
elif menu == "📖 AI 구문 분석 튜터":
    st.title("📖 AI 구문 분석 튜터")
    # (기존 구문 분석 코드와 동일하여 생략, 실제 파일에는 전체 코드를 넣어주세요)
    user_input = st.text_area("분석할 영어 문장을 입력하세요:", height=150)
    if st.button("분석 시작하기"):
        # ... (이전 코드의 분석 로직 그대로 유지)
        pass