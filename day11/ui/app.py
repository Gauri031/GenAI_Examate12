"""PoshanGuide Streamlit app (Day 10).

  * Chat: asks the PoshanGuide API (POST /ask, or /agent), shows citations,
    and saves thumbs up / thumbs down for every answer.
  * Signature feature - "My plate check": the user lists what they ate today and
    sees a colour bar for each food group against ICMR-NIN's "My Plate for the Day".

Run (backend must already be running):   streamlit run ui/app.py
"""
import os
import uuid

import requests
import streamlit as st

from feedback import feedback_stats, save_feedback
from plate import EXAMPLE_MEAL, compute_plate, foods_help, load_reference, parse_meal

st.set_page_config(page_title="PoshanGuide", page_icon="🥗", layout="wide")

API_URL_DEFAULT = os.getenv("POSHAN_API_URL", "http://127.0.0.1:8000")
AGENT_PAYLOAD_FIELD = "question"  # change if your /agent endpoint expects another field name
CHAT_VIEW, PLATE_VIEW = "💬 Ask PoshanGuide", "🍽️ My plate check"

# ------------------------------------------------------------------ session state
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "view" not in st.session_state:
    st.session_state.view = CHAT_VIEW
if "meal_text" not in st.session_state:
    st.session_state.meal_text = ""


# ------------------------------------------------------------------ backend calls
@st.cache_data(ttl=5)
def backend_ok(api_url: str) -> bool:
    try:
        return requests.get(f"{api_url}/health", timeout=2).status_code == 200
    except requests.RequestException:
        return False


def _citations(data: dict) -> list[dict]:
    raw = data.get("citations") or data.get("sources") or []
    out = []
    for i, c in enumerate(raw, 1):
        if isinstance(c, dict):
            out.append({"id": c.get("id", i), "source": c.get("source", ""), "page": c.get("page", ""),
                        "title": c.get("title", ""), "score": c.get("score"), "snippet": c.get("snippet", "")})
        else:
            out.append({"id": i, "source": str(c), "page": "", "title": "", "score": None, "snippet": ""})
    return out


def ask_backend(api_url: str, endpoint: str, question: str, top_k: int) -> dict:
    """Call POST /ask (or /agent). Returns answer, answerable, citations."""
    payload = {"question": question, "top_k": top_k} if endpoint == "/ask" else {AGENT_PAYLOAD_FIELD: question}
    try:
        resp = requests.post(f"{api_url}{endpoint}", json=payload, timeout=90)
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach the PoshanGuide API at {api_url}. Is the backend running? ({exc})")
    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(f"API error {resp.status_code}: {str(detail)[:300]}")
    data = resp.json()
    answer = (data.get("answer") or data.get("response") or data.get("final_answer") or data.get("output") or "").strip()
    answerable = data.get("answerable")
    if answerable is None:
        answerable = bool(answer) and not answer.lower().startswith(("i don't know", "i do not know"))
    return {"answer": answer or "(empty answer)", "answerable": bool(answerable), "citations": _citations(data)}


# ------------------------------------------------------------------ callbacks
def rate(index: int, rating: str) -> None:
    """Save a thumbs up / down for one assistant message."""
    msg = st.session_state.messages[index]
    msg["rating"] = rating
    save_feedback({
        "session_id": st.session_state.session_id, "message_id": msg["id"], "rating": rating,
        "question": msg.get("question", ""), "answer": msg["content"], "answerable": msg.get("answerable"),
        "endpoint": msg.get("endpoint"), "citations": [f"{c['source']} p{c['page']}" for c in msg.get("citations", [])],
    })


def ask_about(question: str) -> None:
    """Send a question from the plate panel to the chat view."""
    st.session_state.pending_question = question
    st.session_state.view = CHAT_VIEW


def set_example() -> None:
    st.session_state.meal_text = EXAMPLE_MEAL


def clear_meal() -> None:
    st.session_state.meal_text = ""


def clear_chat() -> None:
    st.session_state.messages = []


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("🥗 PoshanGuide")
    api_url = st.text_input("API address", API_URL_DEFAULT).rstrip("/")
    endpoint = st.selectbox("Endpoint", ["/ask", "/agent"], help="/ask = RAG with citations (Day 08). /agent = your Day 09 agent, if it is running.")
    top_k = st.slider("Chunks to retrieve (top-k)", 1, 10, 4, disabled=endpoint != "/ask")
    if backend_ok(api_url):
        st.success("Backend is running")
    else:
        st.error("Backend not reachable. Start it first (see README).")
    stats = feedback_stats()
    st.markdown(f"**Feedback saved:** 👍 {stats['up']}   👎 {stats['down']}")
    st.button("Clear chat", on_click=clear_chat)
    st.caption("General nutrition information only. It is not medical advice.")


