import streamlit as st
from PIL import Image
import io
import zipfile

# ページの設定
st.set_page_config(page_title="スクショ切り取り職人", layout="centered")

st.title("🍄 スクショの上の部分だけカットするやつ")
st.write("iPhoneのステータスバーなどが映り込んだ部分を一括でトリミングするよ！")

# 1. ユーザーに画像をアップロードしてもらう
uploaded_files = st.file_uploader("ここに画像を放り込んでね（複数OK）", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 2. トリミングする高さを決めるスライダー（デフォルト120pxくらいかな？）
cut_height = st.slider("上から何ピクセル削る？", min_value=0, max_value=300, value=130, step=10)

if uploaded_files:
    # ダウンロード用のZIPファイルを作る準備
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        # アップロードされた画像を1枚ずつ処理
        for uploaded_file in uploaded_files:
            try:
                # 画像を開く
                img = Image.open(uploaded_file)
                width, height = img.size

                # 【ここが重要！】切り取る範囲を決める
                # (左端, 切り取る高さ, 右端, 下端)
                if height > cut_height:
                    cropped_img = img.crop((0, cut_height, width, height))
                    
                    # メモリ上に保存
                    img_byte_arr = io.BytesIO()
                    # 元のフォーマット(PNG/JPG)で保存
                    img_format = uploaded_file.type.split('/')[-1].upper()
                    if img_format == 'JPEG': img_format = 'JPEG' # Pillow対応
                    
                    cropped_img.save(img_byte_arr, format=img_format)
                    
                    # ZIPに追加
                    zf.writestr(f"fixed_{uploaded_file.name}", img_byte_arr.getvalue())
            except Exception as e:
                st.error(f"エラーだっち… {uploaded_file.name}: {e}")

    # 3. ZIPファイルをダウンロードボタンとして表示
    st.success(f"{len(uploaded_files)}枚の画像を処理したよ！🍄")
    
    st.download_button(
        label="まとめてダウンロードする📦",
        data=zip_buffer.getvalue(),
        file_name="cleaned_screenshots.zip",
        mime="application/zip"
    )
