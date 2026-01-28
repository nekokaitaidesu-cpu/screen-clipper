import streamlit as st
from PIL import Image
import io
import zipfile
from streamlit_cropper import st_cropper

st.set_page_config(page_title="スクショ切り取り職人V5", layout="wide")

# st.title("🍄 スクショ切り取り職人 V5 (スマホ長押し対応版)")
st.write("1枚目で範囲を決めて、結果を画面に表示するよ！長押し保存してね！👆")

# ファイルアップロード
uploaded_files = st.file_uploader("画像をまとめてアップロードしてね", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    # --- 1. 基準となる画像（1枚目）で設定を決める ---
    st.subheader("① カット範囲を決める（1枚目の画像）")
    
    first_image = Image.open(uploaded_files[0])
    orig_w, orig_h = first_image.size
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("👇 この赤い枠で「残したい範囲」を囲ってね！")
        box_coords = st_cropper(
            first_image,
            realtime_update=True,
            box_color='#FF0000',
            aspect_ratio=None,
            return_type='box'
        )
        
        c_left = box_coords['left']
        c_top = box_coords['top']
        c_width = box_coords['width']
        c_height = box_coords['height']
        c_right = c_left + c_width
        c_bottom = c_top + c_height

        # 比率計算
        ratio_left = c_left / orig_w
        ratio_top = c_top / orig_h
        ratio_right = c_right / orig_w
        ratio_bottom = c_bottom / orig_h

    with col2:
        st.write("🎬 仕上がりプレビュー")
        preview_img = first_image.crop((c_left, c_top, c_right, c_bottom))
        st.image(preview_img, caption="プレビュー", use_column_width=True)

    # --- 2. 全画像処理 & 表示 & ZIP作成 ---
    st.write("---")
    if st.button("この設定で加工スタート！", type="primary"):
        
        st.header("👇 ここから長押しで保存できるよ！")
        
        # 処理した画像を一時保存するリスト
        processed_images = []
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # プログレスバー
            progress_bar = st.progress(0)
            
            # 画像を横に並べるための準備（スマホだと縦に見やすくなるように設定）
            # Streamlitのカラム機能を使わずに、そのまま縦に並べたほうがスマホは保存しやすいかも！
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    img = Image.open(uploaded_file)
                    curr_w, curr_h = img.size
                    
                    # 座標計算
                    new_left = int(curr_w * ratio_left)
                    new_top = int(curr_h * ratio_top)
                    new_right = int(curr_w * ratio_right)
                    new_bottom = int(curr_h * ratio_bottom)

                    new_left = max(0, new_left)
                    new_top = max(0, new_top)
                    new_right = min(curr_w, new_right)
                    new_bottom = min(curr_h, new_bottom)

                    final_crop = img.crop((new_left, new_top, new_right, new_bottom))
                    
                    # --- 【ここが新機能】画面に表示！ ---
                    st.image(final_crop, caption=f"{i+1}枚目: {uploaded_file.name}", use_column_width=True)
                    
                    # ZIP用保存処理
                    img_byte_arr = io.BytesIO()
                    img_format = uploaded_file.type.split('/')[-1].upper()
                    if img_format == 'JPEG': img_format = 'JPEG'
                    elif img_format == 'JPG': img_format = 'JPEG'
                    save_format = img_format if img_format in ['PNG', 'JPEG'] else 'PNG'
                        
                    final_crop.save(img_byte_arr, format=save_format)
                    new_filename = f"{i+1:03d}_{uploaded_file.name}"
                    zf.writestr(new_filename, img_byte_arr.getvalue())
                    
                except Exception as e:
                    st.error(f"エラー: {uploaded_file.name} - {e}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))

        st.success("全部できたよ！まとめて欲しいときは下のボタンからZIPでどうぞ👇")
        
        st.download_button(
            label="📦 まとめてZIPでダウンロード",
            data=zip_buffer.getvalue(),
            file_name="images_v5.zip",
            mime="application/zip"
        )
