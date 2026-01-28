import streamlit as st
from PIL import Image
import io
import zipfile
# 新しい助っ人をインポート！
from streamlit_cropper import st_cropper

st.set_page_config(page_title="スクショ切り取り職人V3", layout="wide")

st.title("🍄 スクショ切り取り職人 V3 (ビジュアル版)")
st.write("1枚目の画像で「残したい範囲」を囲ってね！その設定で全部カットするよ！✂️")

# ファイルアップロード
uploaded_files = st.file_uploader("画像をまとめてアップロードしてね", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    # --- 1. 基準となる画像（1枚目）で設定を決める ---
    st.subheader("① カット範囲を決める（1枚目の画像）")
    
    # 1枚目を読み込む
    first_image = Image.open(uploaded_files[0])
    
    # 画面分割（左：操作画面、右：結果プレビュー）
    col1, col2 = st.columns([2, 1]) # 左を広めに
    
    with col1:
        st.info("👇 この枠を動かして「残したい部分（下の部分）」を囲ってね！")
        # ここが魔法のクロップ機能！
        # box_color: 枠の色, aspect_ratio: 自由な形にするならNone
        cropped_box = st_cropper(first_image, realtime_update=True, box_color='#FF0000', aspect_ratio=None)
        
        # 枠の情報を取得（これで「上から何ピクセル削ったか」を計算するよ）
        # st_cropperは「切り抜かれた画像」を返してくるけど、
        # 内部的に座標を知るために、ちょっと計算するよ
        
        # 元の高さ
        orig_w, orig_h = first_image.size
        # 切り抜かれた後の高さ
        crop_w, crop_h = cropped_box.size
        
        # 「上からどれくらい削られたか」 = 元の高さ - 下に残った画像の高さ
        # （※厳密にはboxのY座標が知りたいけど、簡易的に「下合わせ」で計算するね）
        # もし「上だけ切りたい（下はそのまま）」なら、枠の下辺は一番下まで伸ばしておいてね！
        
    with col2:
        st.write("🎬 仕上がりプレビュー")
        st.image(cropped_box, caption="今の設定だとこうなるよ！", use_column_width=True)
        
        # カットする高さを計算（単純に、元の高さと今の高さの差分を計算）
        cut_pixels = orig_h - crop_h
        st.metric(label="上からカットされる量", value=f"約 {cut_pixels} px")

    # --- 2. 全画像に適用してダウンロード ---
    if st.button("この設定で全画像を処理してZIP作成！🍄"):
        
        # ZIPを作る
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # プログレスバー（進捗バー）を出してみる！
            progress_bar = st.progress(0)
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    img = Image.open(uploaded_file)
                    width, height = img.size
                    
                    # プレビューで決まった「上からカットする量」を使ってトリミング
                    # (0, cut_pixels, width, height) -> 左, 上, 右, 下
                    if height > cut_pixels:
                        # 念のため、画像からはみ出さないように調整
                        final_crop = img.crop((0, cut_pixels, width, height))
                        
                        # 保存処理
                        img_byte_arr = io.BytesIO()
                        img_format = uploaded_file.type.split('/')[-1].upper()
                        if img_format == 'JPEG': img_format = 'JPEG'
                        
                        final_crop.save(img_byte_arr, format=img_format)
                        zf.writestr(f"cut_{uploaded_file.name}", img_byte_arr.getvalue())
                    
                except Exception as e:
                    st.error(f"エラー: {uploaded_file.name} - {e}")
                
                # 進捗バーを更新
                progress_bar.progress((i + 1) / len(uploaded_files))

        st.success(f"完了！ {len(uploaded_files)}枚 処理したよ！")
        
        st.download_button(
            label="📦 ダウンロードする",
            data=zip_buffer.getvalue(),
            file_name="smart_cropped_images.zip",
            mime="application/zip",
            type="primary"
        )
