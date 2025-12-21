import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import uuid
import os

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="SPM Scholarship Check",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# --- 2. CSS 美化 (UI 终极视觉增强版) ---
st.markdown("""
<style>
    /* === 侧边栏收起时的样式 === */
    [data-testid="stSidebarCollapsedControl"] {
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        width: 32px !important;
        height: 100vh !important;
        background-color: #FFFDF5 !important;
        border-right: 2px solid #FDE68A !important;
        z-index: 100000 !important;
        display: flex !important;
        align-items: flex-start !important;
        justify-content: center !important;
        padding-top: 20px !important;
        transition: background-color 0.3s;
    }
    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #FEF3C7 !important;
        cursor: pointer;
    }
    [data-testid="stSidebarCollapsedControl"] svg {
        color: #D97706 !important;
        fill: #D97706 !important;
        width: 20px !important;
        height: 20px !important;
        stroke-width: 3px !important;
    }

    /* === 侧边栏展开时的样式 === */
    section[data-testid="stSidebar"] {
        width: 450px !important;
        background-color: #FFFDF5; 
        border-right: 1px solid #F3E8D3;
    }

    /* === 基础样式 === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .st-emotion-cache-1plm3a3 a {display: none !important;} 
    h1 a, h2 a, h3 a {display: none !important;}
    .block-container {padding-top: 2rem; padding-bottom: 5rem;}
    
    button[data-testid="stNumberInputStepDown"] { display: none !important; }
    button[data-testid="stNumberInputStepUp"] { display: none !important; }
    
    /* 结果卡片 */
    .scholarship-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 6px solid #10B981; 
        animation: fadeIn 0.8s;
        transition: transform 0.2s;
    }
    .scholarship-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }
    
    .tag {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0284C7;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 12px;
        margin-right: 5px;
        font-weight: 600;
    }
    
    .info-text {
        font-size: 13px;
        color: #4B5563;
        margin-top: 8px;
        line-height: 1.5;
    }
    .field-tag { color: #D97706; font-weight: bold; } 
    .block-tag { color: #DC2626; font-weight: bold; } 
    .b40-tag { color: #059669; font-weight: bold; }   

    div[data-testid="column"] button {
        border-color: #FECACA;
        color: #DC2626;
        border-radius: 50%;
        width: 35px;
        height: 35px;
    }
    div[data-testid="column"] button:hover {
        background-color: #FEF2F2;
        border-color: #EF4444;
    }
    
    .stSelectbox { margin-bottom: 0px; }
    
    .feedback-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #F3F4F6;
        color: #374151;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        border: 1px solid #D1D5DB;
        transition: all 0.2s;
        width: 100%;
        margin-top: 10px;
    }
    .feedback-btn:hover {
        background-color: #E5E7EB;
        border-color: #9CA3AF;
        color: #111827;
    }
    
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 45px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 基础数据 ---

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

# --- 4. 终极全集奖学金数据库 ---
SCHOLARSHIP_DB = [
    # === TIER 1: JPA 家族 ===
    {
        "name": "JPA Program Penajaan Nasional (PPN)",
        "provider": "JPA",
        "tags": ["全球 Top 10", "全额资助"],
        "min_A_total": 9, "allow_A_minus": False, "min_A_plus": 9,       
        "hard_req": {"Bahasa Melayu": ["A+", "A"], "Sejarah": ["A+", "A"]},
        "koko_marks": 8.5, "state_req": "All", "muslim_req": False, "bumi_req": False,
        "field_block": "医学/牙医/药剂 (Medicine/Dentistry/Pharmacy)", 
        "desc": "JPA 最顶级的奖学金，全额资助前往全球 Top 10 大学 (UK/US)。需通过面试。",
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

# --- 4. 界面逻辑 ---

st.title("🎓 SPM Scholarship Check")
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

st.subheader("📚 科目与成绩 (Subjects & Grades)")
st.caption("👇 点击下方 **+** 号添加科目。")

# === 动态列表逻辑 (回调版) ===
if 'rows' not in st.session_state:
    st.session_state.rows = [
        {"id": str(uuid.uuid4()), "subject": "Bahasa Melayu", "grade": "A+"},
        {"id": str(uuid.uuid4()), "subject": "Bahasa Inggeris", "grade": "A"},
        {"id": str(uuid.uuid4()), "subject": "Sejarah", "grade": "A-"},
        {"id": str(uuid.uuid4()), "subject": "Matematik", "grade": "A+"},
        {"id": str(uuid.uuid4()), "subject": "Pendidikan Moral", "grade": "A"},
    ]

def update_subject(idx, row_id):
    key = f"sub_{row_id}"
    st.session_state.rows[idx]['subject'] = st.session_state[key]

def update_grade(idx, row_id):
    key = f"grade_{row_id}"
    st.session_state.rows[idx]['grade'] = st.session_state[key]

rows_to_delete = []
all_selected_subjects = [row['subject'] for row in st.session_state.rows if row['subject'] != "-- 请选择 --"]

h1, h2, h3, h4 = st.columns([0.5, 3, 1.5, 0.5])
with h1: st.markdown("**#**")
with h2: st.markdown("**科目 (Subject)**")
with h3: st.markdown("**等级 (Grade)**")
with h4: st.markdown("")

FULL_SUBJECT_OPTIONS = ["-- 请选择 --"] + SUBJECT_LIST
GRADE_OPTIONS = ["-- 请选择 --", "A+", "A", "A-", "B+", "B", "C+", "C", "D", "E", "G"]

for i, row in enumerate(st.session_state.rows):
    c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 0.5])
    with c1: st.write(f"{i + 1}") 
    with c2:
        available_subjects = [sub for sub in SUBJECT_LIST if sub not in all_selected_subjects or sub == row['subject']]
        final_options = ["-- 请选择 --"] + available_subjects
        curr_sub = row["subject"]
        sub_idx = final_options.index(curr_sub) if curr_sub in final_options else 0
        st.selectbox("Sub", final_options, index=sub_idx, key=f"sub_{row['id']}", label_visibility="collapsed", on_change=update_subject, args=(i, row['id']))
    with c3:
        curr_grade = row["grade"]
        grade_idx = GRADE_OPTIONS.index(curr_grade) if curr_grade in GRADE_OPTIONS else 0
        st.selectbox("Grd", GRADE_OPTIONS, index=grade_idx, key=f"grade_{row['id']}", label_visibility="collapsed", on_change=update_grade, args=(i, row['id']))
    with c4:
        if st.button("🗑️", key=f"del_{row['id']}"): rows_to_delete.append(i)

if rows_to_delete:
    for index in sorted(rows_to_delete, reverse=True): del st.session_state.rows[index]
    st.rerun()

if st.button("➕ 添加科目 (Add Subject)"):
    st.session_state.rows.append({"id": str(uuid.uuid4()), "subject": "-- 请选择 --", "grade": "-- 请选择 --"})
    st.rerun()

# === 侧边栏 (TNG 支持 & 反馈) ===
with st.sidebar:
    st.markdown("### 🌟 关于这个 App")
    st.info("输入成绩，即刻匹配 JPA, Petronas 及各州 Yayasan 奖学金。")
    st.markdown("---")
    st.markdown("### ☕ 请开发者喝杯咖啡")
    st.write("服务器和维护需要成本。如果觉得好用，欢迎打赏支持！")
    
    if os.path.exists("tng.jpeg"):
        st.image("tng.jpeg", caption="Touch 'n Go eWallet", use_container_width=True)
    else:
        st.warning("请确保 'tng.jpeg' 文件在代码目录下。")
    
    st.markdown("---")
    # 暖心的反馈文案
    st.markdown("### 💌 帮助学弟学妹")
    st.write("如果你发现某个奖学金的条件变了，或者 App 有问题，请一定要告诉我！你的反馈能帮到明年千千万万的考生。")
    
    GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScOcxd2Bz5L2aKmVxIWCXtEwGC45T2yTU_W7NVyxawqGe6o4Q/viewform?usp=dialog" 
    # 使用 st.link_button 替代 raw HTML，避免代码乱码
    st.link_button("📝 点击提交反馈 (Google Form)", GOOGLE_FORM_URL)

# --- 分析按钮 ---
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
analyze_btn = st.button("🚀 立即分析 (Analyze)", type="primary", use_container_width=True)
st.markdown("<div id='result_anchor'></div>", unsafe_allow_html=True)

if analyze_btn:
    components.html("""<script>window.parent.document.getElementById('result_anchor').scrollIntoView({behavior: 'smooth'});</script>""", height=0)
    st.markdown("### 📊 分析结果")
    
    # 统计
    user_grades = {}
    count_A_plus = 0; count_A_strict = 0; count_A_loose = 0
    for row in st.session_state.rows:
        sub = row['subject']; grade = row['grade']
        if sub == "-- 请选择 --" or grade == "-- 请选择 --": continue
        if sub: user_grades[sub] = grade
        if grade == "A+": count_A_plus+=1; count_A_strict+=1; count_A_loose+=1
        elif grade == "A": count_A_strict+=1; count_A_loose+=1
        elif grade == "A-": count_A_loose+=1
            
    eligible_count = 0
    
    for sch in SCHOLARSHIP_DB:
        is_pass = True
        
        # 1. 基础门槛
        if sch['state_req'] != "All" and sch['state_req'] != user_state: continue 
        if sch.get('muslim_req') and not is_muslim: continue
        if sch.get('bumi_req') and not is_bumi: continue

        # 2. 成绩判定
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
        if koko_score < sch['koko_marks']: is_pass = False

        if is_pass:
            eligible_count += 1
            tags_html = "".join([f"<span class='tag'>{t}</span>" for t in sch['tags']])
            
            # 动态生成提示信息
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
        st.warning("无符合标准的奖学金。")