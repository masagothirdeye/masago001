import streamlit as st
from PIL import Image, ImageDraw
import os

# ページの初期設定
st.set_page_config(page_title="オリジナルカレンダー注文", layout="centered")

# 🎨 デザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #f7f9fa; }
    h1, h2, h3 { color: #2c3e50 !important; font-weight: 700; }
    .step-box { background-color: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    div.stButton > button { border-radius: 6px !important; font-weight: bold !important; height: 45px; }
    .size-badge { background-color: #1E88E5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 14px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("📅 オリジナルカレンダー作成・注文")
st.caption("お気に入りの写真を調整して、あなただけのカレンダーを作りましょう")

# セッション状態の初期化
if "c_step" not in st.session_state: st.session_state.c_step = 1
if "order_data" not in st.session_state:
    st.session_state.order_data = {
        "image": None, "cropped_image": None, "template": "A", "quantity": 1,
        "name": "", "zip": "", "address": "", "tel": "", "email": ""
    }

c_step = st.session_state.c_step
data = st.session_state.order_data

# プログレスバー
steps_names = ["1. 写真の調整（トリミング）", "2. 台紙・枚数の選択", "3. お届け先入力", "4. 最終確認", "5. 完了"]
st.progress(c_step / 5)
st.write(f"**現在のステップ: {steps_names[c_step-1]}**")

# =========================================================
# 【ステップ 1】写真のアップロードと位置調整（ミリ数比率連動）
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    # ユーザーがこれから選ぶ予定の暫定デザイン（ここで枠の縦横を決定する）
    st.write("どのタイプのカレンダーを作りますか？（枠の向きが変わります）")
    temp_select = st.selectbox(
        "カレンダーのタイプを選択",
        ["横型カレンダー（台紙A または B用）", "縦型カレンダー（台紙C用）"],
        index=0 if data["template"] in ["A", "B"] else 1
    )
    
    # 選択によって比率とミリ数の文字を自動切り替え
    if "横型" in temp_select:
        target_w_mm, target_h_mm = 260, 165
        aspect_ratio = 260 / 165  # 約 1.575
        size_text = "横 260ミリ × 縦 165ミリ（横型仕様）"
        if data["template"] == "C": data["template"] = "A" # 安全のための初期化
    else:
        target_w_mm, target_h_mm = 145, 245
        aspect_ratio = 145 / 245  # 約 0.591
        size_text = "横 145ミリ × 縦 245ミリ（縦型仕様）"
        data["template"] = "C"
        
    st.markdown(f"🎨 設定される印刷サイズ: <span class='size-badge'>{size_text}</span>", unsafe_allow_html=True)
    st.write("")
    
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        width, height = img.size
        
        st.write("---")
        st.markdown("### ✂️ 写真の切り抜き調整")
        st.caption("スライダーを動かして、カレンダーの指定枠に収まるように位置と大きさを調整してください。")
        
        # 枠線の計算（バグらない安全クッション付き）
        min_dim = min(width, height)
        
        # 比率に応じて、切り抜きボックスの初期最大サイズを制限
        if aspect_ratio > 1: # 横長の場合
            max_crop_size = min(width, int(height * aspect_ratio))
            crop_size = st.slider("① 切り抜く大きさを決める（拡大・縮小）", int(max_crop_size*0.2), max_crop_size, int(max_crop_size*0.8))
            crop_w = crop_size
            crop_h = int(crop_size / aspect_ratio)
        else: # 縦長の場合
            max_crop_size = min(int(width / aspect_ratio), height)
            crop_size = st.slider("① 切り抜く大きさを決める（拡大・縮小）", int(max_crop_size*0.2), max_crop_size, int(max_crop_size*0.8))
            crop_h = crop_size
            crop_w = int(crop_size * aspect_ratio)
            
        # 写真からはみ出さないための安全ガード
        if crop_w > width:
            crop_w = width
            crop_h = int(width / aspect_ratio)
        if crop_h > height:
            crop_h = height
            crop_w = int(height * aspect_ratio)
            
        max_x = max(0, width - crop_w)
        max_y = max(0, height - crop_h)
        
        left = st.slider("② 左右の位置を動かす", 0, max_x, int(max_x / 2))
        top = st.slider("③ 上下の位置を動かす", 0, max_y, int(max_y / 2))
        
        # プレビュー表示
        preview_img = img.copy()
        draw = ImageDraw.Draw(preview_img)
        draw.rectangle([left, top, left + crop_w, top + crop_h], outline="#1E88E5", width=int(min_dim*0.01)+2)
        
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("▼ 全体位置（青枠の中がカレンダーに入ります）")
            st.image(preview_img, use_container_width=True)
        with col_pre2:
            st.write("▼ カレンダーへの配置プレビュー")
            cropped_img = img.crop([left, top, left + crop_w, top + crop_h])
            st.image(cropped_img, use_container_width=True)
            
            # データを保存
            data["image"] = img
            data["cropped_image"] = cropped_img
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    if data["cropped_image"] is not None:
        if st.button("OK：位置を決定して次へ ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 2
            st.rerun()

# =========================================================
# 【ステップ 2】台紙の選択（画像付き）と枚数の指定
# =========================================================
elif c_step == 2:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📐 台紙デザインと作成枚数を選んでください")
    
    # ステップ1の画像に合わせて選択肢を制限、または初期位置を変更
    if data["template"] == "C":
        st.info("💡 縦型写真用に調整されたため、自動的に【台紙C】が選ばれています。")
        template_choice = st.radio("ご希望のデザイン：", ["C：シンプル・タテ型タイプ（タテ型）"])
    else:
        template_choice = st.radio(
            "ご希望のデザインを選択してください：",
            ["A：ナチュラル・イラストタイプ（ヨコ型）", "B：アニマル・ポップタイプ（ヨコ型）"]
        )
    data["template"] = template_choice[0]
    
    st.write("▼ 選択中の台紙イメージ")
    
    img_name = f"design_{data['template'].lower()}.png"
    if os.path.exists(img_name):
        st.image(img_name, caption=f"台紙タイプ {data['template']} の実際のデザイン", use_container_width=True)
    else:
        st.warning(f"⚠️ 倉庫に『{img_name}』が見つからないため、サンプルの案内文を表示しています。")
        if data["template"] == "A":
            st.info("【台紙 A】ナチュラル・イラスト：横260mm×縦165mmの写真が配置されます")
        elif data["template"] == "B":
            st.info("【台紙 B】アニマル・ポップ：横260mm×縦165mmの写真が配置されます")
        elif data["template"] == "C":
            st.info("【台紙 C】シンプル・タテ型：横145mm×縦245mmの写真が配置されます")
        
    st.write("---")
    data["quantity"] = st.number_input("作成枚数 (冊)", min_value=1, max_value=100, value=data["quantity"], step=1)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 写真を選び直す", use_container_width=True):
            st.session_state.c_step = 1
            st.rerun()
    with col2:
        if st.button("OK：台紙を決定して次へ ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 3
            st.rerun()

# =========================================================
# 【ステップ 3】お客様情報の入力（以下、前回のフローを継承）
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

# =========================================================
# 【ステップ 4】最終確認画面
# =========================================================
elif c_step == 4:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("🔍 ご注文内容に間違いがないかご確認ください")
    
    col_img, col_info = st.columns([1, 1])
    with col_img:
        st.write("**【配置する写真（トリミング済）】**")
        if data["cropped_image"]:
            st.image(data["cropped_image"], use_container_width=True)
    with col_info:
        st.write("**【ご注文仕様】**")
        st.write(f"・選んだ台紙: **タイプ {data['template']}**")
        st.write(f"・注文枚数: **{data['quantity']} 冊**")
        
        st.write("**【お届け先】**")
        st.write(f"・お名前: {data['name']} 様")
        st.write(f"・住所: 〒{data['zip']} {data['address']}")
        st.write(f"枠サイズ: {'260mm × 165mm' if data['template'] in ['A','B'] else '145mm × 245mm'}")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 修正する", use_container_width=True):
            st.session_state.c_step = 3
            st.rerun()
    with col2:
        if st.button(" 注文を確定する（申込）", use_container_width=True, type="primary"):
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
