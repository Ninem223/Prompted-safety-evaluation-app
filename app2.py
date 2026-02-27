import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Medical Safety Eval - Media Version", layout="wide")

# 2. DATA LOADING
@st.cache_data(ttl=600)
def load_questions():
    sheet_id = "1vpSd5TYYw9VUs43L4Hg5iU7nAlrTS7GBXFm2PPu43g4"
    sheet_name = "Questions"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        return pd.read_csv(url)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_questions()

# 3. SESSION STATE
if 'q_idx' not in st.session_state: st.session_state.q_idx = 0
if 'ans_idx' not in st.session_state: st.session_state.ans_idx = 1
if 'results' not in st.session_state: st.session_state.results = []
if 'done' not in st.session_state: st.session_state.done = False

# --- APP INTERFACE ---
if not st.session_state.done and df is not None:
    row = df.iloc[st.session_state.q_idx]
    
    # FIXED HEADER
    st.info(f"### **QUESTION:** {row['Question']}")
    st.write(f"Question {st.session_state.q_idx + 1} of {len(df)} | Evaluating Chatbot {st.session_state.ans_idx} of 4")
    st.divider()
    
    # CHATBOT RESPONSE
    st.subheader(f"Chatbot Response {st.session_state.ans_idx}")
    st.markdown(row[f'Answer{st.session_state.ans_idx}'])
    
    # --- UPDATED TABLE LOGIC ---
    # Matches 'Table1', 'Table2', 'Table3', 'Table4' columns from your sheet
    table_col = f'Table{st.session_state.ans_idx}'
    if table_col in df.columns and pd.notna(row[table_col]):
        table_content = str(row[table_col]).strip()
        if table_content:
            st.markdown("### 📊 Summary Table")
            # Using unsafe_allow_html can sometimes help with complex Markdown rendering
            st.markdown(table_content) 

    # --- IMAGE DISPLAY ---
    img_cols = st.columns(3)
    suffixes = ['A', 'B', 'C']
    for i, s in enumerate(suffixes):
        col_name = f'Image{st.session_state.ans_idx}_{s}'
        if col_name in df.columns:
            img_val = row[col_name]
            if pd.notna(img_val) and str(img_val).strip() != "":
                with img_cols[i]:
                    try:
                        st.image(img_val, use_container_width=True, caption=f"Visual {s}")
                    except:
                        st.warning(f"Unable to load image from {col_name}. Check the URL.")
    
    st.divider()
    
    # GRADING BUTTONS
    st.write("### Rate this response:")
    c1, c2, c3 = st.columns(3)
    
    grade = None
    if c1.button("1 - Unsafe 🚩", use_container_width=True): grade = 1
    if c2.button("2 - Adequate 🟡", use_container_width=True): grade = 2
    if c3.button("3 - Good ✅", use_container_width=True): grade = 3
    
    if grade:
        st.session_state.results.append({
            "Question": row['Question'],
            "Chatbot": st.session_state.ans_idx,
            "Grade": grade
        })
        if st.session_state.ans_idx < 4:
            st.session_state.ans_idx += 1
        else:
            st.session_state.ans_idx = 1
            st.session_state.q_idx += 1
        if st.session_state.q_idx >= len(df):
            st.session_state.done = True
        st.rerun()

# --- COMPLETION SCREEN ---
elif st.session_state.done:
    st.success("🎉 All evaluations complete!")
    res_df = pd.DataFrame(st.session_state.results)
    st.dataframe(res_df, use_container_width=True)
    csv = res_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Grades CSV", csv, "medical_eval_results.csv", "text/csv")