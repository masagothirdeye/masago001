import streamlit as st
from PIL import Image, ImageDraw
import os
from streamlit_cropper import st_cropper # ✨ 追加パーツの読み込み

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
if "base_rotation" not in st.session_state: st.session_state.base_rotation = 0 # 90度ずつの回転用

if "order_data" not in st.session_state:
    st.session_state.order_data = {
        "image": None, "cropped_image": None, "template": "A", "quantity": 1,
        "name": "", "zip": "", "address": "", "tel": "", "email": "", "photo_type": "横型"
    }

c_step = st.session_state.c_step
data = st.session_state.order_data

# プログレスバー
steps_names = ["1. 写真の調整（トリミング）", "2. 台紙・枚数の選択", "3. お届け先入力", "4. 最終確認", "5. 完了"]
st.progress(c_step / 5)
st.write(f"**現在のステップ: {steps_names[c_step-1]}**")

# =========================================================
# 【ステップ 1】写真のアップロードとスマホ対応トリミング
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    st.markdown("""
    <div class="notice-box">
        <h4 style='color: #e65100; margin-top:0; font-size:16px;'>📐 配置できる写真の限界サイズ基準</h4>
        <p style='margin-size: 13px; margin-bottom: 5px;'>基本の枠サイズは以下の通りですが、<b>「自由にサイズを決める」</b>を選べばお好みの比率でカットできます！</p>
        <ul style='margin-bottom:0; padding-left:20px;'>
            <li><b>横型写真枠：</b> 横 260ミリ × 縦 165ミリ 比率</li>
            <li><b>縦型写真枠：</b> 横 145ミリ × 縦 245ミリ 比率</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 🔘 比率選択ボタン
    photo_direction = st.radio(
        "切り抜き枠の比率を選んでください：",
        ["横型枠（260×165）", "縦型枠（145×245）", "自由なサイズ（フリー比率）"],
        horizontal=True
    )
    
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # 画像の読み込み
        raw_img = Image.open(uploaded_file).convert("RGB")
        
        st.write("---")
        st.markdown("### 🔄 1. 写真の向き・角度を調整する")
        
        # 🔄 90度ずつの回転ボタン
        col_rot1, col_rot2, col_rot3 = st.columns(3)
        with col_rot1:
            if st.button("↩️ 左に90度回転", use_container_width=True):
                st.session_state.base_rotation = (st.session_state.base_rotation + 90) % 360
        with col_rot2:
            if st.button("↪️ 右に90度回転", use_container_width=True):
                st.session_state.base_rotation = (st.session_state.base_rotation - 90) % 360
        with col_rot3:
            if st.button("🔄 向きをリセット", use_container_width=True):
                st.session_state.base_rotation = 0
                
        # 90度回転をまず適用
        if st.session_state.base_rotation != 0:
            rotated_base = raw_img.rotate(st.session_state.base_rotation, expand=True)
        else:
            rotated_base = raw_img.copy()
            
        # 📐 スライダーによる「1度きざみ」の細かな数値角度調整
        fine_tune_angle = st.slider("✨ 細かな角度の微調整（傾き補正：-45度 〜 +45度）", -45, 45, 0, step=1)
        
        if fine_tune_angle != 0:
            rotated_img = rotated_base.rotate(-fine_tune_angle, expand=True, resample=Image.Resampling.BICUBIC)
        else:
            rotated_img = rotated_base
            
        st.write("---")
        st.markdown("### ✂️ 2. 写真のサイズと位置を調整する")
        st.info("💡 スマホの方は、写真の上の【青い枠の四隅】を触って広げたり、中を触って移動させてください。")
        
        # 枠線（比率）の設定
        if "横型枠" in photo_direction:
            aspect_ratio = 260 / 165
            data["photo_type"] = "横型"
        elif "縦型枠" in photo_direction:
            aspect_ratio = 145 / 245
            data["photo_type"] = "縦型"
        else:
            aspect_ratio = None # フリーサイズ
            data["photo_type"] = "フリーサイズ"
            
        # 🎨 スマホ対応のトリミング画面を表示（スライダーを廃止し、直接操作に変更）
        cropped_img = st_cropper(
            rotated_img,
            realtime_update=True,
            box_color='#1E88E5',
            aspect_ratio=aspect_ratio
        )
        
        # プレビュー画像の表示
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("▼ 現在の切り抜きエリア調整画面")
            # st_cropper自体が表示されるため、ここでは案内のみ
        with col_pre2:
            st.write("▼ 実際の印刷切り抜きイメージ")
            st.image(cropped_img, use_container_width=True)
            
            # データをセッションに格納
            data["image"] = rotated_img
            data["cropped_image"] = cropped_img
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    if data["cropped_image"] is not None:
        if st.button("OK：この配置で決定して次へ ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 2
            st.rerun()

# =========================================================
# 【ステップ 2】台紙の選択（写真自動合体プレビュー）
# =========================================================
elif c_step == 2:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📐 台紙デザインと作成枚数を選んでください")
    
    template_choice = st.radio(
        "ご希望のデザインを選択してください（台紙はすべてヨコ型仕様です）：",
        ["A：ナチュラル・イラストタイプ", 
         "B：アニマル・ポップタイプ", 
         "C：シンプル・定番タイプ"]
    )
    data["template"] = template_choice[0]
    
    st.write("▼ 【完成見本】選択中の台紙にあなたのお写真を合体しました！")
    
    img_name = f"design_{data['template'].lower()}.png"
    
    if os.path.exists(img_name) and data["cropped_image"] is not None:
        try:
            base_bg = Image.open(img_name).convert("RGB")
            bg_w, bg_h = base_bg.size
            user_pic = data["cropped_image"].copy()
            
            if data["photo_type"] == "横型":
                fit_w, fit_h = 520, 330
            elif data["photo_type"] == "縦型":
                fit_w, fit_h = 290, 490
            else:
                fre_w, fre_h = user_pic.size
                ratio = min(500 / fre_w, 400 / fre_h)
                fit_w, fit_h = int(fre_w * ratio), int(fre_h * ratio)
                
            user_pic = user_pic.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
            paste_x = max(0, (bg_w - fit_w) // 2)
            paste_y = max(0, (bg_h - fit_h) // 2 - 20)
            
            combined_preview = base_bg.copy()
            combined_preview.paste(user_pic, (paste_x, paste_y))
            st.image(combined_preview, caption="あなたのお写真が合成された完成イメージです", use_container_width=True)
            
        except Exception as e:
            st.image(data["cropped_image"], caption="調整したお写真", width=300)
    else:
        st.warning(f"⚠️ 倉庫に『{img_name}』が見つからないため、現在は写真のみ表示しています。")
        st.image(data["cropped_image"], caption="ステップ1で調整したあなたのお写真", width=300)
        
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
# 【ステップ 3】お届け先情報
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
        st.write(f"・切り抜きタイプ: {data['photo_type']}")
        
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
        st.session_state.base_rotation = 0
        st.session_state.order_data = {
            "image": None, "cropped_image": None, "template": "A", "quantity": 1,
            "name": "", "zip": "", "address": "", "tel": "", "email": "", "photo_type": "横型"
        }
        st.rerun()
