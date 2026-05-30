import streamlit as st
import subprocess
import sys

# 必要な外部ライブラリ（画像切り抜き用など）を自動インストールする設定
try:
    from streamlit_image_cropper import st_cropper
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit-image-cropper", "Pillow"])
    from streamlit_image_cropper import st_cropper
    from PIL import Image

# ページの初期設定
st.set_page_config(page_title="オリジナルカレンダー注文", layout="centered")

# 🎨 スタイリッシュなデザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #f7f9fa; }
    h1, h2, h3 { color: #2c3e50 !important; font-weight: 700; }
    .step-box { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .nav-box { display: flex; justify-content: space-between; margin-top: 20px; }
    div.stButton > button { border-radius: 6px !important; font-weight: bold !important; height: 45px; }
    </style>
""", unsafe_allow_html=True)

st.title("📅 オリジナルカレンダー作成・注文")
st.caption("お気に入りの写真を調整して、あなただけのカレンダーを作りましょう")

# セッション状態（画面の進捗など）の初期化
if "c_step" not in st.session_state: st.session_state.c_step = 1
if "order_data" not in st.session_state:
    st.session_state.order_data = {
        "image": None, "cropped_image": None, "template": "A", "quantity": 1,
        "name": "", "zip": "", "address": "", "tel": "", "email": ""
    }

c_step = st.session_state.c_step
data = st.session_state.order_data

# 現在のステップを表示するバー
steps_names = ["1. 写真の調整", "2. 台紙・枚数", "3. お届け先入力", "4. 最終確認", "5. 完了"]
st.progress(c_step / 5)
st.write(f"**現在のステップ: {steps_names[c_step-1]}**")

# =========================================================
# 【ステップ 1】写真のアップロードと位置調整
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.info("💡 枠線をドラッグ、または四隅をつまんで、カレンダーに収めたい位置に調整してください。")
        
        # ✂️ 画像切り抜きパーツ（4:3の比率で固定）
        cropped_img = st_cropper(img, realtime_update=True, box_color='#1E88E5', aspect_ratio=(4, 3))
        
        # プレビュー表示
        st.write("▼ 切り抜き後のイメージ")
        st.image(cropped_img, width=300)
        
        # データを一時保存
        data["image"] = img
        data["cropped_image"] = cropped_img
    st.markdown('</div>', unsafe_allow_html=True)
    
    if data["cropped_image"] is not None:
        if st.button("OK：次へ進む ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 2
            st.rerun()

# =========================================================
# 【ステップ 2】台紙の選択と枚数の指定
# =========================================================
elif c_step == 2:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📐 台紙デザインと作成枚数を選んでください")
    
    # 台紙の選択（実際のPDFの雰囲気を文字で表現しています）
    template_option = st.radio(
        "作成するカレンダーの台紙（デザインタイプ）",
        ["A：ナチュラル・イラストタイプ", "B：アニマル・ポップタイプ", "C：シンプル・タテ型タイプ"],
        index=["A", "B", "C"].index(data["template"])
    )
    data["template"] = template_option[0] # 先頭のA, B, Cだけを保存
    
    st.write("---")
    # 枚数の選択
    data["quantity"] = st.number_input("作成枚数 (冊)", min_value=1, max_value=100, value=data["quantity"], step=1)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ナビゲーションボタン
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 戻る", use_container_width=True):
            st.session_state.c_step = 1
            st.rerun()
    with col2:
        if st.button("OK：次へ進む ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 3
            st.rerun()

# =========================================================
# 【ステップ 3】お客様情報の入力
# =========================================================
elif c_step == 3:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("👤 お届け先・お客様情報を入力してください")
    
    data["name"] = st.text_input("お名前", value=data["name"])
    data["zip"] = st.text_input("郵便番号 (例: 123-4567)", value=data["zip"])
    data["address"] = st.text_input("ご住所", value=data["address"])
    data["tel"] = st.text_input("電話番号", value=data["tel"])
    data["email"] = st.text_input("メールアドレス", value=data["email"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 簡易的な入力チェック
    ready = data["name"] and data["address"] and data["email"]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 戻る", use_container_width=True):
            st.session_state.c_step = 2
            st.rerun()
    with col2:
        if st.button("OK：注文確認画面へ ➔", use_container_width=True, type="primary", disabled=not ready):
            st.session_state.c_step = 4
            st.rerun()
    if not ready:
        st.caption("⚠️ お名前、ご住所、メールアドレスを入力すると次へ進めます。")

# =========================================================
# 【ステップ 4】最終確認画面
# =========================================================
elif c_step == 4:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("🔍 ご注文内容に間違いがないかご確認ください")
    
    col_img, col_info = st.columns([1, 1])
    with col_img:
        st.write("**【配置する写真】**")
        if data["cropped_image"]:
            st.image(data["cropped_image"], use_container_width=True)
    with col_info:
        st.write("**【ご注文仕様】**")
        st.write(f"・選んだ台紙: **タイプ {data['template']}**")
        st.write(f"・注文枚数: **{data['quantity']} 冊**")
        
        st.write("**【お届け先】**")
        st.write(f"・お名前: {data['name']} 様")
        st.write(f"・住所: 〒{data['zip']} {data['address']}")
        st.write(f"・連絡先: {data['tel']} / {data['email']}")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.warning("⚠️ 「注文を確定する」ボタンを押すと、お申し込みが完了します。")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 修正する", use_container_width=True):
            st.session_state.c_step = 3
            st.rerun()
    with col2:
        if st.button(" 注文を確定する（申込）", use_container_width=True, type="primary"):
            # 💡 本番時はここで写真データや住所をサーバーに保存したり、メールを送るプログラムを動かします。
            st.session_state.c_step = 5
            st.rerun()

# =========================================================
# 【ステップ 5】完了画面
# =========================================================
elif c_step == 5:
    st.balloons()
    st.success("🎉 お申し込みありがとうございました！")
    
    st.markdown(f"""
    <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #dcdcdc;">
        <h4>【重要】これからの流れについて</h4>
        <p>ご入力いただいたメールアドレス（ <b>{data['email']}</b> ）宛てに、<b>お振込みいただく銀行口座の情報</b>を記載した自動案内メールをお送りいたしました。</p>
        <p>🚨 <b>【ご注意】</b><br>
        商品の作成は、<b>ご入金が確認された後</b>に取り掛かります。</p>
        <p>📅 <b>お届けの目安</b><br>
        ご入金確認後、約<b>7週間</b>でお手元に届きますので、楽しみにお待ちください。</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 トップへ戻る", use_container_width=True):
        st.session_state.c_step = 1
        st.session_state.order_data = {
            "image": None, "cropped_image": None, "template": "A", "quantity": 1,
            "name": "", "zip": "", "address": "", "tel": "", "email": ""
        }
        st.rerun()
