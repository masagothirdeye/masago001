import streamlit as st
from PIL import Image, ImageDraw

# ページの初期設定
st.set_page_config(page_title="オリジナルカレンダー注文", layout="centered")

# 🎨 デザイン（CSS）
st.markdown("""
    <style>
    .stApp { background-color: #f7f9fa; }
    h1, h2, h3 { color: #2c3e50 !important; font-weight: 700; }
    .step-box { background-color: #ffffff; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
    div.stButton > button { border-radius: 6px !important; font-weight: bold !important; height: 45px; }
    .template-card { border: 2px solid #e0e0e0; padding: 15px; border-radius: 8px; background-color: #ffffff; text-align: center; }
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
# 【ステップ 1】写真のアップロードと位置調整（トリミング）
# =========================================================
if c_step == 1:
    st.markdown('<div class="step-box">', unsafe_allow_html=True)
    st.subheader("📸 カレンダーに使用する写真をアップロードしてください")
    
    uploaded_file = st.file_uploader("スマホやPCから画像を選択（JPG / PNG）", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # 画像の読み込み
        img = Image.open(uploaded_file).convert("RGB")
        width, height = img.size
        
        st.write("---")
        st.markdown("### ✂️ 写真の切り抜き調整")
        st.caption("スライダーを動かして、カレンダーの枠（横長 4:3）に収める位置と大きさを調整してください。")
        
        # 自由で絶対にバグらないトリミングシステム（位置と拡大率のスライダー）
        min_dim = min(width, height)
        crop_size = st.slider("① 切り抜く大きさを決める（拡大・縮小）", int(min_dim*0.2), min_dim, int(min_dim*0.8))
        
        # カレンダー枠（4:3）に合わせて切り抜き範囲を計算
        crop_w = crop_size
        crop_h = int(crop_size * 3 / 4)
        
        # 縦が足りなくなった場合の安全調整
        if crop_h > height:
            crop_h = height
            crop_w = int(height * 4 / 3)
            
        max_x = max(0, width - crop_w)
        max_y = max(0, height - crop_h)
        
        left = st.slider("② 左右の位置を動かす", 0, max_x, int(max_x / 2))
        top = st.slider("③ 上下の位置を動かす", 0, max_y, int(max_y / 2))
        
        # プレビュー用に枠線を描画
        preview_img = img.copy()
        draw = ImageDraw.Draw(preview_img)
        # 切り抜き枠を太い青線で表示
        draw.rectangle([left, top, left + crop_w, top + crop_h], outline="#1E88E5", width=int(min_dim*0.01)+1)
        
        col_pre1, col_pre2 = st.columns(2)
        with col_pre1:
            st.write("▼ 全体位置（青枠の中が切り抜かれます）")
            st.image(preview_img, use_container_width=True)
        with col_pre2:
            st.write("▼ カレンダーへの配置イメージ")
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
    
    # 選択用のラジオボタン
    template_choice = st.radio(
        "ご希望のデザインを選択してください：",
        ["A：ナチュラル・イラストタイプ（ヨコ型）", "B：アニマル・ポップタイプ（ヨコ型）", "C：シンプル・タテ型タイプ（タテ型）"]
    )
    data["template"] = template_choice[0] # A, B, Cの文字だけ抽出
    
    st.write("▼ 選択中の台紙イメージ")
    
    # PDFのデザインを簡易的に再現したビジュアルカードを画面に出す
    if data["template"] == "A":
        st.markdown("""
        <div class="template-card" style="border-color: #81c784;">
            <span style="font-size: 20px; font-weight: bold; color: #2e7d32;">【台紙 A】ナチュラル・イラストタイプ</span><br>
            <span style="font-size: 14px; color: #666;">温かみのある植物やリーフのイラストが毎月を彩る、リビングに馴染むヨコ型カレンダー</span>
            <div style="background: #e8f5e9; height: 120px; margin: 15px 0; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: 1px dashed #81c784;">
                <b style="color: #2e7d32;">[ 🖼️ お客様の写真（ヨコ長） ]<br>ーーーーーーーーーーー<br>🗓️ 1月・2月・3月（3ヶ月表示）</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif data["template"] == "B":
        st.markdown("""
        <div class="template-card" style="border-color: #ffb74d;">
            <span style="font-size: 20px; font-weight: bold; color: #ef6c00;">【台紙 B】アニマル・ポップタイプ</span><br>
            <span style="font-size: 14px; color: #666;">可愛い動物のキャラクターが四隅にあしらわれた、子供部屋やギフトに最適なヨコ型カレンダー</span>
            <div style="background: #fff3e0; height: 120px; margin: 15px 0; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: 1px dashed #ffb74d;">
                <b style="color: #ef6c00;">🐾 [ 🖼️ お客様の写真（ヨコ長） ] 🐾<br>ーーーーーーーーーーー<br>🗓️ 1月・2月・3月（3ヶ月表示）</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif data["template"] == "C":
        st.markdown("""
        <div class="template-card" style="border-color: #64b5f6;">
            <span style="font-size: 20px; font-weight: bold; color: #1565c0;">【台紙 C】シンプル・タテ型タイプ</span><br>
            <span style="font-size: 14px; color: #666;">すっきりした文字と実用的な書き込みスペースを重視した、どんな場所にも合うスマートなタテ型カレンダー</span>
            <div style="background: #e3f2fd; height: 160px; width: 60%; margin: 15px auto; border-radius: 6px; display: flex; align-items: center; justify-content: center; border: 1px dashed #64b5f6;">
                <b style="color: #1565c0;">[ 🖼️ お客様の写真 ]<br><br>ーーーーーーー<br><br>🗓️ 1月・2月・3月<br>（縦並び配置）</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    # 枚数入力
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
    
    data["name"] = st.text_input("お名前")
    data["zip"] = st.text_input("郵便番号 (例: 123-4567)")
    data["address"] = st.text_input("ご住所")
    data["tel"] = st.text_input("電話番号")
    data["email"] = st.text_input("メールアドレス")
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
        st.write(f"・連絡先: {data['tel']} / {data['email']}")
        
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
