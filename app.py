import streamlit as st
from PIL import Image, ImageDraw
import os
from streamlit_cropper import st_cropper

# ページの初期設定
st.set_page_config(page_title="オリジナルカレンダー注文", layout="centered")

# 🎨 【ボタン色完全リニューアル版】デザイン（CSS）
st.markdown("""
<style>
/* アプリ全体の背景と基本の文字色を強制固定 */
.stApp { 
    background-color: #87cefa !important; 
    color: #000000 !important; 
}

/* 各種見出しや文字を真っ黒に固定 */
h1, h2, h3, h4, h5, h6, span, p, label, .stText { 
    color: #000000 !important; 
}

/* ステップBOXの背景（白） */
.step-box { 
    background-color: #ffffff !important; 
    color: #000000 !important;
    padding: 25px; 
    border-radius: 10px; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
    margin-bottom: 20px; 
}
.step-box h1, .step-box h2, .step-box h3, .step-box p, .step-box label {
    color: #000000 !important;
}

/* ファイルアップローダー内の文字化け対策 */
div[data-testid="stFileUploader"] section {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px dashed #333333 !important;
}
div[data-testid="stFileUploader"] label p {
    color: #000000 !important;
}
div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] p {
    color: #333333 !important;
}

/* ＝★＝★＝ ボタンのカラーカスタマイズ ＝★＝★＝ */

/* ① 【次へ・確定（主要なボタン）】の指定：オレンジ (#ffa500) */
div.stButton > button[kind="primary"] {
    background-color: #ffa500 !important;
    color: #000000 !important;
    border: 2px solid #e09000 !important;
    border-radius: 6px !important; 
    font-weight: bold !important; 
    height: 45px;
    transition: all 0.2s ease;
}
/* カーソルが当たった（ホバー）・タップした時は少し濃いオレンジへ */
div.stButton > button[kind="primary"]:hover, div.stButton > button[kind="primary"]:active {
    background-color: #e69500 !important;
    color: #000000 !important;
    border-color: #cc8000 !important;
}

/* ② 【戻る・リセット（標準のボタン）】の指定：薄緑 (#98fb98) */
div.stButton > button[kind="secondary"] {
    background-color: #98fb98 !important;
    color: #000000 !important;
    border: 2px solid #7ecc7e !important;
    border-radius: 6px !important; 
    font-weight: bold !important; 
    height: 45px;
    transition: all 0.2s ease;
}
/* カーソルが当たった（ホバー）・タップした時は少し濃い薄緑へ */
div.stButton > button[kind="secondary"]:hover, div.stButton > button[kind="secondary"]:active {
    background-color: #82e282 !important;
    color: #000000 !important;
    border-color: #69c069 !important;
}

/* スマホ用リアル図解スタイル */
.visual-guide-card {
    background-color: #e8f4fd !important;
    border: 2px solid #1e88e5 !important;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 20px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.08);
}
.visual-guide-card p, .visual-guide-card span {
    color: #2c3e50 !important;
}
.guide-display-frame {
    border: 3px solid #FF0000 !important;
    padding: 15px 10px;
    position: relative;
    text-align: center;
    background-color: #ffffff !important;
    font-weight: bold;
    margin: 15px auto;
    max-width: 300px;
    border-radius: 4px;
}
.guide-display-frame span {
    color: #FF0000 !important;
}
.guide-display-frame p {
    color: #555555 !important;
}

.corner-marker-tl { position: absolute; top: -8px; left: -8px; background: white !important; border: 1px solid #333 !important; width: 14px; height: 14px; }
.corner-marker-tr { position: absolute; top: -8px; right: -8px; background: white !important; border: 1px solid #333 !important; width: 14px; height: 14px; }
.corner-marker-bl { position: absolute; bottom: -8px; left: -8px; background: white !important; border: 1px solid #333 !important; width: 14px; height: 14px; }
.corner-marker-br { position: absolute; bottom: -8px; right: -8px; background: white !important; border: 1px solid #333 !important; width: 14px; height: 14px; }

.action-arrow-tl { position: absolute; top: -25px; left: -25px; font-size: 24px; color: #FF0000 !important; font-weight: bold; }
.action-arrow-tr { position: absolute; top: -25px; right: -25px; font-size: 24px; color: #FF0000 !important; font-weight: bold; }
.action-arrow-bl { position: absolute; bottom: -25px; left: -25px; font-size: 24px; color: #FF0000 !important; font-weight: bold; }
.action-arrow-br { position: absolute; bottom: -25px; right: -25px; font-size: 24px; color: #FF0000 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📅 オリジナルカレンダー作成・注文")
st.caption("お気に入りの写真を調整して、あなただけのカレンダーを作りましょう")

# セッション状態の初期化
if "c_step" not in st.session_state: st.session_state.c_step = 1
if "base_rotation" not in st.session_state: st.session_state.base_rotation = 0 

if "order_data" not in st.session_state:
    st.session_state.order_data = {
        "image": None, "cropped_image": None, "template": "A", "quantity": 1,
        "name": "", "zip": "", "address": "", "tel": "", "email": "", "photo_type": "フリーサイズ"
    }

c_step = st.session_state.c_step
data = st.session_state.order_data

# プログレスバー
steps_names = ["1. 写真の調整（トリミング）", "2. 台紙・枚数の選択", "3. お届け先入力", "4. 最終確認", "5. 完了"]
st.progress(c_step / 5)
st.markdown(f"**現在のステップ: {steps_names[c_step-1]}**")

# =========================================================
# 【ステップ 1】写真のアップロードとスマホ対応トリミング
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        raw_img = Image.open(uploaded_file).convert("RGB")
        st.session_state.order_data["image"] = raw_img
    elif data["image"] is not None:
        raw_img = data["image"]
    else:
        raw_img = None

    if raw_img:
        st.write("---")
        st.markdown("### 🔄 1. 写真の向き・角度を調整する")
        
        col_rot1, col_rot2, col_rot3 = st.columns(3)
        with col_rot1:
            if st.button("↩️ 左に90度回転", use_container_width=True, type="secondary"):
                st.session_state.base_rotation = (st.session_state.base_rotation + 90) % 360
                st.rerun()
        with col_rot2:
            if st.button("↪️ 右に90度回転", use_container_width=True, type="secondary"):
                st.session_state.base_rotation = (st.session_state.base_rotation - 90) % 360
                st.rerun()
        with col_rot3:
            if st.button("🔄 向きをリセット", use_container_width=True, type="secondary"):
                st.session_state.base_rotation = 0
                st.rerun()
                
        if st.session_state.base_rotation != 0:
            rotated_base = raw_img.rotate(st.session_state.base_rotation, expand=True)
        else:
            rotated_base = raw_img.copy()
            
        fine_tune_angle = st.slider("✨ 細かな角度の微調整（傾き補正：-45度 〜 +45度）", -45, 45, 0, step=1)
        
        if fine_tune_angle != 0:
            rotated_img = rotated_base.rotate(-fine_tune_angle, expand=True, resample=Image.Resampling.BICUBIC)
        else:
            rotated_img = rotated_base
            
        st.write("---")
        st.markdown("### ✂️ 2. 写真のサイズと位置を調整する")
        
        # ガイド部分
        st.markdown('<div class="visual-guide-card"><p style="margin:0 0 5px 0;font-size:16px;font-weight:bold;color:#1e88e5;text-align:center;">📱 【かんたん操作ガイド】</p><p style="margin:0 0 15px 0;font-size:14px;color:#455a64;text-align:center;line-height:1.4;">下の写真に表示されている<b>「赤い枠」</b>は、指で自由に大きさを変えられます！</p><div class="guide-display-frame"><div class="corner-marker-tl"></div><div class="corner-marker-tr"></div><div class="corner-marker-bl"></div><div class="corner-marker-br"></div><div class="action-arrow-tl">🔴↖</div><div class="action-arrow-tr">↗🔴</div><div class="action-arrow-bl">🔴↙</div><div class="action-arrow-br">↘🔴</div><span style="font-size:16px;color:#FF0000;">四隅の「白い四角」をつかんで<br>外側や内側にスライドさせると<br>サイズが変わります！</span><p style="font-size:13px;font-weight:normal;color:#555;margin:10px 0 0 0;padding-top:8px;border-top:1px dashed #ddd;">※真ん中あたりをさわると、上下左右に位置をうごかせます。</p></div></div>', unsafe_allow_html=True)
        
        # トリミング画面を表示
        cropped_img = st_cropper(
            rotated_img,
            realtime_update=True,
            box_color='#FF0000',
            aspect_ratio=None
        )
        
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("上のガイドを見ながら、実際の赤い枠を調整してね！ 👆")
        with col_pre2:
            st.write("▼ 実際の印刷切り抜きイメージ")
            st.image(cropped_img, use_container_width=True)
            
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
        if st.button("◀ 写真を調整し直す", use_container_width=True, type="secondary"):
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
        if st.button("◀ 戻る", use_container_width=True, type="secondary"):
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
        st.write("**【配置する写真（トリミング済）**】")
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
        if st.button("◀ 修正する", use_container_width=True, type="secondary"):
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
    <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #dcdcdc; color: #000000;">
        <h4 style="color: #000000;">【重要】これからの流れについて</h4>
        <p>ご入力いただいたメールアドレス（ <b>{data['email']}</b> ）宛てに、<b>お振込みいただく銀行口座の情報</b>を記載した自動案内メールをお送りいたしました。</p>
        <p>🚨 <b>【ご注意】</b><br>
        商品の作成は、<b>ご入金が確認された後</b>に取り掛かります。</p>
        <p>📅 <b>お届けの目安</b><br>
        ご入金確認後、約<b>7週間</b>でお手元に届きますので、楽しみにお待ちください。</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 トップへ戻る", use_container_width=True, type="secondary"):
        st.session_state.c_step = 1
        st.session_state.base_rotation = 0
        st.session_state.order_data = {
            "image": None, "cropped_image": None, "template": "A", "quantity": 1,
            "name": "", "zip": "", "address": "", "tel": "", "email": "", "photo_type": "フリーサイズ"
        }
        st.rerun()
