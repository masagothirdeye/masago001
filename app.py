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
    .notice-box { background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    .size-badge { background-color: #1E88E5; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
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
# 【ステップ 1】写真のアップロードと位置調整（ボタン切り替え式）
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    # ⚠️ 印刷サイズに関する大事な注意書き（限界サイズを明記）
    st.markdown("""
    <div class="notice-box">
        <h4 style='color: #e65100; margin-top:0;'>⚠️ 写真の印刷サイズに関するご注意</h4>
        <p style='margin-bottom:5px;'>当店のカレンダー台紙は<b>すべて横型仕様</b>となります。配置できる写真の限界サイズは以下の通りです：</p>
        <ul>
            <li><b>横型のお写真：</b> 横 260ミリ × 縦 165ミリ まで</li>
            <li><b>縦型のお写真：</b> 横 145ミリ × 縦 245ミリ まで</li>
        </ul>
        <p style='font-size:13px; color:#555; margin-bottom:0;'>※下のボタンでお手元の写真の向きを選ぶと、自動的に限界サイズの比率枠が表示されます。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 🔘 写真の向きを切り替えるボタン（選択肢）
    photo_orientation = st.radio(
        "アップロードするお写真の向きを選んでください：",
        ["横型のお写真（260mm × 165mm枠）", "縦型のお写真（145mm × 245mm枠）"],
        horizontal=True
    )
    
    # ボタンの選択によって、青い枠の比率をカチッと切り替える
    if "横型" in photo_orientation:
        aspect_ratio = 260 / 165  # 1.575
        size_label = "横型用（260mm × 165mm）"
    else:
        aspect_ratio = 145 / 245  # 0.591
        size_label = "縦型用（145mm × 245mm）"
        
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        img_w, img_h = img.size
        
        st.write("---")
        st.markdown(f"### ✂️ 写真のカット位置調整 （適用中: <span class='size-badge'>{size_label}</span>）", unsafe_allow_html=True)
        st.caption("青い枠線のエリアが実際のカレンダーに印刷されます。スライダーを動かして上下左右のカット位置を微調整してください。")
        
        # 写真のサイズに応じて、はみ出さない最大の枠サイズを計算
        if aspect_ratio > 1: # 横型枠
            crop_w = min(img_w, int(img_h * aspect_ratio))
            crop_h = int(crop_w / aspect_ratio)
        else: # 縦型枠
            crop_h = min(img_h, int(img_w / aspect_ratio))
            crop_w = int(crop_h * aspect_ratio)
            
        # スライダーで動かせる限界の幅
        max_x = max(0, img_w - crop_w)
        max_y = max(0, img_h - crop_h)
        
        # 位置調整スライダー（直感的にお客さんがカット位置を変えられる）
        left = st.slider("① 左右の位置をずらす（横方向のカット調整）", 0, max_x, int(max_x / 2)) if max_x > 0 else 0
        top = st.slider("② 上下の位置をずらす（縦方向のカット調整）", 0, max_y, int(max_y / 2)) if max_y > 0 else 0
        
        # プレビュー画像の作成
        preview_img = img.copy()
        draw = ImageDraw.Draw(preview_img)
        # 送っていただいたスクショと同じ、綺麗な青色の太枠線を描画
        draw.rectangle([left, top, left + crop_w, top + crop_h], outline="#1E88E5", width=int(min(img_w, img_h)*0.015)+2)
        
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("▼ お写真全体図（青枠の中がカレンダーに入ります）")
            st.image(preview_img, use_container_width=True)
        with col_pre2:
            st.write("▼ 実際の印刷切り抜きイメージ")
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
# 【ステップ 2】台紙の選択（すべてヨコ型A・B·C）
# =========================================================
elif c_step == 2:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📐 台紙デザインと作成枚数を選んでください")
    
    template_choice = st.radio(
        "ご希望のデザインを選択してください：",
        ["A：ナチュラル・イラストタイプ（ヨコ型カレンダー）", 
         "B：アニマル・ポップタイプ（ヨコ型カレンダー）", 
         "C：シンプル・定番タイプ（ヨコ型カレンダー）"]
    )
    data["template"] = template_choice[0]
    
    st.write("▼ 選択中の台紙イメージ")
    
    img_name = f"design_{data['template'].lower()}.png"
    if os.path.exists(img_name):
        st.image(img_name, caption=f"台紙タイプ {data['template']} の実際のデザイン", use_container_width=True)
    else:
        st.warning(f"⚠️ 倉庫に『{img_name}』が見つからないため、サンプルの案内文を表示しています。")
        st.info(f"【台紙 {data['template']}】選んだ写真がはめ込まれたヨコ型のカレンダー台紙となります。")
        
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
# 【ステップ 3】お届け先情報（以下、変更なし）
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
