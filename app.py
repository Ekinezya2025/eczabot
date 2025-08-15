import streamlit as st
import torch
from unsloth import FastLanguageModel

# Sayfa ayarları
st.set_page_config(page_title="💊 Eczabot", page_icon="💊", layout="wide")

# Sayfa arka planı
st.markdown("""
    <style>
    .stApp {
        background-color: #ffe6f0;
    }
    </style>
""", unsafe_allow_html=True)

# Üst kısım: başlık ve logo (sağ üst köşe)
col1, col2 = st.columns([8, 1])
with col1:
    st.title("💊 Eczabot")
    st.caption("İlaçlar hakkında doğru ve anlaşılır bilgi verir. Tıbbi tavsiye yerine geçmez.")
with col2:
    st.image("ekinezyalogo.png", width=50, use_container_width=False)  # Küçük logo

device = "cuda" if torch.cuda.is_available() else "cpu"

@st.cache_resource
def load_model():
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="Ekinezya2025/EczaciLlamaModel",
        max_seq_length=512,
        dtype=torch.float16,
        load_in_4bit=True,
        device_map="auto"
    )
    model = model.to(device)
    FastLanguageModel.for_inference(model)
    return model, tokenizer

model2, tokenizer = load_model()

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context.
Write a response that appropriately completes the request.

### Instruction:
Read the medical information and provide a clear, simplified, and accurate answer so a non-medical person can understand it.
Important: NEVER suggest or recommend any specific medicine. If the user asks which medicine to use, politely refuse and suggest consulting a qualified healthcare professional.
Provide only general information or safety instructions. Avoid repeating sentences.

### Input:
{}

### Response:
"""

st.markdown("""
    <style>
    /* Tüm sayfa arka planı */
    body, .stApp, main, header, footer {
        background-color: #ffe6f0 !important;
    }

    /* Chat container gibi diğer alanlar */
    .css-18e3th9, .css-1lsmgbg {
        background-color: #ffe6f0 !important;
    }

    /* Scroll bar renkleri (opsiyonel) */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #dbb8cb;
        border-radius: 4px;
    }
    </style>

    <script>
    // Light mod görünümü zorlamak
    const app = document.querySelector('.stApp');
    if (app) {
        app.setAttribute('data-theme', 'light');
    }
    </script>
""", unsafe_allow_html=True)






# Chat kutusu: sayfa boyunca ve siyah arka plan
chat_style = """
<div style='background-color:#000000; padding:15px; border-radius:12px; min-height:500px; max-height:90vh; overflow-y:auto;'>
</div>
"""

# Mesaj kutusu
def chat_message_box(msg, role="assistant"):
    bg_color = "#dbb8cb" if role=="assistant" else "#e5e5e5"
    st.markdown(
        f"<div style='background-color:{bg_color}; padding:12px; border-radius:12px; margin-bottom:5px;'>{msg}</div>",
        unsafe_allow_html=True
    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba 👋 Ben Eczabot. İlaçlar hakkında doğru ve anlaşılır bilgiler vermek için buradayım. Size nasıl yardımcı olabilirim?"}
    ]

# Chat alanı
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        chat_message_box(msg["content"], msg["role"])

if prompt := st.chat_input("Sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    chat_message_box(prompt, "user")

    # "Düşünüyor..." göstergesi
    thinking_msg = st.empty()
    thinking_msg.markdown(
        "<div style='background-color:#dbb8cb; padding:12px; border-radius:12px;'>🤔 Düşünüyor...</div>",
        unsafe_allow_html=True
    )

    inputs = tokenizer([alpaca_prompt.format(prompt)], return_tensors="pt").to(device)
    output_ids = model2.generate(
        **inputs,
        max_new_tokens=400,
        do_sample=True,
        top_p=0.9,
        repetition_penalty=1.2
    )
    answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    if "### Response:" in answer:
        answer = answer.split("### Response:")[1].strip()
        answer = answer.lstrip(": ").strip()

    thinking_msg.empty()

    st.session_state.messages.append({"role": "assistant", "content": answer})
    chat_message_box(answer, "assistant")