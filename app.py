import streamlit as st
import subprocess
import json
import time
import os
import sys

st.set_page_config(page_title="Live News Scraper", page_icon="📰", layout="wide")

st.markdown(
    """
    <style>
        .big-title { font-size: 32px !important; font-weight: bold; color: #E63946; text-align: center; }
        .sub-text { font-size: 16px !important; color: #555; text-align: center; }
        .article-title { font-size: 22px; font-weight: bold; color: #1D3557; }
        .article-summary { font-size: 16px; color: #333; }
        .read-more { color: #E63946; font-weight: bold; text-decoration: none; }
        .sidebar-title { font-size: 18px !important; font-weight: bold; color: #1D3557; }
        .stButton>button { background-color: #457B9D; color: white; border-radius: 10px; }
        .stButton>button:hover { background-color: #1D3557; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="big-title">Live News Scraper & Summarizer 📰</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Get the latest news with summarized content and Hindi translation!</p>', unsafe_allow_html=True)

CATEGORY_MAPPING = {
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Meerut", "Prayagraj", "Noida", "Ghaziabad", "Agra", "Varanasi"],
    "Maharashtra": ["Mumbai", "Pune", "Navi Mumbai", "Nagpur", "Nashik", "Aurangabad", "Thane"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem"],
    "West Bengal": ["Kolkata"],
    "Delhi": [],
    "Punjab": ["Amritsar", "Ludhiana", "Chandigarh"],
    "Haryana": ["Faridabad", "Gurgaon"],
    "Bihar": ["Patna"],
    "Assam": ["Guwahati"],
    "Kerala": [], "Goa": [], "Manipur": [], "Mizoram": [], "Tripura": [], "Nagaland": [], "Sikkim": [],
    "Arunachal Pradesh": [], "Meghalaya": [], "Chhattisgarh": [], "Jharkhand": [], "Uttarakhand": [],
    "Odisha": [], "Himachal Pradesh": [], "Ladakh": [], "Jammu and Kashmir": [], "Andaman and Nicobar": [],
}

SPECIAL_CATEGORIES = {
    "World": ["US", "UK", "Pakistan", "Europe", "China", "Middle East", "Rest of World"],
    "Business": ["Financial Literacy", "India Business", "International Business"],
    "Sports": ["Cricket", "Tennis", "Badminton", "Hockey", "Football", "Chess"],
    "Entertainment": ["ETimes"],
    "Lifestyle": ["Health & Fitness"],
    "Technology": [],
}

st.sidebar.markdown('<p class="sidebar-title">Select News Category:</p>', unsafe_allow_html=True)

BROAD_CATEGORIES = ["State", "World", "Business", "Sports", "Entertainment", "Lifestyle", "Technology"]

# Store dropdown selections in session_state to persist values
if "broad_category" not in st.session_state:
    st.session_state.broad_category = "Select a Category"
if "selected_state" not in st.session_state:
    st.session_state.selected_state = "Select a State"
if "selected_subcategory" not in st.session_state:
    st.session_state.selected_subcategory = "All"

# ✅ First dropdown: Broad category
broad_category = st.sidebar.selectbox("Choose a category:", ["Select a Category"] + BROAD_CATEGORIES, key="broad_category")

# ✅ If "State" is selected, show states dropdown
if broad_category == "State":
    selected_state = st.sidebar.selectbox("Choose a state:", ["Select a State"] + list(CATEGORY_MAPPING.keys()), key="selected_state")
    
    if selected_state in CATEGORY_MAPPING and CATEGORY_MAPPING[selected_state]:
        selected_subcategory = st.sidebar.selectbox("Choose a city:", ["All"] + CATEGORY_MAPPING[selected_state], key="selected_subcategory")

# ✅ If another category is selected, check for subcategories
elif broad_category in SPECIAL_CATEGORIES:
    subcategories = SPECIAL_CATEGORIES[broad_category]
    if subcategories:
        selected_subcategory = st.sidebar.selectbox("Choose a subcategory:", ["All"] + subcategories, key="selected_subcategory")

urls = []

# ✅ Fetch news button
if st.sidebar.button("Fetch News 📰"):
    if broad_category == "State" and selected_state and selected_state != "Select a State":
        state_name = selected_state.lower().replace(" ", "-")
        
        if selected_subcategory and selected_subcategory != "All":
            city_name = selected_subcategory.lower().replace(" ", "-")
            urls.append(f"https://timesofindia.indiatimes.com/city/{city_name}")
        else:
            urls.append(f"https://timesofindia.indiatimes.com/india/{state_name}")

    elif broad_category in SPECIAL_CATEGORIES:
        if selected_subcategory and selected_subcategory != "All":
            subcat_name = selected_subcategory.lower().replace(" ", "-")
            urls.append(f"https://timesofindia.indiatimes.com/{broad_category.lower()}/{subcat_name}")
        else:
            urls.append(f"https://timesofindia.indiatimes.com/{broad_category.lower()}")

    with open("urls.json", "w", encoding="utf-8") as f:
        json.dump(urls, f, indent=4)

    with open("scraper_log.txt", "w") as log:
        result = subprocess.run([sys.executable, "scraper.py"], stdout=log, stderr=log)

    if result.returncode != 0:
        st.error("Error in scraper.py! Check scraper_log.txt.")
        st.stop()

    if os.path.exists("toi_articles.json"):
        with open("summarizer_log.txt", "w") as log:
            result = subprocess.run([sys.executable, "summarizer.py"], stdout=log, stderr=log)

        if result.returncode != 0:
            st.error("Error in summarizer.py! Check summarizer_log.txt.")
            st.stop()

        time.sleep(3)
        try:
            with open("processed_articles.json", "r", encoding="utf-8") as f:
                articles = json.load(f)

            if articles:
                for i, article in enumerate(articles, 1):
                    with st.container():
                        st.markdown(f'<p class="article-title">{i}. {article["title"]}</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="article-summary">{article["summary"]} <a href="{article["url"]}" class="read-more">[Read more]</a></p>', unsafe_allow_html=True)
                        with st.expander("Show Hindi Translation"):
                            st.write(article["translated_text"])
                        st.markdown("---")
            else:
                st.warning("No articles found.")
        except FileNotFoundError:
            st.error("Failed to find processed data.")
    else:
        st.warning("Please select a valid category before fetching news.")
