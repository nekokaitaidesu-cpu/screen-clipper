import streamlit as st
from PIL import Image
import io
import zipfile

# ページの設定（ワイド表示にする）
st.set_page_config(page_title="スクショ切り取り職人V2", layout="wide")

st.title("🍄 スクショ切り取り職人 V2")
st.write("プレビューを見ながら、機種に合わせて完璧にカットできるよ！")

# --- サイドバー（設定エリア） ---
st.sidebar.header("✂️ 設定メニュー")

# 機種ごとのステータスバーの高さ目安（ピクセル）
# ※機種によって微妙に違うから、自分のスマホに合わせて調整してみてね！
device_presets = {
    "手動で調整 (カスタム)": 0,
    "iPhone 14/15/16 Pro (Dynamic Island)": 160,
    "iPhone 12/13/14 (ノッチあり)": 140,
    "iPhone SE / 8 (ホームボタンあり)": 40,
    "Android (一般的)": 70,
}

# セレクトボックスで機種を選ぶ
selected_device = st.sidebar.selectbox("スマホの機種は？", list(device_presets.keys()))

# スライダー（機種を選ぶと、自動で数値が変わるよ！）
default_value = device_presets[selected_device]
cut_height = st.sidebar.slider(
    "カットする高さ (px)", 
    min_value=0, 
    max_value=300, 
    value=default_value if default_value > 0 else 130, 
    step=2
)

# --- メインエリア ---
uploaded_files = st.file_uploader("ここに画像を放り込んでね（複数OK）", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    st.write("---")
    st.subheader(f"📸 プレビュー ({len(uploaded_files)}枚)")
    
    # ZIPを作る準備
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # 画像を処理して表示
        for uploaded_file in uploaded_files:
            try:
                img = Image.open(uploaded_file)
                width, height = img.size

                # 切り取り処理
                if height > cut_height:
                    cropped_img = img.crop((0, cut_height, width, height))
                    
                    # 画面にBefore/Afterを並べて表示（カラム機能）
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(img, caption="Before (元の画像)", use_column_width=True)
                    with col2:
                        st.image(cropped_img, caption=f"After ({cut_height}pxカット)", use_column_width=True)
                    
                    # 保存用データ作成
                    img_byte_arr = io.BytesIO()
                    img_format = uploaded_file.type.split('/')[-1].upper()
                    if img_format == 'JPEG': img_format = 'JPEG'
                    
                    cropped_img.save(img_byte_arr, format=img_format)
                    
                    # ZIPに追加 (ファイル名の頭に cut_ をつける)
                    zf.writestr(f"cut_{uploaded_file.name}", img_byte_arr.getvalue())
            
            except Exception as e:
                st.error(f"エラー: {uploaded_file.name} - {e}")

    st.write("---")
    # ダウンロードボタン
    st.success("いい感じにカットできた？ ダウンロードはこちら👇")
    st.download_button(
        label="📦 まとめてダウンロード",
        data=zip_buffer.getvalue(),
        file_name="cut_screenshots.zip",
        mime="application/zip",
        type="primary" # ボタンを目立たせる色にする
    )
