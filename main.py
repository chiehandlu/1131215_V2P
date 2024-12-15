import streamlit as st
from youtube_utils import get_video_info, download_subtitle, download_translated_subtitle
from subtitle_processor import convert_subtitle, edit_subtitle
from search_utils import search_keywords, generate_timestamps
from database import save_to_database, load_from_database

def main():
    st.title("YouTube 字幕擷取與管理工具")

    # 單支/批量影片字幕擷取
    st.header("字幕擷取")
    video_url = st.text_input("輸入 YouTube 影片 URL")
    language = st.selectbox("選擇字幕語言", ["en", "zh", "zh-TW", "zh-CN", "ja", "ko"])
    auto_translate = st.checkbox("使用自動翻譯 (如果原始字幕不可用)", value=True)
    
    if st.button("擷取字幕"):
        if video_url:
            with st.spinner('正在擷取字幕...'):
                video_info = get_video_info(video_url)
                if video_info:
                    subtitle = download_subtitle(video_url, language, auto_translate)
                    if subtitle:
                        st.success(f"成功擷取 {video_info['title']} 的字幕")
                        st.session_state['current_subtitle'] = subtitle
                        st.session_state['video_info'] = video_info
                    else:
                        st.error("無法擷取字幕")
                else:
                    st.error("無法獲取影片資訊")

    # 字幕格式轉換與編輯
    st.header("字幕格式轉換與編輯")
    
    # 檢查是否有當前字幕資料
    if 'current_subtitle' in st.session_state:
        output_format = st.selectbox("選擇輸出格式", ["TXT", "SRT", "CSV"])
        converted_subtitle = convert_subtitle(st.session_state['current_subtitle'], output_format)
        
        # 顯示轉換後的字幕
        st.text_area("編輯字幕", converted_subtitle, height=300)
        
        # 加入下載按鈕
        if st.download_button(
            label="下載字幕檔案",
            data=converted_subtitle,
            file_name=f"subtitle.{output_format.lower()}",
            mime="text/plain"
        ):
            st.success("字幕已下載")
            
    else:
        st.info("請先擷取字幕")

    # 關鍵字搜尋與標記
    if st.session_state.get('current_subtitle'):
        st.header("關鍵字搜尋與標記")
        search_query = st.text_input("輸入搜尋關鍵字")
        
        if search_query and st.button("搜尋"):
            # 實作搜尋邏輯
            pass

if __name__ == "__main__":
    main() 