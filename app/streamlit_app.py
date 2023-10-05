import streamlit as st
from chat import run_chain, build_chain
import uuid

MAX_HISTORY_LENGTH = 5

if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id

st.session_state['llm_chain'] = build_chain()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    
if "chats" not in st.session_state:
    st.session_state.chats = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions" not in st.session_state:
    st.session_state.questions = []

if "answers" not in st.session_state:
    st.session_state.answers = []

if "input" not in st.session_state:
    st.session_state.input = ""



def intro():
    col1, col2, col3 = st.columns([1, 9, 2])
    with col2:
        h2 = 'Welcome to QA chatbot!'
        h4 = 'Ask questions about your documentation.'
        st.write(f"<h2 class='main-header'>{h2}</h2>", unsafe_allow_html=True)
        st.write(f"<h4 class='main-header'>{h4}</h4>", unsafe_allow_html=True)
        st.write(f'User: {st.session_state.user_id}')

    with col3:
        clear = st.button("Clear")
    return clear

clear_chat = intro()

if clear_chat:
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.input = ""
    st.session_state["chat_history"] = []

def handle_input():
    input = st.session_state.input

    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }

    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]

    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state['llm_chain']
    result = run_chain(llm_chain, input, chat_history)
    print(result)
    answer = result['answer']
    chat_history.append((input, answer))
    
    document_list = []
    if 'source_documents' in result:
        for d in result['source_documents']:
            if not (d.metadata['source'] in document_list):
                document_list.append((d.metadata['source']))

    st.session_state.answers.append({
        'answer': result,
        'sources': document_list,
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""

def render_question(md):
    col1, col2 = st.columns([1, 9])
    with col1:
        st.warning('You:')
    with col2:
        q = f"[{md['id']}]  {md['question']}"
        st.warning(q)

def render_answer(answer):
    col1, col2 = st.columns([1, 9])
    with col1:
        st.info('Bot:')
    with col2:
        st.info(answer['answer'])
        # st.info(answer['generated_question'])

def render_sources(sources):
    col1, col2 = st.columns([1,9])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                st.write(s)

def write_chat_message(md):
    chat = st.container()
    with chat:
        render_answer(md['answer'])
        render_sources(md['sources'])
    
        
with st.container():
    for (q, a) in zip(st.session_state.questions, st.session_state.answers):
        render_question(q)
        write_chat_message(a)

st.markdown('---')
input = st.text_input("Please, ask your question.", key="input", on_change=handle_input)
