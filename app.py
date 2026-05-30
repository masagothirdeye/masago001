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
        "name": "", "zip": "", "address": "", "tel": "", "email": "", "photo_type": "横型"
    }

c_step = st.session_state.c_step
data = st.session_state.order_data

# プログレスバー
steps_names = ["1. 写真の調整（トリミング）", "2. 台紙・枚数の選択", "3. お届け先入力", "4. 最終確認", "5. 完了"]
st.progress(c_step / 5)
st.write(f"**現在のステップ: {steps_names[c_step-1]}**")

# =========================================================
# 【ステップ 1】写真のアップロードと位置調整
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    st.markdown("""
    <div class="notice-box">
        <h4 style='color: #e65100; margin-top:0; font-size:16px;'>📐 配置できる写真の限界サイズ</h4>
        <ul style='margin-bottom:0; padding-left:20px;'>
            <li><b>横型のお写真の場合：</b> 横 260ミリ × 縦 165ミリ まで</li>
            <li><b>縦型のお写真の場合：</b> 横 145ミリ × 縦 245ミリ まで</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    photo_direction = st.radio(
        "お持ちの写真の向きを選んでください：",
        ["横型のお写真（260×165比率）", "縦型のお写真（145×245比率）"],
        horizontal=True
    )
    
    if "横型" in photo_direction:
        aspect_ratio = 260 / 165
        size_label = "横型枠（260mm × 165mm）"
        data["photo_type"] = "横型"
    else:
        aspect_ratio = 145 / 245
        size_label = "縦型枠（145mm × 245mm）"
        data["photo_type"] = "縦型"
        
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        img_w, img_h = img.size
        
        st.write("---")
        st.markdown(f"### ✂️ 写真のカット位置調整 （適用枠: <span class='size-badge'>{size_label}</span>）", unsafe_allow_html=True)
        st.caption("青い枠線の中がカレンダーに入るサイズです。スライダーを動かして上下左右のカット位置を微調整してください。")
        
        if aspect_ratio > 1:
            crop_w = min(img_w, int(img_h * aspect_ratio))
            crop_h = int(crop_w / aspect_ratio)
        else:
            crop_h = min(img_h, int(img_w * aspect_ratio))
            crop_w = int(crop_h * aspect_ratio)
            
        max_x = max(0, img_w - crop_w)
        max_y = max(0, img_h - crop_h)
        
        left = st.slider("① 左右の位置をずらす（横方向のカット位置）", 0, max_x, int(max_x / 2)) if max_x > 0 else 0
        top = st.slider("② 上下の位置をずらす（縦方向のカット位置）", 0, max_y, int(max_y / 2)) if max_y > 0 else 0
        
        preview_img = img.copy()
        draw = ImageDraw.Draw(preview_img)
        draw.rectangle([left, top, left + crop_w, top + crop_h], outline="#1E88E5", width=int(min(img_w, img_h)*0.015)+2)
        
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("▼ お写真全体（青枠のエリアがカレンダーに残ります）")
            st.image(preview_img, use_container_width=True)
        with col_pre2:
            st.write("▼ 実際の印刷切り抜きイメージ")
            cropped_img = img.crop([left, top, left + crop_w, top + crop_h])
            st.image(cropped_img, use_container_width=True)
            
            data["image"] = img
            data["cropped_image"] = cropped_img
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    if data["cropped_image"] is not None:
        if st.button("OK：この配置で決定して次へ ➔", use_container_width=True, type="primary"):
            st.session_state.c_step = 2
            st.rerun()

# =========================================================
# 【ステップ 2】台紙の選択（★写真自動合体プレビュー搭載！）
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
            # 1. 倉庫からベースとなる台紙画像を読み込む
            base_bg = Image.open(img_name).convert("RGB")
            bg_w, bg_h = base_bg.size
            
            # 2. ステップ1で切り抜いたお客様の写真をコピー
            user_pic = data["cropped_image"].copy()
            
            # 3. 横型写真か縦型写真かで、台紙に貼り付けるサイズと位置を自動計算
            if data["photo_type"] == "横型":
                # 横型枠の標準的なサイズ（例: 520x330）に写真をリサイズ
                fit_w, fit_h = 520, 330
                user_pic = user_pic.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
                # 台紙画像の中央あたりに配置（台紙の大きさに合わせて自動で真ん中に配置）
                paste_x = max(0, (bg_w - fit_w) // 2)
                paste_y = max(0, (bg_h - fit_h) // 2 - 40) # 少し上寄りに配置
            else:
                # 縦型枠の標準的なサイズ（例: 290x490）に写真をリサイズ
                fit_w, fit_h = 290, 490
                user_pic = user_pic.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
                # 台紙の左側や中央など、縦型お写真用の位置に配置
                paste_x = max(0, (bg_w - fit_w) // 2)
                paste_y = max(0, (bg_h - fit_h) // 2 - 20)
                
            # 4. 台紙に写真をガッチャンコ（合成）する
            combined_preview = base_bg.copy()
            combined_preview.paste(user_pic, (paste_x, paste_y))
            
            # 5. 画面にドカンと表示
            st.image(combined_preview, caption="あなたのお写真が合成された完成イメージです", use_container_width=True)
            
        except Exception as e:
            st.error(f"プレビュー合成中にエラーが発生しました。手動プレビューに切り替えます。")
            st.image(data["cropped_image"], caption="調整したお写真", width=300)
    else:
        # まだ倉庫に design_a.png などがない場合の案内
        st.warning(f"⚠️ 倉庫に『{img_name}』が見つからないため、現在は写真のみ表示しています。画像を倉庫（GitHub）にアップすると自動で台紙と合体します！")
        col_view1, col_view2 = st.columns([1, 1])
        with col_view1:
            st.info(f"【選択中】台紙タイプ {data['template']}（ヨコ型）")
        with col_view2:
            st.image(data["cropped_image"], caption="ステップ1で調整したあなたのお写真", use_container_width=True)
        
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
# 【ステップ 3】お届け先情報（変更なし）
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
        st.write(f"・写真タイプ: {data['photo_type']}写真仕様")
        
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
        ご入金確認後, 約<b>7週間</b>でお手元に届きますので、楽しみにお待ちください。</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 トップへ戻る", use_container_width=True):
        st.session_state.c_step = 1
        st.session_state.order_data = {
            "image": None, "cropped_image": None, "template": "A", "quantity": 1,
            "name": "", "zip": "", "address": "", "tel": "", "email": "", "photo_type": "横型"
        }
        st.rerun()
