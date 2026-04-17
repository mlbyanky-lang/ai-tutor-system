import streamlit as st
import google.generativeai as genai
import pandas as pd
import random
import os

# 1. 초기 설정 (Secrets 연동)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="김영편입 노량진 - 종합 AI 튜터", page_icon="📖", layout="wide")

def load_vocab():
    if os.path.exists("voca.csv"):
        # 인코딩 문제 방지를 위해 utf-8-sig 사용
        df = pd.read_csv("voca.csv", encoding='utf-8-sig')
        return df
    return None

# 2. 사이드바 메뉴
st.sidebar.title("종합 학습 시스템")
menu = st.sidebar.radio("메뉴 이동", ["📝 맞춤형 어휘 테스트", "📖 AI 구문 분석 튜터"])

# 3. [메뉴 1] 어휘 테스트 (범위 선택 기능 포함)
if menu == "📝 맞춤형 어휘 테스트":
    st.title("📝 맞춤형 어휘 테스트")
    df = load_vocab()
    
    if df is None:
        st.error("voca.csv 파일을 찾을 수 없습니다.")
    else:
        # 1) 범위 선택 레이아웃
        st.markdown("### 🎯 학습 범위를 선택하세요")
        day_list = sorted(df['day'].unique())  # 엑셀의 'day' 컬럼에서 중복 없이 목록 추출
        selected_day = st.selectbox("학습할 DAY를 선택하세요:", day_list)
        
        # 선택된 DAY에 해당하는 단어들만 필터링
        filtered_df = df[df['day'] == selected_day]
        
        st.info(f"현재 **{selected_day}** 범위에서 문제가 출제됩니다. (총 {len(filtered_df)}단어)")

        # 2) 문제 생성 로직 (세션 상태 활용)
        # 선택한 DAY가 바뀌면 기존 퀴즈 데이터를 삭제하고 새로 고침
        if 'last_selected_day' not in st.session_state or st.session_state.last_selected_day != selected_day:
            st.session_state.last_selected_day = selected_day
            if 'quiz_data' in st.session_state:
                del st.session_state.quiz_data

        if 'quiz_data' not in st.session_state:
            target_row = filtered_df.sample(n=1).iloc[0]
            question_word = target_row['word']
            correct_answer = target_row['meaning']
            
            # 전체 단어장(df)에서 오답 후보 3개 추출
            distractors = df[df['meaning'] != correct_answer]['meaning'].sample(n=3).tolist()
            options = distractors + [correct_answer]
            random.shuffle(options)
            
            st.session_state.quiz_data = {
                'word': question_word,
                'answer': correct_answer,
                'options': options,
                'solved': False
            }

        # 3) 퀴즈 화면 출력
        quiz = st.session_state.quiz_data
        st.divider()
        st.subheader(f"Q. 다음 단어의 알맞은 뜻은? : **{quiz['word']}**")

        # 보기 출력 (가로 2개씩 2줄 배치)
        col1, col2 = st.columns(2)
        for i, option in enumerate(quiz['options']):
            target_col = col1 if i % 2 == 0 else col2
            if target_col.button(option, key=f"btn_{option}", use_container_width=True):
                quiz['solved'] = True
                if option == quiz['answer']:
                    st.success(f"⭕ 정답입니다! : {option}")
                else:
                    st.error(f"❌ 틀렸습니다. 정답은 '{quiz['answer']}' 입니다.")

        # 다음 문제 버튼
        if quiz['solved']:
            if st.button("➡️ 다음 문제로 넘어가기", type="primary"):
                del st.session_state.quiz_data
                st.rerun()

# 4. [메뉴 2] AI 구문 분석 튜터 (기존 로직 유지)
elif menu == "📖 AI 구문 분석 튜터":
    st.title("📖 AI 구문 분석 튜터")
    SYSTEM_PROMPT = """
    너는 편입 영어 수험생을 1대1로 밀착 관리하는 '구문 분석 및 해석 전문 AI 튜터'야. 학생이 영어 문장을 입력하면, 아래의 엄격한 양식에 맞춰서 답변을 출력해 줘.
    1. 문장 구조 분석 / 2. 직독직해 / 3. 자연스러운 해석 / 4. 핵심 어휘 및 문법 포인트
    """
    user_input = st.text_area("분석할 영어 문장을 입력하세요:", height=150)
    if st.button("분석 시작하기"):
        if user_input:
            with st.spinner('분석 중...'):
                try:
                    full_prompt = SYSTEM_PROMPT + "\n\n" + user_input
                    response = model.generate_content(full_prompt)
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류 발생: {e}")