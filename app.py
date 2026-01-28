import streamlit as st
from PIL import Image
import io
import zipfile

from streamlit_cropper import st_cropper

st.set_page_config(page_title="スクショ切り取り職人V4", layout="wide")

st.title("🍄 スクショ切り取り職人 V4 (上下左右自由カット版)")
st.write("1枚目で決めた「赤い枠の範囲」で、全画像を同じ比率で切り取るよ！✂️")

# ファイルアップロード
uploaded_files = st.file_uploader("画像をまとめてアップロードしてね", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    # --- 1. 基準となる画像（1枚目）で設定を決める ---
    st.subheader("① カット範囲を決める（1枚目の画像）")
    
    # 1枚目を読み込む
    first_image = Image.open(uploaded_files[0])
    orig_w, orig_h = first_image.size
    
    # 画面分割
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("👇 この赤い枠で「残したい範囲」を囲ってね！上下左右どこでもOK！")
        # 【重要】return_type='box' を指定して、画像じゃなくて「座標」を受け取るよ！
        box_coords = st_cropper(
            first_image,
            realtime_update=True,
            box_color='#FF0000',
            aspect_ratio=None,
            return_type='box' # ここがポイント！
        )
        
        # 受け取った座標（left, top, width, height）を整理
        c_left = box_coords['left']
        c_top = box_coords['top']
        c_width = box_coords['width']
        c_height = box_coords['height']
        # 右端と下端の座標を計算
        c_right = c_left + c_width
        c_bottom = c_top + c_height

        # --- 他の画像にも適用するために「比率」を計算しておくよ ---
        # (画像サイズが微妙に違っても対応できるようにするため)
        ratio_left = c_left / orig_w
        ratio_top = c_top / orig_h
        ratio_right = c_right / orig_w
        ratio_bottom = c_bottom / orig_h

    with col2:
        st.write("🎬 仕上がりプレビュー")
        # 座標を使ってプレビュー画像を作成
        preview_img = first_image.crop((c_left, c_top, c_right, c_bottom))
        st.image(preview_img, caption="この範囲で全画像をカットするよ！", use_column_width=True)
        
        st.write("---")
        st.write(f"📐 **カット情報 (1枚目基準)**")
        st.write(f"- 上カット: {c_top} px")
        st.write(f"- 下カット: {orig_h - c_bottom} px")

   # ... (上のimport部分はそのまま)

    # --- 2. 全画像に適用してダウンロード ---
    st.write("---")
    if st.button("この設定で全画像を処理してZIP作成！🍄", type="primary"):
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            progress_bar = st.progress(0)
            
            # 【変更点】enumerateを使って、0から順番に番号を振るよ！
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    img = Image.open(uploaded_file)
                    curr_w, curr_h = img.size
                    
                    # --- さっきの比率計算ロジック（そのまま） ---
                    new_left = int(curr_w * ratio_left)
                    new_top = int(curr_h * ratio_top)
                    new_right = int(curr_w * ratio_right)
                    new_bottom = int(curr_h * ratio_bottom)

                    new_left = max(0, new_left)
                    new_top = max(0, new_top)
                    new_right = min(curr_w, new_right)
                    new_bottom = min(curr_h, new_bottom)

                    final_crop = img.crop((new_left, new_top, new_right, new_bottom))
                    
                    # 保存処理
                    img_byte_arr = io.BytesIO()
                    img_format = uploaded_file.type.split('/')[-1].upper()
                    if img_format == 'JPEG': img_format = 'JPEG'
                    elif img_format == 'JPG': img_format = 'JPEG'
                    save_format = img_format if img_format in ['PNG', 'JPEG'] else 'PNG'
                        
                    final_crop.save(img_byte_arr, format=save_format)
                    
                    # 【ここがポイント！】ファイル名に連番をつける (001_画像名.jpg)
                    # これでスマホ側でも順番が守られるよ！
                    new_filename = f"{i+1:03d}_{uploaded_file.name}"
                    
                    zf.writestr(new_filename, img_byte_arr.getvalue())
                    
                except Exception as e:
                    st.error(f"エラー: {uploaded_file.name} - {e}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))

        st.success(f"完了！ {len(uploaded_files)}枚 処理したよ！")
        
        st.download_button(
            label="📦 ダウンロードする",
            data=zip_buffer.getvalue(),
            file_name="perfect_cropped_images.zip",
            mime="application/zip"
        )