# ------------------------------------------------------------------ chat view
def render_message(i: int, msg: dict) -> None:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] != "assistant":
            return
        if not msg.get("answerable", True):
            st.caption("The PoshanGuide documents do not contain this answer.")
        cits = msg.get("citations", [])
        if cits:
            with st.expander(f"📚 Sources ({len(cits)})"):
                for c in cits:
                    score = f" (similarity {c['score']})" if c.get("score") is not None else ""
                    where = f"`{c['source']}`" + (f", page {c['page']}" if c.get("page") != "" else "")
                    st.markdown(f"**[{c['id']}] {c.get('title') or c['source']}** - {where}{score}")
                    if c.get("snippet"):
                        st.caption(c["snippet"])
        rated = msg.get("rating")
        up, down, note = st.columns([1, 1, 10])
        up.button("👍", key=f"up_{msg['id']}", on_click=rate, args=(i, "up"), disabled=rated is not None,
                  type="primary" if rated == "up" else "secondary")
        down.button("👎", key=f"down_{msg['id']}", on_click=rate, args=(i, "down"), disabled=rated is not None,
                    type="primary" if rated == "down" else "secondary")
        if rated:
            note.caption("Thank you, your feedback is saved.")


def render_chat() -> None:
    st.header("Ask PoshanGuide")
    st.caption("Answers come only from the PoshanGuide documents, with sources. If the documents do not have the answer, PoshanGuide says \"I don't know\".")

    typed = st.chat_input("Ask a nutrition question, e.g. Which foods are rich in iron for a 2-year-old?")
    question = typed or st.session_state.pop("pending_question", None)
    if question:
        st.session_state.messages.append({"id": uuid.uuid4().hex[:10], "role": "user", "content": question})
        try:
            with st.spinner("Searching the PoshanGuide documents..."):
                result = ask_backend(api_url, endpoint, question, top_k)
            st.session_state.messages.append({
                "id": uuid.uuid4().hex[:10], "role": "assistant", "content": result["answer"],
                "answerable": result["answerable"], "citations": result["citations"],
                "question": question, "endpoint": endpoint})
        except RuntimeError as exc:
            st.error(str(exc))

    if not st.session_state.messages:
        st.info("Try: \"Which foods are rich in iron for a 2-year-old?\" or \"Which nutritionist near my village is free this week?\"")
    for i, msg in enumerate(st.session_state.messages):
        render_message(i, msg)


# ------------------------------------------------------------------ plate view
def bar_html(g: dict) -> str:
    """One colour bar. The dark line marks 100% of the NIN amount; the bar scale goes to 150%."""
    width = min(g["ratio"], 1.5) / 1.5 * 100
    eaten = f"{g['eaten_g']:g}"
    return f"""
<div style="margin:10px 0 14px 0;">
  <div style="display:flex;justify-content:space-between;font-size:0.92rem;margin-bottom:3px;">
    <span><b>{g['label']}</b></span>
    <span>{eaten} of {g['target_g']} g &nbsp;(<b style="color:{g['colour']}">{g['status_text']}</b>)</span>
  </div>
  <div style="position:relative;height:20px;background:rgba(128,128,128,0.22);border-radius:10px;overflow:hidden;">
    <div style="width:{width:.1f}%;height:100%;background:{g['colour']};border-radius:10px;"></div>
    <div style="position:absolute;left:66.67%;top:0;bottom:0;width:2px;background:rgba(0,0,0,0.55);"></div>
  </div>
</div>"""


def legend_html() -> str:
    items = [("low", "Low (under 50%)"), ("almost", "Almost there (50-89%)"), ("ontrack", "On track (90-125%)"),
             ("above", "Above the plate"), ("high", "Too much: cut back")]
    from plate import COLOURS
    chips = "".join(f'<span style="margin-right:14px;white-space:nowrap;"><span style="display:inline-block;width:12px;height:12px;'
                    f'border-radius:3px;background:{COLOURS[k]};margin-right:5px;"></span>{t}</span>' for k, t in items)
    return f'<div style="font-size:0.8rem;margin:6px 0;">{chips}<span style="white-space:nowrap;">| = NIN amount (100%)</span></div>'


