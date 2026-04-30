import streamlit as st
import google.generativeai as genai
import pandas as pd
import random
import os

# ==========================================
# 1. AI 설정 및 보안 (유료 플랜 대응)
# ==========================================
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    # 과금 시 더 빠르고 안정적인 모델로 설정 가능
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. 관리자에게 문의하세요.")

st.set_page_config(page_title="김영편입 노량진 - 종합 AI 관리 시스템", page_icon="🚀", layout="wide")

# 폴더 내의 모든 CSV 파일 목록을 가져오는 함수
def get_all_voca_files():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    return files

# 선택된 CSV 파일에서 데이터를 읽어오는 함수
def load_selected_voca(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        return df
    except Exception as e:
        return None

# ==========================================
# 2. 사이드바 (메뉴 및 단어장 선택)
# ==========================================
st.sidebar.title("🛠️ 학습 설정")
menu = st.sidebar.radio("메뉴 이동", ["📝 맞춤형 어휘 테스트", "📖 AI 구문 분석 튜터"])

if menu == "📝 맞춤형 어휘 테스트":
    st.sidebar.divider()
    all_files = get_all_voca_files()
    if all_files:
        selected_file = st.sidebar.selectbox("📖 단어장 선택", all_files)
    else:
        st.sidebar.error("데이터 파일(.csv)이 없습니다.")

# ==========================================
# 3. [메뉴 1] 어휘 테스트 (멀티 파일 대응)
# ==========================================
if menu == "📝 맞춤형 어휘 테스트":
    st.title("📝 맞춤형 어휘 테스트")
    
    df = load_selected_voca(selected_file)
    
    if df is not None:
        # 1) DAY 선택 (해당 파일 내의 DAY 목록)
        day_list = sorted(df['day'].unique())
        selected_day = st.selectbox(f"📍 {selected_file} - 학습 범위를 선택하세요:", day_list)
        
        filtered_df = df[df['day'] == selected_day]

        # 파일이나 DAY가 바뀌면 문제 초기화
        state_key = f"quiz_{selected_file}_{selected_day}"
        if 'current_state_key' not in st.session_state or st.session_state.current_state_key != state_key:
            st.session_state.current_state_key = state_key
            if 'quiz_data' in st.session_state:
                del st.session_state.quiz_data

        if 'quiz_data' not in st.session_state:
            target_row = filtered_df.sample(n=1).iloc[0]
            # 오답은 '현재 선택된 파일' 전체에서 무작위 추출
            distractors = df[df['meaning'] != target_row['meaning']]['meaning'].sample(n=3).tolist()
            options = distractors + [target_row['meaning']]
            random.shuffle(options)
            st.session_state.quiz_data = {'word': target_row['word'], 'answer': target_row['meaning'], 'options': options, 'solved': False}

        # 퀴즈 UI
        quiz = st.session_state.quiz_data
        st.divider()
        st.subheader(f"Q. 다음 단어의 뜻은? : **{quiz['word']}**")
        
        cols = st.columns(2)
        for i, option in enumerate(quiz['options']):
            if cols[i%2].button(option, key=f"opt_{i}", use_container_width=True):
                quiz['solved'] = True
                if option == quiz['answer']: st.success("🎉 정답!")
                else: st.error(f"❌ 오답! 정답: {quiz['answer']}")

        if quiz['solved'] and st.button("➡️ 다음 문제", type="primary"):
            del st.session_state.quiz_data
            st.rerun()

# ==========================================
# 4. [메뉴 2] AI 구문 분석 (안정성 강화)
# ==========================================
elif menu == "📖 AI 구문 분석 튜터":
    st.title("📖 AI 구문 분석 튜터")
    st.info("💡 유료 플랜 적용 시 대기 시간 없이 즉시 분석됩니다.")
    
    user_input = st.text_area("분석할 영어 문장을 입력하세요:", height=150)
    
    if st.button("🔍 전문 분석 시작"):
        if user_input:
            with st.spinner('AI가 구문을 정밀 분석 중입니다...'):
                try:
                    # 유료 플랜에서는 응답 속도가 훨씬 빨라집니다.
                    response = model.generate_content("다음 문장을 구문 분석, 직독직해, 자연스러운 해석, 핵심 문법 순으로 설명해줘:\n" + user_input)
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    if "429" in str(e):
                        st.warning("⚠️ 현재 접속자가 많아 잠시 지연되고 있습니다. 30초 후 다시 시도하거나 유료 플랜으로 전환하세요.")
                    else:
                        st.error(f"분석 중 오류 발생: {e}")
