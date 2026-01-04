import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import uuid
import os
from openai import OpenAI
from llama_cpp import Llama

# --- 1. 页面配置 (必须在第一行) ---
st.set_page_config(
    page_title="SPM Scholarship Check",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. API 设置 ---
# ⚠️ 部署指南：
# 1. 本地运行：在 .streamlit/secrets.toml 中配置 DEEPSEEK_API_KEY
# 2. Cloud 部署：在 App Settings -> Secrets 中添加
api_key = st.secrets.get("DEEPSEEK_API_KEY")

try:
    if api_key:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        api_ready = True
    else:
        api_ready = False
        llm = Llama(
            model_path="./llama-3-8b.Q4_K_M.gguf", 
            n_ctx=2048, # Context window size
            verbose=False
        )        
except Exception as e:
    api_ready = False

def AskDeepSeek(prompt_text):
    """调用 DeepSeek AI 获取升学建议"""
    if not api_ready:
        output = llm(
        f"Q: You are an experienced Malaysian education counselor (Cikgu). Your tone is encouraging, empathetic, and realistic. Analyze the student's SPM results and wish. 1. Recommend best scholarships. 2. Suggest alternatives if none qualify. 3. CRITICAL RULE: You MUST reply primarily in CHINESE (Malaysian Mandarin). Even if the user asks nonsense or inappropriate questions, you must politely guide them back or refuse in CHINESE. Do not switch to English blocks unless explaining specific terms.{prompt_text} A:", 
        max_tokens=1000, 
        stop=["Q:", "\n"], 
        echo=True
        )
        return output['choices'][0]['text']
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                # 🌟 AI 设定优化：强制中文 + 马来西亚升学顾问人设
                {"role": "system", "content": "You are an experienced Malaysian education counselor (Cikgu). Your tone is encouraging, empathetic, and realistic. Analyze the student's SPM results and wish. 1. Recommend best scholarships. 2. Suggest alternatives if none qualify. 3. CRITICAL RULE: You MUST reply primarily in CHINESE (Malaysian Mandarin). Even if the user asks nonsense or inappropriate questions, you must politely guide them back or refuse in CHINESE. Do not switch to English blocks unless explaining specific terms."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI 连接失败: {str(e)}。请检查网络或余额。"

# --- 3. CSS 美化 ---
st.markdown("""
<style>
    /* === 侧边栏收起/展开样式 === */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important; left: 0 !important; top: 0 !important;
        width: 32px !important; height: 100vh !important;
        background-color: #FFFDF5 !important;
        border-right: 2px solid #FDE68A !important;
        z-index: 100000 !important;
        display: flex !important; align-items: flex-start !important; justify-content: center !important;
        padding-top: 20px !important; transition: background-color 0.3s;
    }
    [data-testid="stSidebarCollapsedControl"]:hover { background-color: #FEF3C7 !important; cursor: pointer; }
    [data-testid="stSidebarCollapsedControl"] svg {
        color: #D97706 !important; fill: #D97706 !important;
        width: 20px !important; height: 20px !important; stroke-width: 3px !important;
    }
    section[data-testid="stSidebar"] { width: 450px !important; background-color: #FFFDF5; border-right: 1px solid #F3E8D3; }

    /* === 界面洁癖处理 === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-1plm3a3 a {display: none !important;} 
    h1 a, h2 a, h3 a {display: none !important;}
    .block-container {padding-top: 2rem; padding-bottom: 5rem;}
    
    /* === 输入框与按钮优化 === */
    button[data-testid="stNumberInputStepDown"] { display: none !important; }
    button[data-testid="stNumberInputStepUp"] { display: none !important; }
    .stSelectbox { margin-bottom: 0px; }
    div.stButton > button { width: 100%; border-radius: 8px; height: 45px; }

    /* === 删除按钮样式 === */
    div[data-testid="column"] button {
        border-color: #FECACA; color: #DC2626; border-radius: 50%;
        width: 35px; height: 35px;
    }
    div[data-testid="column"] button:hover { background-color: #FEF2F2; border-color: #EF4444; }

    /* === 结果卡片样式 === */
    .scholarship-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 6px solid #10B981; animation: fadeIn 0.8s; transition: transform 0.2s;
    }
    .scholarship-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px rgba(0,0,0,0.1); }
    
    /* === 标签与文本样式 === */
    .tag { display: inline-block; background-color: #E0F2FE; color: #0284C7; padding: 2px 10px; border-radius: 15px; font-size: 12px; margin-right: 5px; font-weight: 600; }
    .info-text { font-size: 13px; color: #4B5563; margin-top: 8px; line-height: 1.5; }
    .field-tag { color: #D97706; font-weight: bold; } 
    .block-tag { color: #DC2626; font-weight: bold; } 
    .b40-tag { color: #059669; font-weight: bold; }     

    /* === AI 建议框样式 === */
    .ai-box {
        background-color: #F0FDF4; border: 1px solid #BBF7D0;
        padding: 20px; border-radius: 10px; margin-top: 20px;
        color: #166534; animation: fadeIn 0.8s ease-in;
    }
    .ai-box h4 { margin-top: 0; color: #15803d; }
    
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- 4. 基础数据 ---

STATE_LIST = [
    "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", 
    "Pahang", "Penang", "Perak", "Perlis", "Sabah", 
    "Sarawak", "Selangor", "Terengganu", "W.P. Kuala Lumpur", 
    "W.P. Labuan", "W.P. Putrajaya"
]

SUBJECT_LIST = [
    "Bahasa Melayu", "Bahasa Inggeris", "Sejarah", "Matematik", 
    "Matematik Tambahan", "Fizik", "Kimia", "Biologi", "Sains",
    "Pendidikan Islam", "Pendidikan Moral", "Tasawwur Islam", 
    "Pendidikan Al-Quran dan Al-Sunnah", "Pendidikan Syari'ah Islamiah",
    "Prinsip Perakaunan", "Ekonomi", "Perniagaan", 
    "Sains Komputer", "Reka Cipta", "Grafik Komunikasi Teknikal",
    "Pendidikan Seni Visual", "Sains Rumah Tangga", "Pertanian",
    "Bahasa Cina", "Bahasa Tamil", "Bahasa Arab", "Bahasa Iban", "Bahasa Kadazandusun",
    "Kesusasteraan Melayu Komunikatif", "Kesusasteraan Inggeris"
]

# --- 5. 完整奖学金数据库 (含 PPN 修复) ---
SCHOLARSHIP_DB = [
    # === TIER 1: JPA 家族 ===
    {
        "name": "JPA Program Penajaan Nasional (PPN)",
        "provider": "JPA",
        "tags": ["全球 Top 10", "全额资助"],
        # 🌟 修复：9个 A+，开启 must_all_A_minus 严格模式
        "min_A_total": 9, "allow_A_minus": False, "min_A_plus": 9,        
        "hard_req": {
            "Bahasa Melayu": ["A+"], 
            "Bahasa Inggeris": ["A+"],
            "Sejarah": ["A+"],
            "Matematik": ["A+"],
            "Matematik Tambahan": ["A+"],
            "Fizik": ["A+"],
            "Kimia": ["A+"]
        },
        "must_all_A_minus": True, # <--- 关键开关：所有科目最低 A-
        "koko_marks": 8.5, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_block": "医学/牙医/药剂 (Medicine/Dentistry/Pharmacy)", 
        "desc": "JPA 最顶级的奖学金。要求核心科目全 A+，且其余所有科目不得低于 A-。",
        "link": "https://esilav2.jpa.gov.my/"
    },
    {
        "name": "JPA LSPM (Program Khas Dalam Negara)",
        "provider": "JPA",
        "tags": ["国内顶尖大学", "GLU/IPTS"],
        "min_A_total": 9, "allow_A_minus": False, "min_A_plus": 9,
        "hard_req": {"Bahasa Melayu": ["A+", "A"], "Sejarah": ["A+", "A"]},
        "koko_marks": 8.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "资助在国内顶尖大学 (如 UTP, UNITEN, MMU, IMU 等) 就读预科及本科。",
        "link": "https://esilav2.jpa.gov.my/"
    },
    {
        "name": "JPA PPF (Perubatan/Pergigian/Farmasi)",
        "provider": "JPA",
        "tags": ["医学专项"],
        "min_A_total": 9, "allow_A_minus": False, "min_A_plus": 7, 
        "hard_req": {"Biologi": ["A+", "A"], "Kimia": ["A+", "A"], "Fizik": ["A+", "A"], "Matematik": ["A+", "A"]},
        "koko_marks": 8.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_only": "医学/牙医/药剂 (Medicine/Dentistry/Pharmacy)",
        "desc": "医科、牙医、药剂系专项资助。需签署政府服务合约。",
        "link": "https://esilav2.jpa.gov.my/"
    },
    {
        "name": "JPA JKPJ (日韩法德工程)",
        "provider": "JPA",
        "tags": ["工程系", "日韩法德"],
        "min_A_total": 7, "allow_A_minus": False, "min_A_plus": 5,
        "hard_req": {"Matematik": ["A+", "A"], "Matematik Tambahan": ["A+", "A"], "Fizik": ["A+", "A"]},
        "koko_marks": 8.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_only": "工程 (Engineering), 理科 (Science/Tech)",
        "desc": "前往日、韩、法、德学习工程与科技。包含外语预科班。",
        "link": "https://esilav2.jpa.gov.my/"
    },
    
    # === TIER 2: Corporate & Overseas Giants ===
    {
        "name": "Petronas PESP",
        "provider": "Petronas",
        "tags": ["油气/工程", "就业保障"],
        "min_A_total": 8, "allow_A_minus": False, "min_A_plus": 4,        
        "hard_req": {"Matematik": ["A+", "A"], "Bahasa Inggeris": ["A+", "A"]}, 
        "koko_marks": 8.5, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_block": "医学 (Medicine), 师范 (Education)",
        "desc": "毕业后进入 Petronas 工作。极度看重领导力。",
        "link": "https://educationsponsorship.petronas.com.my/"
    },
    {
        "name": "Shell Malaysia Scholarship",
        "provider": "Shell",
        "tags": ["工程/地质", "全额资助"],
        "min_A_total": 8, "allow_A_minus": False, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 8.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_only": "工程, 地质, 商业 (Eng/Geo/Commercial)",
        "desc": "Shell 全额奖学金，需通过虚拟工作评估。",
        "link": "https://www.shell.com.my/careers/students-and-graduates/scholarships.html"
    },
    {
        "name": "Singapore ASEAN Scholarship",
        "provider": "MOE Singapore",
        "tags": ["新加坡", "A-Level", "全额"],
        "min_A_total": 8, "allow_A_minus": False, "min_A_plus": 6,
        "hard_req": {"Bahasa Inggeris": ["A+", "A"]}, 
        "koko_marks": 8.5, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "全额资助在新加坡完成 Pre-U (A-Level)。极度看重英语。",
        "link": "https://www.moe.gov.sg/financial-matters/awards-scholarships/asean-scholarship/malaysia"
    },
    {
        "name": "CIMB ASEAN Scholarship",
        "provider": "CIMB",
        "tags": ["金融/科技", "数据科学"],
        "min_A_total": 8, "allow_A_minus": False, "min_A_plus": 0,        
        "hard_req": {}, "koko_marks": 8.5, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "涵盖金融与科技数据领域。提供导师指导与直接就业机会。",
        "link": "https://www.cimb.com/en/careers/students/cimb-asean-scholarship.html"
    },
    {
        "name": "Bank Negara Kijang Scholarship",
        "provider": "Bank Negara",
        "tags": ["经济/法律", "精英"],
        "min_A_total": 8, "allow_A_minus": False, "min_A_plus": 8,        
        "hard_req": {}, "koko_marks": 8.5, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_only": "经济, 会计, 金融, 法律 (Economics/Law/Finance)",
        "desc": "央行奖学金。不资助纯医学或纯工程 (除非 Fintech 相关)。",
        "link": "https://www.bnm.gov.my/careers/scholarships"
    },
    {
        "name": "Khazanah Global Scholarship",
        "provider": "Yayasan Khazanah",
        "tags": ["未来领袖", "GLC"],
        "min_A_total": 8, "allow_A_minus": False, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 9.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "培养 GLC (官联公司) 未来领袖，极度看重课外活动与领导潜质。",
        "link": "https://www.yayasankhazanah.com.my/"
    },
    {
        "name": "Yayasan UEM Overseas",
        "provider": "Yayasan UEM",
        "tags": ["工程/商科", "KYUEM"],
        "min_A_total": 7, "allow_A_minus": False, "min_A_plus": 0,
        "hard_req": {"Bahasa Inggeris": ["A+", "A"], "Matematik": ["A+", "A"]},
        "koko_marks": 8.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "国际工程领域首选，包含顶尖预科 KYUEM 入学资格。",
        "link": "https://yayasanuem.org/scholarships/"
    },
    {
        "name": "Gamuda Scholarship",
        "provider": "Gamuda",
        "tags": ["建筑", "工程"],
        "min_A_total": 7, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 8.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "毕业后进入基建巨头 Gamuda。看重性格与沟通能力。",
        "link": "https://gamuda.com.my/sustainability/yayasan-gamuda/gamuda-scholarship/"
    },
    {
        "name": "YTL Foundation Scholarship",
        "provider": "YTL",
        "tags": ["本地私立", "Heriot-Watt"],
        "min_A_total": 6, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 7.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "资助本地私立大学学费 (如 Heriot-Watt, UNITEN)。",
        "link": "https://ytlfoundation.com/scholarship-programme/"
    },
    
    # === TIER 3: MARA/Bumi ===
    {
        "name": "MARA Young Talent (YTP)",
        "provider": "MARA",
        "tags": ["土著限定", "B40优先"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 6.0, "state_req": "All", "muslim_req": False, "bumi_req": True,
        "income_req": "B40", 
        "desc": "通往海外或顶尖私立大学。优先考虑 B40/M40 家庭。",
        "link": "https://www.mara.gov.my/"
    },
    {
        "name": "MARA TESP",
        "provider": "MARA",
        "tags": ["土著限定", "私立大学"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 6.0, "state_req": "All", "muslim_req": False, "bumi_req": True,
        "desc": "资助在国内私立大学 (IPTS) 就读，仅限土著。",
        "link": "https://www.mara.gov.my/"
    },
    {
        "name": "Yayasan Peneraju Profesional",
        "provider": "Peneraju",
        "tags": ["土著限定", "专业认证"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {"Matematik": ["A+", "A", "A-"], "Bahasa Inggeris": ["A+", "A", "A-"]},
        "koko_marks": 6.0, "state_req": "All", "muslim_req": False, "bumi_req": True,
        "field_only": "会计/金融 (ACCA/CFA/Accounting)",
        "desc": "专业认证快速通道，仅限土著。",
        "link": "https://yayasanpeneraju.com.my/"
    },

    # === TIER 4: State (All States) ===
    {
        "name": "Yayasan Selangor (Pinjaman)",
        "provider": "Yayasan Selangor",
        "tags": ["雪兰莪子民"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 0, "state_req": "Selangor", "muslim_req": False, "bumi_req": False,
        "desc": "免息贷学金。成绩优异 (CGPA 3.75+) 可豁免还款。",
        "link": "https://yayasanselangor.org.my/"
    },
    {
        "name": "Yayasan Sarawak Tun Taib",
        "provider": "Yayasan Sarawak",
        "tags": ["砂拉越子民", "STEM"],
        "min_A_total": 6, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {"Bahasa Melayu": ["A+", "A", "A-", "B+", "B", "C"]},
        "koko_marks": 0, "state_req": "Sarawak", "muslim_req": False, "bumi_req": False,
        "desc": "砂拉越顶级奖学金，优先 STEM。含混合型贷学金。",
        "link": "https://yayasansarawak.org.my/"
    },
    {
        "name": "Biasiswa Kerajaan Negeri Sabah",
        "provider": "Kerajaan Sabah",
        "tags": ["沙巴子民"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 6.0, "state_req": "Sabah", "muslim_req": False, "bumi_req": False,
        "desc": "沙巴州卓越奖学金 (BKNS)。",
        "link": "https://biasiswa.sabah.gov.my/"
    },
    {
        "name": "YPJ Biasiswa/Pinjaman",
        "provider": "YPJ",
        "tags": ["柔佛子民"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 5.0, "state_req": "Johor", "muslim_req": False, "bumi_req": False,
        "desc": "柔佛州资助。视成绩决定是奖学金还是贷学金。",
        "link": "http://ypj.gov.my/"
    },
    {
        "name": "Yayasan Terengganu (Biasiswa)",
        "provider": "Yayasan Terengganu",
        "tags": ["登嘉楼子民", "精英"],
        "min_A_total": 8, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {"Bahasa Melayu": ["A+", "A", "A-"], "Bahasa Inggeris": ["A+", "A", "A-"]},
        "koko_marks": 7.0, "state_req": "Terengganu", "muslim_req": False, "bumi_req": False,
        "desc": "登嘉楼州精英奖学金。要求父母必须是登嘉楼人。",
        "link": "http://yt.gov.my/"
    },
    {
        "name": "Yayasan Pahang (Skim Pelajar Cemerlang)",
        "provider": "Yayasan Pahang",
        "tags": ["彭亨子民"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 6.0, "state_req": "Pahang", "muslim_req": False, "bumi_req": False,
        "desc": "彭亨州提供的教育资助，涵盖奖学金与贷学金。",
        "link": "https://www.yp.org.my/"
    },
    {
        "name": "Yayasan Perak (Insentif)",
        "provider": "Yayasan Perak",
        "tags": ["霹雳子民", "一次性"],
        "min_A_total": 3, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 0, "state_req": "Perak", "muslim_req": False, "bumi_req": False,
        "income_req": "B40",
        "desc": "获得大学录取即送 RM500-RM1000 援助金。B40家庭优先。",
        "link": "https://yayasanperak.gov.my/"
    },
    {
        "name": "Yayasan Negeri Sembilan",
        "provider": "Yayasan NS",
        "tags": ["森美兰子民"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 0, "state_req": "Negeri Sembilan", "muslim_req": False, "bumi_req": False,
        "desc": "森美兰州提供的教育资助。",
        "link": "https://yns.gov.my/"
    },
    {
        "name": "Yayasan Melaka (TAPEM)",
        "provider": "TAPEM",
        "tags": ["马六甲子民"],
        "min_A_total": 4, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 0, "state_req": "Melaka", "muslim_req": False, "bumi_req": False,
        "desc": "马六甲教育信托基金 (TAPEM) 提供的贷学金。",
        "link": "https://tapem.melaka.gov.my/"
    },
    {
        "name": "Yayasan Kelantan (YAKIN)",
        "provider": "YAKIN",
        "tags": ["吉兰丹子民"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 0, "state_req": "Kelantan", "muslim_req": False, "bumi_req": False,
        "desc": "吉兰丹基金局提供的教育援助。",
        "link": "http://www.yakin.kelantan.gov.my/"
    },
    
    # === TIER 5: Private/Vocational/Other ===
    {
        "name": "Sin Chew Education Fund",
        "provider": "Sin Chew",
        "tags": ["私立大学", "全额学费"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 6.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "星洲日报教育基金，提供各私立大学全额学费奖学金。",
        "link": "https://scedufund.sinchew.com.my/"
    },
    {
        "name": "Kuok Foundation (Polytechnic)",
        "provider": "Kuok Foundation",
        "tags": ["家境清寒", "Politeknik"],
        "min_A_total": 4, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 5.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "income_req": "B40",
        "desc": "郭鹤年基金会，资助理工学院 (Politeknik) 学生，重视家境。",
        "link": "https://kuokfoundation.com/"
    },
    {
        "name": "KPM PISMP (师范)",
        "provider": "KPM",
        "tags": ["师范", "公务员"],
        "min_A_total": 5, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {"Bahasa Melayu": ["A+", "A", "A-"], "Sejarah": ["A+", "A", "A-"]},
        "koko_marks": 7.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_only": "教育/师范 (Education)",
        "desc": "毕业后成为公立教师。需通过 UKCG 心理测试。",
        "link": "https://pismp.moe.gov.my/"
    },
    {
        "name": "JPA Dermasiswa B40 (TVET)",
        "provider": "JPA",
        "tags": ["B40优先", "TVET"],
        "min_A_total": 3, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 4.0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "income_req": "B40",
        "desc": "资助 TVET/Politeknik 课程。B40 家庭优先。",
        "link": "https://esilav2.jpa.gov.my/"
    },
    {
        "name": "PTPK (Pinjaman Latihan Kemahiran)",
        "provider": "PTPK",
        "tags": ["技职教育", "SKM"],
        "min_A_total": 0, "allow_A_minus": True, "min_A_plus": 0,
        "hard_req": {}, "koko_marks": 0, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "desc": "为技职教育 (SKM) 提供贷款与生活津贴，门槛低。",
        "link": "https://www.ptpk.gov.my/"
    }
]

# --- 6. 界面逻辑 ---

st.title("🎓 SPM Scholarship Check + AI Advisor")
st.caption("输入成绩，AI 自动匹配符合资格的马来西亚热门奖学金。")
st.markdown("---")

# === 输入区域 ===
col1, col2 = st.columns(2)
with col1:
    user_state = st.selectbox("🏠 来自州属 (State)", STATE_LIST, index=11)
    koko_score = st.number_input("🏅 Koko 分数 (0-10)", 0.00, 10.00, 8.50, step=0.01)

with col2:
    religion = st.selectbox("🕌 宗教 (Religion)", ["Islam", "Non-Muslim"], index=1)
    is_muslim = True if religion == "Islam" else False
    
    race = st.selectbox("🌏 种族身份 (Status)", ["Bumiputera", "Non-Bumiputera"], index=1)
    is_bumi = True if race == "Bumiputera" else False

# ==========================================
# 🚀 替换开始：防卡顿 + 智能过滤 + 启动同步版
# ==========================================

st.subheader("📚 科目与成绩 (Subjects & Grades)")
st.caption("👇 点击下方 **+** 号添加科目。")

# 1. 初始化 Session State
if 'rows' not in st.session_state:
    st.session_state.rows = [
        {"id": str(uuid.uuid4()), "subject": "Bahasa Melayu", "grade": "A+"},
        {"id": str(uuid.uuid4()), "subject": "Bahasa Inggeris", "grade": "A"},
        {"id": str(uuid.uuid4()), "subject": "Sejarah", "grade": "A-"},
        {"id": str(uuid.uuid4()), "subject": "Matematik", "grade": "A+"},
        {"id": str(uuid.uuid4()), "subject": "Pendidikan Moral", "grade": "A"},
    ]

# 2. 【关键优化】数据同步步：先从界面获取最新值，更新到 rows 列表
#    这步操作替代了 on_change，能极大减少卡顿
for row in st.session_state.rows:
    sub_key = f"sub_{row['id']}"
    grade_key = f"grade_{row['id']}"
    
    # 如果界面上已经有这个控件的值，就同步回 rows 列表
    if sub_key in st.session_state:
        row['subject'] = st.session_state[sub_key]
    if grade_key in st.session_state:
        row['grade'] = st.session_state[grade_key]

# 3. 计算“已被选过”的科目 (用于过滤)
all_selected_subjects = [r['subject'] for r in st.session_state.rows if r['subject'] != "-- 请选择 --"]

# 4. 标题栏
h1, h2, h3, h4 = st.columns([0.5, 3, 1.5, 0.5])
with h1: st.markdown("**#**")
with h2: st.markdown("**科目 (Subject)**")
with h3: st.markdown("**等级 (Grade)**")
with h4: st.markdown("")

rows_to_delete = []
GRADE_OPTIONS = ["-- 请选择 --", "A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]

# 5. 渲染每一行
for i, row in enumerate(st.session_state.rows):
    c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 0.5])
    
    with c1: 
        st.write(f"{i + 1}") 
    
    with c2:
        # --- 智能过滤逻辑 ---
        # 逻辑：完整列表 - 别人选过的 + 我自己当前选的
        # 这样下拉菜单里就只有“剩下的”和“我自己当前选的”
        available_subjects = [
            s for s in SUBJECT_LIST 
            if s not in all_selected_subjects or s == row['subject']
        ]
        final_options = ["-- 请选择 --"] + available_subjects
        
        # 确保当前选的值在选项列表里 (防止报错)
        current_index = 0
        if row['subject'] in final_options:
            current_index = final_options.index(row['subject'])
        
        # 渲染下拉框 (注意：没有 on_change 了)
        st.selectbox(
            "Subject", 
            options=final_options,
            index=current_index,
            key=f"sub_{row['id']}", # key 必须对应上面的同步逻辑
            label_visibility="collapsed"
        )

    with c3:
        current_grade_index = 0
        if row['grade'] in GRADE_OPTIONS:
            current_grade_index = GRADE_OPTIONS.index(row['grade'])
            
        st.selectbox(
            "Grade", 
            options=GRADE_OPTIONS, 
            index=current_grade_index,
            key=f"grade_{row['id']}",
            label_visibility="collapsed"
        )
        
    with c4:
        if st.button("🗑️", key=f"del_{row['id']}"):
            rows_to_delete.append(i)

# 6. 处理删除
if rows_to_delete:
    for index in sorted(rows_to_delete, reverse=True):
        del st.session_state.rows[index]
    st.rerun()

# 7. 添加按钮
if st.button("➕ 添加科目 (Add Subject)"):
    st.session_state.rows.append({"id": str(uuid.uuid4()), "subject": "-- 请选择 --", "grade": "-- 请选择 --"})
    st.rerun()

# ==========================================
# 🚀 替换结束
# ==========================================

# === 侧边栏 ===
with st.sidebar:
    st.markdown("### 🌟 关于这个 App")
    st.info("输入成绩，即刻匹配 JPA, Petronas 及各州 Yayasan 奖学金")
    st.markdown("---")
    st.markdown("### ☕ 请开发者喝杯咖啡")
    st.write("服务器和维护需要成本。如果觉得好用，欢迎打赏支持！")
    
    if os.path.exists("tng.jpeg"):
        st.image("tng.jpeg", caption="Touch 'n Go eWallet", use_container_width=True)
    else:
        # 默默处理，不报错
        pass
        
    st.markdown("---")
    st.markdown("### 💌 帮助学弟学妹")
    st.write("如果你发现某个奖学金的条件变了，或者 App 有问题，请一定要告诉我！你的反馈能帮到明年千千万万的考生。")
    GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScOcxd2Bz5L2aKmVxIWCXtEwGC45T2yTU_W7NVyxawqGe6o4Q/viewform?usp=dialog" 
    st.link_button("📝 点击提交反馈 (Google Form)", GOOGLE_FORM_URL)

# --- Student Input for AI ---
st.markdown("### 🤖 AI 咨询 (Beta)")
student_wish = st.text_input(
    "你想读什么科系？或者对未来有什么迷茫？",
    placeholder="例如：我想读 Computer Science，或者我不确定要选 Matriculation 还是 A-Level..."
)

# --- 分析按钮 ---
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
analyze_btn = st.button("🚀 立即分析 (Analyze)", type="primary", use_container_width=True)
st.markdown("<div id='result_anchor'></div>", unsafe_allow_html=True)

if analyze_btn:
    components.html("""<script>window.parent.document.getElementById('result_anchor').scrollIntoView({behavior: 'smooth'});</script>""", height=0)
    st.markdown("### 📊 分析结果")
    
    # 1. 统计成绩 & 清洗数据
    user_grades = {}
    count_A_plus = 0; count_A_strict = 0; count_A_loose = 0
    
    # 第一次遍历：存入字典 (去除重复科目)
    for row in st.session_state.rows:
        sub = row['subject']; grade = row['grade']
        if sub == "-- 请选择 --" or grade == "-- 请选择 --": continue
        if sub: user_grades[sub] = grade
        
    # 第二次遍历：根据字典统计分数 (确保统计准确)
    for sub, grade in user_grades.items():
        if grade == "A+": count_A_plus+=1; count_A_strict+=1; count_A_loose+=1
        elif grade == "A": count_A_strict+=1; count_A_loose+=1
        elif grade == "A-": count_A_loose+=1
    
    # 2. 构建 AI Prompt
    prompt_grades_str = ""
    for sub, grade in user_grades.items():
        prompt_grades_str += f"- {sub}: {grade}\n"

    # === 👇 新增：给 AI 的“入学标准小抄” (Knowledge Base)，防止幻觉 ===
    general_requirements = """
    Reference Guidelines for Malaysia Pathways (Use this to advise):
    1. JPA/Petronas/Top Scholarships: strictly requires A+/A grades.
    2. Matrikulasi (Science): Generally requires decent results (mix of A and B). If a student has mostly C/D, do NOT recommend Matrikulasi Science lightly.
    3. Asasi (Public Uni Foundation): Highly competitive, usually needs multiple As.
    4. STPM (Form 6): The most accessible route. Open to almost anyone with credits (C) in BM and Sejarah. Best for students with average results (B/C) who want a second chance.
    5. Diploma (UPU/Polytechnic): Good for students with B/C/D grades. Focus on skills.
    6. IPTS (Private): Entry is flexible (usually 3-5 Credits), but requires money/loans (PTPTN).
    """

    ai_prompt = f"""
    Student Profile:
    - State: {user_state}
    - Religion/Race Status: {religion}, {race}
    - Koko Score: {koko_score}/10
    
    SPM Results:
    {prompt_grades_str}
    Summary: {count_A_plus} A+, {count_A_strict} A (A+/A), {count_A_loose} A (including A-).
    
    Student's Wish/Question: "{student_wish}"
    
    Eligible Scholarships (based on hard requirements):
    """
    
    eligible_count = 0
    
    # 3. 奖学金匹配循环
    for sch in SCHOLARSHIP_DB:
        is_pass = True
        
        # --- 匹配逻辑 ---
        if sch['state_req'] != "All" and sch['state_req'] != user_state: continue 
        if sch.get('muslim_req') and not is_muslim: continue
        if sch.get('bumi_req') and not is_bumi: continue

        # 成绩判定
        if sch['name'].startswith("JPA JKPJ"):
            science_pass = True
            for sub in ["Matematik", "Matematik Tambahan", "Fizik"]:
                if user_grades.get(sub) not in ["A+", "A"]: science_pass = False
            if not science_pass: is_pass = False
            if count_A_loose < sch['min_A_total']: is_pass = False
        else:
            user_A_count = count_A_loose if sch['allow_A_minus'] else count_A_strict
            if user_A_count < sch['min_A_total']: is_pass = False
            for req_sub, req_grades in sch['hard_req'].items():
                if user_grades.get(req_sub) not in req_grades: is_pass = False

        if sch['min_A_plus'] > 0 and count_A_plus < sch['min_A_plus']: is_pass = False
        
        # 🌟 修复：PNN 专用逻辑，如果开启 must_all_A_minus，则所有科目不得低于 A-
        if sch.get("must_all_A_minus") and any(g not in ["A+", "A", "A-"] for g in user_grades.values()):
            is_pass = False
            
        if koko_score < sch['koko_marks']: is_pass = False

        # --- 匹配成功，显示卡片 ---
        if is_pass:
            eligible_count += 1
            ai_prompt += f"- {sch['name']}\n"
            
            tags_html = "".join([f"<span class='tag'>{t}</span>" for t in sch['tags']])
            info_html = ""
            if "field_only" in sch:
                info_html += f"<div class='info-text'><span class='field-tag'>🎯 指定科系:</span> {sch['field_only']}</div>"
            if "field_block" in sch:
                info_html += f"<div class='info-text'><span class='block-tag'>⛔ 不含科系:</span> {sch['field_block']}</div>"
            if sch.get("income_req") == "B40":
                info_html += f"<div class='info-text'><span class='b40-tag'>💡 B40 群体优先</span></div>"

            st.markdown(f"""
            <div class="scholarship-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:#1F2937;">{sch['name']}</h3>
                    <span class="status-pass">✅ 符合资格</span>
                </div>
                <p style="color:#6B7280; font-size:14px; margin-top:5px;">{sch['provider']}</p>
                <div style="margin: 10px 0;">{tags_html}</div>
                <p>{sch['desc']}</p>
                {info_html}
            </div>
            """, unsafe_allow_html=True)
            
            if "link" in sch:
                st.link_button("🔗 官网核实 (Verify)", sch['link'])
            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
    if eligible_count == 0:
        st.warning("根据硬性指标，暂无完全匹配的奖学金。")
        ai_prompt += "None. The student did not qualify for any scholarships in the database.\n"
    
    # 补充 AI Prompt 指令
    ai_prompt += f"""
    \n[IMPORTANT REFERENCE DATA]
    {general_requirements}
    
    Based on the Student Profile, SPM Results, and the [IMPORTANT REFERENCE DATA] above:
    1. If scholarships are listed, recommend the best fit.
    2. If NO scholarships are listed, suggest realistic alternatives (STPM, Matrikulasi, Diploma) based on their specific grades. 
    3. BE REALISTIC. If grades are mostly B/C, recommend STPM or Diploma, NOT Asasi/Matrikulasi Science.
    4. Keep the advice encouraging but honest.
    5. CRITICAL RULE: Reply primarily in CHINESE (Malaysian Mandarin).
    """

    # --- 4. DeepSeek AI 分析 ---
    st.markdown("### 🤖 DeepSeek AI 升学建议")
    
    if student_wish:
        with st.spinner("DeepSeek 正在思考你的未来..."):
            advice = AskDeepSeek(ai_prompt)
            st.markdown(f"""
            <div class="ai-box">
                <h4>💡 AI 的建议：</h4>
                <p>{advice}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 👇 新增：免责声明
            st.caption("⚠️ 免责声明：AI 建议仅供参考，入学标准每年可能会更改。请务必以 UPU/Matrikulasi 官方最新公告为准。")
    else:
        st.info("在上方输入你的升学愿望，AI 才能给你更准确的建议哦！")