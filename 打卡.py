import calendar
from datetime import date, datetime, timedelta
import json
import os
import time
import streamlit as st

# 页面配置
st.set_page_config(
    page_title="🌟 がんばりスタンプカード 🌟", page_icon="🧸", layout="centered"
)

# 注入 CSS 样式：包含缩小版的标题栏与连续打卡特殊按钮样式
st.markdown(
    """
    <style>
    .stApp { background-color: #FFF0F5; }
    
    /* 🌟 缩小版顶部标题卡片（约原先的 2/3 大小） */
    .score-card {
        background: linear-gradient(135deg, #FFB6C1 0%, #FF69B4 100%);
        padding: 12px 18px;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(255, 105, 180, 0.2);
        margin-bottom: 15px;
    }
    .score-card h2 {
        color: white !important;
        margin: 0 !important;
        font-size: 1.4em !important;
    }
    .score-card p {
        margin: 3px 0 0 0 !important;
        opacity: 0.95;
        font-size: 0.85em !important;
    }
    
    .streak-badge {
        background-color: #FFF0F5;
        color: #FF1493;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 0.8em;
        border: 1px solid #FFB6C1;
    }
    .ticket-card {
        background-color: #FFFFF0;
        border: 2px dashed #FF8C00;
        padding: 10px 14px;
        border-radius: 14px;
        margin-bottom: 8px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.03);
    }
    
    /* 迷你日历容器 */
    .mini-calendar-container {
        max-width: 360px;
        margin: 0 auto;
        padding: 10px;
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0px 4px 12px rgba(255, 182, 193, 0.3);
        border: 2px solid #FFE4E1;
    }
    .cal-header-day {
        text-align: center;
        font-weight: bold;
        color: #FF69B4;
        font-size: 0.75em;
        margin-bottom: 6px;
    }
    .cal-day-box {
        border-radius: 10px;
        padding: 3px 1px;
        text-align: center;
        margin: 1.5px;
        font-weight: bold;
        font-size: 0.75em;
        line-height: 1.1;
        transition: transform 0.2s;
    }
    .cal-day-box:hover {
        transform: scale(1.1);
    }
    .cal-full { 
        background-color: #E8F5E9; 
        color: #2E7D32; 
        border: 1.5px solid #A5D6A7; 
        box-shadow: 0px 2px 4px rgba(76, 175, 80, 0.15);
    }
    .cal-part { 
        background-color: #FFF3E0; 
        color: #EF6C00; 
        border: 1.5px solid #FFCC80; 
        box-shadow: 0px 2px 4px rgba(255, 152, 0, 0.15);
    }
    .cal-empty { 
        background-color: #FAFAFA; 
        color: #D3D3D3; 
        border: 1px dashed #E0E0E0; 
    }
    .cal-none { background-color: transparent; }

    div.stExpander {
        background-color: #FFFFFF;
        border-radius: 16px !important;
        border: 1px solid #FFE4E1 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "tracker_data.json"
DEFAULT_TITLE = "🐭 らきちゃんの頑張りスタンプカード 🐭"

DEFAULT_TASKS = [
    {"id": "reading", "name": "📖 読書 20分", "yt_mins": 5},
    {"id": "math", "name": "✍️ 算数の宿題", "yt_mins": 10},
    {"id": "english", "name": "🗣️ 英語の練習 15分", "yt_mins": 5},
    {"id": "desk", "name": "🧹 机の片付け", "yt_mins": 3},
]

DEFAULT_SHOP = [
    {"id": "shop_1", "name": "🍦 アイスクリームを食べる", "cost": 5},
    {"id": "shop_2", "name": "🎮 ゲーム 30分許可", "cost": 10},
    {"id": "shop_3", "name": "🧸 小さいおもちゃを買う", "cost": 20},
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "app_title" not in data:
                    data["app_title"] = DEFAULT_TITLE
                if "tasks" not in data:
                    data["tasks"] = DEFAULT_TASKS
                if "shop" not in data:
                    data["shop"] = DEFAULT_SHOP
                if "youtube_mins" not in data:
                    data["youtube_mins"] = 0
                if "wallet" not in data:
                    data["wallet"] = []
                for task in data["tasks"]:
                    if "yt_mins" not in task:
                        task["yt_mins"] = 5
                return data
        except Exception:
            pass
    return {
        "app_title": DEFAULT_TITLE,
        "flowers": 0,
        "youtube_mins": 0,
        "records": {},
        "streaks": {},
        "tasks": DEFAULT_TASKS,
        "shop": DEFAULT_SHOP,
        "wallet": [],
    }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# 1. 顶部成就看板（缩小至 2/3，前后带小老鼠 🐭 图标）
current_title = data.get("app_title", DEFAULT_TITLE)

# 如果原标题还带着气球 🎈，自动替换为小老鼠 🐭
if "🎈" in current_title:
    current_title = current_title.replace("🎈", "🐭")

st.markdown(
    f"""
    <div class="score-card">
        <h2>{current_title}</h2>
        <p>まいにち コツコツ がんばって、すてきなごほうびを ゲットしよう！✨</p>
    </div>
""",
    unsafe_allow_html=True,
)

col_score1, col_score2 = st.columns(2)
with col_score1:
    st.metric(label="🌸 お花（ポイント）", value=f"{data['flowers']} 枚")
with col_score2:
    st.metric(label="📺 YouTube 視聴可能時間", value=f"{data['youtube_mins']} 分")

st.markdown("---")

# 2. 单日打卡与日期选择
selected_date = st.date_input("📅 詳細チェックの日付を選択", value=date.today())
date_str = selected_date.strftime("%Y-%m-%d")
today_records = data["records"].get(date_str, [])

st.subheader(f"📝 {date_str} のチェックイン")

# 3. 任务打卡列表（带 5 天连续打卡特别奖励按钮）
for task in data["tasks"]:
    t_name = task["name"]
    t_id = task["id"]
    t_yt = task.get("yt_mins", 5)
    is_done = t_name in today_records
    current_streak = data["streaks"].get(t_id, 0)

    col_t1, col_t2, col_t3 = st.columns([2.0, 1.0, 1.1])

    with col_t1:
        st.markdown(
            f"**{t_name}** <br><span class='streak-badge'>🔥 {current_streak}日連続</span>",
            unsafe_allow_html=True,
        )

    if is_done:
        col_t2.button("✅ 完了", key=f"done_{t_id}_{date_str}", disabled=True)
    else:
        if col_t2.button("+1 🌸", key=f"f_{t_id}_{date_str}"):
            if date_str not in data["records"]:
                data["records"][date_str] = []
            data["records"][date_str].append(t_name)
            data["flowers"] += 1

            yesterday_str = (selected_date - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            yesterday_records = data["records"].get(yesterday_str, [])
            new_streak = (
                current_streak + 1
                if (t_name in yesterday_records or current_streak == 0)
                else 1
            )
            data["streaks"][t_id] = new_streak

            save_data(data)
            st.toast(
                f"素晴らしい！【{t_name}】をクリア！ 🌸 お花を 1枚 ゲット！"
            )
            st.rerun()

        if col_t3.button(f"+{t_yt}分 📺", key=f"yt_{t_id}_{date_str}"):
            if date_str not in data["records"]:
                data["records"][date_str] = []
            data["records"][date_str].append(t_name)
            data["youtube_mins"] += t_yt

            yesterday_str = (selected_date - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            yesterday_records = data["records"].get(yesterday_str, [])
            new_streak = (
                current_streak + 1
                if (t_name in yesterday_records or current_streak == 0)
                else 1
            )
            data["streaks"][t_id] = new_streak

            save_data(data)
            st.toast(
                f"やったね！【{t_name}】をクリア！ 📺 YouTube {t_yt}分 ゲット！"
            )
            st.rerun()

    # 🌟 新功能：连续打卡达到 5 天或以上时，展示领奖按钮
    if current_streak >= 5:
        b_col1, b_col2 = st.columns([2.0, 2.1])
        with b_col2:
            if st.button(
                f"🎁 5日連続特別ご褒美！（+2 🌸）",
                key=f"streak_bonus_{t_id}_{date_str}",
            ):
                data["flowers"] += 2
                # 领取后重置或扣减 5 天计数，开始下一轮5天挑战
                data["streaks"][t_id] = current_streak - 5
                save_data(data)
                st.balloons()
                st.success(
                    f"🎉 5日連続達成おめでとう！特別ボーナスとしてお花を 2枚 プレゼント！"
                )
                st.rerun()

st.markdown("---")

# 4. 🌟 已调整位置：电子钱包（マイ財布）放置于 チェックイン 的下面
with st.expander("👛 マイ財布（手に入れたチケット）", expanded=True):
    wallet = data.get("wallet", [])
    if not wallet:
        st.info(
            "まだチケットはありません。お花をためて「ご褒美交換所」でチケットに交換しよう！"
        )
    else:
        st.write("##### 🎟️ 所持中のご褒美チケット")
        for idx, ticket in enumerate(wallet):
            t_col1, t_col2 = st.columns([3, 1])
            with t_col1:
                st.markdown(
                    f"""
                    <div class="ticket-card">
                        <b>🎁 {ticket['name']}</b><br>
                        <small style='color: #888;'>交換日: {ticket['date']}</small>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            with t_col2:
                if st.button("使う！", key=f"use_ticket_{idx}"):
                    used_ticket = data["wallet"].pop(idx)
                    save_data(data)
                    st.balloons()
                    st.success(
                        f"🎉 【{used_ticket['name']}】を使用しました！保護者に見せてご褒美を受け取ってね！"
                    )
                    st.rerun()

st.markdown("---")

# 5. 积分兑换商城
st.subheader("🎁 ご褒美交換所")
for idx, item in enumerate(data["shop"]):
    sc1, sc2 = st.columns([3, 1])
    sc1.write(f"**{item['name']}** （必要なお花: 🌸 **{item['cost']}** 枚）")

    can_afford = data["flowers"] >= item["cost"]

    if sc2.button(
        "交換する", key=f"buy_btn_{idx}", disabled=not can_afford
    ):
        data["flowers"] -= item["cost"]
        new_ticket = {
            "name": item["name"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        data["wallet"].append(new_ticket)

        save_data(data)
        st.balloons()
        st.success(
            f"🎉 【{item['name']}】のチケットに交換しました！『マイ財布』を確認してね！"
        )
        st.rerun()

st.markdown("---")

# 6. 精小全景日历（位置：ご褒美交換所的下方）
with st.expander("🗓️ 今月のカレンダー（全体チェック状況）", expanded=True):
    today = date.today()

    c_col1, c_col2, c_col3 = st.columns([1, 2, 1])
    with c_col2:
        y_col, m_col = st.columns(2)
        with y_col:
            year = st.number_input(
                "年", min_value=2024, max_value=2030, value=today.year
            )
        with m_col:
            month = st.number_input(
                "月", min_value=1, max_value=12, value=today.month
            )

    cal = calendar.monthcalendar(year, month)
    total_tasks_count = len(data["tasks"])

    st.markdown('<div class="mini-calendar-container">', unsafe_allow_html=True)

    headers = ["月🌙", "火🔥", "水💧", "木🌲", "金✨", "土🎈", "日☀️"]
    h_cols = st.columns(7)
    for i, h in enumerate(headers):
        h_cols[i].markdown(
            f"<div class='cal-header-day'>{h}</div>", unsafe_allow_html=True
        )

    for week in cal:
        w_cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                w_cols[i].markdown(
                    "<div class='cal-day-box cal-none'></div>",
                    unsafe_allow_html=True,
                )
            else:
                d_str = f"{year:04d}-{month:02d}-{day:02d}"
                day_records = data["records"].get(d_str, [])
                done_count = len(day_records)

                if done_count >= total_tasks_count and total_tasks_count > 0:
                    css_class = "cal-full"
                    icon = "🌟"
                elif done_count > 0:
                    css_class = "cal-part"
                    icon = "🌸"
                else:
                    css_class = "cal-empty"
                    icon = "·"

                w_cols[i].markdown(
                    f"""
                    <div class='cal-day-box {css_class}' title='{d_str}: {done_count}/{total_tasks_count}完了'>
                        {day}<br><span style='font-size:0.95em;'>{icon}</span>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style='font-size:0.8em; color:#888; margin-top:12px; text-align:center;'>
            🟩 <b>🌟</b> 全て完了 &nbsp;|&nbsp; 
            🟧 <b>🌸</b> 一部完了 &nbsp;|&nbsp; 
            ⬜ <b>·</b> 未チェック
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# 7. ⚙️ 家长管理区
with st.expander("⚙️ 保護者専用設定（タイトル・タスク・ご褒美・リセット）"):
    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🏷️ タイトル設定",
            "📝 タスク＆個別YouTube設定",
            "🎁 ご褒美ストアの管理",
            "📺 YouTube時間の調整",
            "🔄 履歴リセット",
        ]
    )

    with tab0:
        st.write("##### ページタイトルの変更")
        new_title = st.text_input("新しいタイトルを入力", value=current_title)
        if st.button("タイトルを更新"):
            if new_title.strip():
                data["app_title"] = new_title.strip()
                save_data(data)
                st.success("タイトルを更新しました！")
                st.rerun()
            else:
                st.warning("タイトルを入力してください！")

    with tab1:
        st.write("##### 新しいタスクの追加")
        new_task_name = st.text_input(
            "タスク名", placeholder="例：🧩 パズル 30分"
        )
        new_task_yt = st.number_input(
            "このタスクで得られる YouTube 時間（分）",
            min_value=1,
            value=5,
            step=1,
        )

        if st.button("タスクを追加"):
            if new_task_name:
                new_id = f"custom_{int(time.time())}"
                data["tasks"].append(
                    {
                        "id": new_id,
                        "name": new_task_name,
                        "yt_mins": int(new_task_yt),
                    }
                )
                save_data(data)
                st.success(f"追加しました：{new_task_name}")
                st.rerun()
            else:
                st.warning("タスク名を入力してください！")

        st.write("##### 現在のタスク一覧（個別のYouTube時間設定・削除）")
        for idx, t in enumerate(data["tasks"]):
            del_col1, del_col2 = st.columns([3, 1])
            del_col1.write(
                f"**{t['name']}** （獲得YouTube時間: {t.get('yt_mins', 5)}分）"
            )
            if del_col2.button("削除", key=f"del_task_{idx}"):
                data["tasks"].pop(idx)
                save_data(data)
                st.rerun()

    with tab2:
        st.write("##### 新しいご褒美の追加")
        new_item_name = st.text_input(
            "ご褒美名", placeholder="例：🍿 映画を観に行く"
        )
        new_item_cost = st.number_input(
            "必要なお花の枚数", min_value=1, value=10, step=1
        )
        if st.button("ご褒美を追加"):
            if new_item_name:
                data["shop"].append(
                    {"name": new_item_name, "cost": int(new_item_cost)}
                )
                save_data(data)
                st.success(f"追加しました：{new_item_name}")
                st.rerun()
            else:
                st.warning("ご褒美名を入力してください！")

        st.write("##### 現在のご褒美一覧（削除）")
        for idx, item in enumerate(data["shop"]):
            del_col1, del_col2 = st.columns([3, 1])
            del_col1.write(f"{item['name']}（🌸 {item['cost']}枚）")
            if del_col2.button("削除", key=f"del_item_{idx}"):
                data["shop"].pop(idx)
                save_data(data)
                st.rerun()

    with tab3:
        st.write("##### YouTube 時間の消費・手動調整")
        st.write(f"現在の残り時間: **{data['youtube_mins']} 分**")
        used_mins = st.number_input(
            "調整する分数（減らす場合はマイナスを入力）",
            value=0,
            step=5,
        )
        if st.button("時間を更新"):
            data["youtube_mins"] += int(used_mins)
            if data["youtube_mins"] < 0:
                data["youtube_mins"] = 0
            save_data(data)
            st.success("YouTube 時間を更新しました！")
            st.rerun()

    with tab4:
        st.write("##### 🔄 チェックイン履歴・連続記録のリセット")
        st.warning(
            "⚠️ この操作を行うと、これまでの「チェックイン履歴」と「連続日数」がクリアされます。（タスク内容、所持お花、YouTube時間、チケットは消えません）"
        )
        if st.button("チェックイン履歴をリセットする"):
            data["records"] = {}
            data["streaks"] = {}
            save_data(data)
            st.success("チェックイン履歴と連続記録をリセットしました！")
            st.rerun()