def render_plate() -> None:
    ref = load_reference()
    st.header("🍽️ My plate check")
    st.caption(f"List what you ate today. The bars compare each food group with ICMR-NIN's \"My Plate for the Day\" "
               f"({ref['kcal']} kcal adult plate).")

    left, right = st.columns([2, 3], gap="large")
    with left:
        st.text_area("What did you eat today?", key="meal_text", height=230,
                     placeholder="One food per line or separated by commas, with a quantity:\n2 roti\n1 katori dal\n1 banana\n1 glass milk\n\nPress Ctrl+Enter to update.")
        b1, b2 = st.columns(2)
        b1.button("Load example meal", on_click=set_example)
        b2.button("Clear", on_click=clear_meal)
        with st.expander("Foods I understand and the unit for each"):
            st.caption("The number you type multiplies the unit. For example 2 roti = 2 x 1 roti. You can also write grams, like 150 g curd or 200 ml milk, or 'handful' for nuts and 'tbsp' for ghee.")
            st.dataframe(foods_help(), hide_index=True, height=300)

    parsed = parse_meal(st.session_state.meal_text)
    result = compute_plate(parsed, ref)

    with right:
        if not parsed["items"]:
            st.info("Type what you ate on the left, or click **Load example meal**.")
            if parsed["unrecognised"]:
                st.warning("I did not recognise: " + ", ".join(parsed["unrecognised"]))
        else:
            m1, m2 = st.columns(2)
            m1.metric("Food groups on track", f"{result['on_track']} of {result['total_groups']}")
            m2.metric("Foods outside the plate", result["limit_servings"],
                      help="Sweets, fried snacks, biscuits and soft drinks are not part of My Plate. Keep them small.")
            st.markdown(legend_html(), unsafe_allow_html=True)
            for g in result["groups"]:
                st.markdown(bar_html(g), unsafe_allow_html=True)

            if parsed["unrecognised"]:
                st.warning("I did not recognise: " + ", ".join(parsed["unrecognised"]) + ". Check the food list on the left.")
            if result["limit_items"]:
                st.caption("Outside the plate today: " + ", ".join(result["limit_items"]) + ". Keep these small.")

    if parsed["items"]:
        st.divider()
        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            st.subheader("Your plate compared with NIN")
            rows = ["| Food group | You ate (g) | NIN plate (g) | Your share | Plate share | Status |", "|---|---|---|---|---|---|"]
            for g in result["groups"]:
                rows.append(f"| {g['label']} | {g['eaten_g']:g} | {g['target_g']} | {g['share_eaten_pct']:g}% | {g['share_plate_pct']:g}% | {g['status_text']} |")
            st.markdown("\n".join(rows))
            with st.expander("How I read your meal"):
                for it in parsed["items"]:
                    parts = ", ".join(f"{k} {v:g} g" for k, v in it["grams"].items() if k != "limit") or ("outside the plate" if "limit" in it["grams"] else "no plate group")
                    st.markdown(f"- `{it['text']}` -> **{it['food']}** x {it['amount']:g} ({it['unit']}) = {parts}")
        with c2:
            st.subheader("Next step")
            if result["needs_more"]:
                for g in result["needs_more"][:3]:
                    st.markdown(f"**{g['label']}**: about {g['gap_g']:g} g more to reach the plate.")
                low = result["needs_more"][0]
                st.button(f"Ask PoshanGuide about {low['label'].split(' (')[0].lower()}", on_click=ask_about,
                          args=(low["ask"],), type="primary")
            else:
                st.success("Every group is at or above 90% of the plate. Well done!")
            high = [g for g in result["groups"] if g["status"] == "high"]
            for g in high:
                st.markdown(f"**{g['label']}**: about {g['excess_g']:g} g above the plate. Try to cut back.")

    st.caption(f"Source: {ref['source']}. Amounts are for a {ref['kcal']} kcal adult plate, as raw or edible weight. "
               "Household amounts are rough estimates (1 roti = 30 g flour, 1 katori dal = 30 g raw dal, 1 katori sabzi = 100 g). "
               "Children, pregnant and breastfeeding women, and people with medical conditions need different amounts: ask your doctor or Anganwadi worker.")


# ------------------------------------------------------------------ main
st.radio("View", [CHAT_VIEW, PLATE_VIEW], horizontal=True, key="view", label_visibility="collapsed")
if st.session_state.view == CHAT_VIEW:
    render_chat()
else:
    render_plate()
