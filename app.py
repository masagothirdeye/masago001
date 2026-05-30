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
    .size-badge { background-color: #2e7d32; color: white; padding: 4px 8px; border-radius: 4px; font-size: 14px; font-weight: bold; }
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
# 【ステップ 1】写真のアップロードと位置調整（枠内での微調整）
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    # 枠のタイプを最初に選んでもらう
    st.write("作成するカレンダーの向きを選んでください：")
    temp_select = st.selectbox(
        "カレンダーのタイプ",
        ["横型カレンダー（台紙A または B用）", "縦型カレンダー（台紙C用）"],
        index=0 if data["template"] in ["A", "B"] else 1
    )
    
    # 選んだ向きによって、絶対に崩れない固定の「仕上がり比率」を設定
    if "横型" in temp_select:
        target_w, target_h = 260, 165
        aspect_ratio = 260 / 165  # 1.575
        size_text = "横 260mm × 縦 165mm 固定枠"
        if data["template"] == "C": data["template"] = "A"
    else:
        target_w, target_h = 145, 245
        aspect_ratio = 145 / 245  # 0.591
        size_text = "横 145mm × 縦 245mm 固定枠"
        data["template"] = "C"
        
    st.markdown(f"📐 仕上がり印刷枠: <span class='size-badge'>{size_text}</span>", unsafe_allow_html=True)
    st.write("")
    
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        img_w, img_h = img.size
        
        st.write("---")
        st.markdown("### ✂️ 写真のはめ込み微調整")
        st.caption("指定枠（青い線）の中に写真をどう収めるか、感覚的に調整してください。はみ出た部分は自動でカットされます。")
        
        # 1. 【拡大・縮小】写真のどのくらいの範囲を枠内に収めるか
        # 枠の比率を保ったまま、切り抜くベースサイズを決める
        max_base = min(img_w, int(img_h * aspect_ratio)) if aspect_ratio > 1 else min(int(img_w / aspect_ratio), img_h)
        
        # スライダーで直感的に拡大率（切り抜き視野の広さ）を調整
        zoom = st.slider("① 写真を拡大・縮小する（右に動かすと拡大、左に動かすと引いた写真になります）", 
                         min_value=int(max_base * 0.1), max_value=max_base, value=int(max_base * 0.9), step=1)
        
        if aspect_ratio > 1:
            crop_w = zoom
            crop_h = int(zoom / aspect_ratio)
        else:
            crop_h = zoom
            crop_w = int(zoom * aspect_ratio)
            
        # 2. 【位置調整】上下・左右をカットする位置の微調整
        max_x = max(0, img_w - crop_w)
        max_y = max(0, img_h - crop_h)
        
        left = st.slider("② 左右の位置をずらす（左右のカット位置調整）", 0, max_x, int(max_x / 2))
        top = st.slider("③ 上下の位置をずらす（上下のカット位置調整）", 0, max_y, int(max_y / 2))
        
        # プレビュー画像の作成
        preview_img = img.copy()
        draw = ImageDraw.Draw(preview_img)
        # 切り抜かれる固定枠を青色の太線で描画
        draw.rectangle([left, top, left + crop_w, top + crop_h], outline="#1E88E5", width=int(min(img_w, img_h)*0.01)+2)
        
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("▼ 全体図（青い枠線のエリアがカレンダーに残ります）")
            st.image(preview_img, use_container_width=True)
        with col_pre2:
            st.write("▼ カレンダーへの配置プレビュー（最終仕上がり）")
            # 実際に指定枠の比率でカットされた画像
            cropped_img = img.crop([left, top, left + crop_w, top + crop_h])
            st.image(cropped_img, use_container_width=True)
            
            # データを保存
            data["image"] = img
            data["cropped_image"] = cropped_img
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    if data["cropped_image"] is not None:
        if st.button("OK：この配置で決定して次へ ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 2
            st.rerun()

# =========================================================
# 【ステップ 2】台紙の選択（画像付き）と枚数の指定
# =========================================================
elif c_step == 2:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📐 台紙デザインと作成枚数を選んでください")
    
    if data["template"] == "C":
        st.info("💡 縦型枠（145mm×245mm）で調整されたため、自動的に【台紙C】が適用されています。")
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
            st.info("【台紙 A】ナチュラル・イラスト：調整済みの横260mm×縦165mmの写真が配置されます")
        elif data["template"] == "B":
            st.info("【台紙 B】アニマル・ポップ：調整済みの横260mm×縦165mmの写真が配置されます")
        elif data["template"] == "C":
            st.info("【台紙 C】シンプル・タテ型：調整済みの横145mm×縦245mmの写真が配置されます")
        
    st.write("---")
    data["quantity"] = st.number_input("作成枚数 (冊)", min_value=1, max_value=100, value=data["quantity"], step=1)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("◀ 写真を調整し直す", use_container_width=True):
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
        st.write(f"・印刷サイズ: {'260mm × 165mm' if data['template'] in ['A','B'] else '145mm × 245mm'}")
        
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
        <p>ご入力いただいたメールアドレス（ <b>{data['email']}</b> ）宛てに, <b>お振込みいただく銀行口座の情報</b>を記載した自動案内メールをお送りいたしました。</p>
        <p>🚨 <b>【ご注意】</b><br>
        商品の作成は, <b>ご入金が確認された後</b>に取り掛かります。</p>
        <p>📅 <b>お届けの目安</b><br>
        ご入金確認後, 約<b>7週間</b>でお手元に届きますので、楽しみにお待ちください。</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 トップへ戻る", use_container_width=True):
        st.session_state.c_step = 1
        st.session_state.order_data = {
            "image": None, "cropped_image": None, "template": "A", "quantity": 1,
            "name": "", "zip": "", "address": "", "tel": "", "email": ""
        }
        st.rerun()
