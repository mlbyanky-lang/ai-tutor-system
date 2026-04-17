import streamlit as st
import google.generativeai as genai
import pandas as pd
import random
import os

# 1. 초기 설정
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="김영편입 노량진 - 종합 AI 튜터", page_icon="📖", layout="wide")

def load_vocab():
    if os.path.exists("voca.csv"):
        # 인코딩 문제 방지를 위해 utf-8-sig 사용
        df = pd.read_csv("voca.csv", encoding='utf-8-sig')
        return df
    else:
        return None

# 2. 사이드바
st.sidebar.title("종합 학습 시스템")
menu = st.sidebar.radio("메뉴 이동", ["📝 객관식 어휘 테스트", "📖 AI 구문 분석 튜터"])

# 3. [메뉴 1] 객관식 어휘 테스트
if menu == "📝 객관식 어휘 테스트":
    st.title("📝 객관식 어휘 테스트")
    df = load_vocab()
    
    if df is None:
        st.error("voca.csv 파일을 찾을 수 없습니다.")
    else:
        # 새로운 문제 생성 로직
        if 'quiz_data' not in st.session_state:
            # 문제 단어 선정
            target_row = df.sample(n=1).iloc[0]
            question_word = target_row['word']
            correct_answer = target_row['meaning']
            
            # 오답 후보 선정 (현재 단어 제외하고 3개 무작위 추출)
            distractors = df[df['meaning'] != correct_answer]['meaning'].sample(n=3).tolist()
            
            # 보기 4개 섞기
            options = distractors + [correct_answer]
            random.shuffle(options)
            
            st.session_state.quiz_data = {
                'word': question_word,
                'answer': correct_answer,
                'options': options,
                'solved': False
            }

        quiz = st.session_state.quiz_data
        st.subheader(f"Q. 다음 단어의 알맞은 뜻을 고르세요: **{quiz['word']}**")

        # 객관식 버튼 생성
        for option in quiz['options']:
            if st.button(option, key=option, use_container_width=True):
                quiz['solved'] = True
                if option == quiz['answer']:
                    st.success(f"⭕ 정답입니다! : {option}")
                else:
                    st.error(f"❌ 틀렸습니다. 정답은 '{quiz['answer']}' 입니다.")

        # 다음 문제 버튼
        if quiz['solved']:
            if st.button("➡️ 다음 문제로 넘어가기"):
                del st.session_state.quiz_data
                st.rerun()

# 4. [메뉴 2] AI 구문 분석 튜터 (기존 로직 동일)
elif menu == "📖 AI 구문 분석 튜터":
    st.title("📖 AI 구문 분석 튜터")
    # ... (기존 구문 분석 코드 붙여넣기)
    user_input = st.text_area("분석할 영어 문장을 입력하세요:", height=150)
    if st.button("분석 시작하기"):
        # AI 분석 로직...
        pass