# app.py — Wordle-like game as a single-file Streamlit app
# --------------------------------------------------------
# How to run locally:
#   1) pip install streamlit
#   2) streamlit run app.py
#
# Optional: put your own 5-letter word list in a file named "words.txt"
#   (one word per line, lowercase). The app will auto-load it if present.
# --------------------------------------------------------

import random
import string
from pathlib import Path

import streamlit as st

WORD_LENGTH = 5
MAX_GUESSES = 6

# -------------------- Utilities --------------------
def load_words() -> list[str]:
    """Load candidate words. If words.txt exists (one word per line), use it.
    Otherwise, fall back to a small default list.
    """
    p = Path("words.txt")
    if p.exists():
        words = [w.strip().lower() for w in p.read_text(encoding="utf-8").splitlines()]
        words = [w for w in words if len(w) == WORD_LENGTH and all(ch in string.ascii_lowercase for ch in w)]
        if words:
            return words
    # Safe default list (replace with your own list in words.txt)
    return ['abbie', 'abeed', 'aired', 'argie', 'aseng', 'asing', 'bahia', 'bantu', 'batak', 'bimbo', 'bindi', 'bitch', 'boang', 'boche', 'bosch', 'bulba','bunga', 'chink','cholo', 'chong', 'cokin','cushi', 'dalle', 'darky','dhoti', 'dogan', 'dogun','fricc', 'fritz', 'gabel','gadjo', 'galla', 'garoi', 'ghati', 'ginzo', 'gippo', 'godon', 'gooky','goyim', 'goyum', 'grago', 'groid', 'gubba', 'guido', 'gyppo', 'gyppy','gypsy', 'hadji', 'hajji', 'hamba', 'haole','hujaa', 'hunky', 'hurri', 'hymie', 'injun','jakun', 'jamet', 'jawir', 'jerry', 'jidan', 'jidov','jocky', 'kafir', 'kalar', 'kalia', 'kallu', 'katwa', 'katwe', 'kebab', 'khach','kraut', 'labas','leupe', 'limey', 'lubra', 'lugan', 'lyakh', 'majus', 'malau','malon', 'manne','mocro', 'momos', 'namak','nawar', 'neger', 'negro', 'nichi', 'nidge', 'nigar', 'niger', 'nigga', 'nigor','nigra', 'nigre','paddy', 'penis', 'piker', 'pikey','plouc', 'pocha', 'pocho', 'polak', 'pommy', 'pshek', 'pussy','rapes', 'raper','roske', 'ruski','seppo', 'shina','slant','slobo', 'slope', 'slopy','sooty','spade','spick', 'spook', 'squaw','szkop', 'szwab', 'taffy', 'tanka', 'tibla', 'timur', 'today', 'tonto', 'turco', 'turko', 'turks', 'ukrop', 'vanja', 'wigga']


def choose_answer(words: list[str]) -> str:
    return random.choice(words)


def wordle_feedback(guess: str, answer: str) -> list[int]:
    """Return per-letter feedback using Wordle rules.
    2 = correct position (green), 1 = in word wrong spot (yellow), 0 = absent (gray).
    """
    result = [0] * WORD_LENGTH
    # First pass: mark greens and track remaining letters in answer
    remaining = {}
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = 2
        else:
            remaining[a] = remaining.get(a, 0) + 1
    # Second pass: mark yellows
    for i, g in enumerate(guess):
        if result[i] != 0:
            continue
        if remaining.get(g, 0) > 0:
            result[i] = 1
            remaining[g] -= 1
    return result


def update_keyboard(kb: dict[str, int], guess: str, fb: list[int]) -> None:
    """Track the best-known status per letter: 0<1<2 dominance.
    kb maps letter -> status (0,1,2)."""
    for ch, s in zip(guess, fb):
        kb[ch] = max(kb.get(ch, -1), s)


# -------------------- Rendering --------------------
CSS = """
<style>
.tile { display:inline-block; width: 3rem; height: 3rem; line-height: 3rem; 
        text-align:center; font-weight:700; border-radius: 0.4rem; margin: 0.15rem; 
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.t0 { background:#3a3a3c; color:white; }     /* gray */
.t1 { background:#b59f3b; color:white; }     /* yellow */
.t2 { background:#538d4e; color:white; }     /* green */
.tE { background:#121213; color:#d7dadc; border:1px solid #3a3a3c; } /* empty */
.kb  { display:inline-block; width: 2rem; height: 2.4rem; line-height: 2.4rem; margin: 0.1rem; border-radius: 0.35rem; font-weight:700; }
</style>
"""

STATUS_TO_CLASS = {0: "t0", 1: "t1", 2: "t2"}


def render_board(guesses: list[str], feedbacks: list[list[int]]):
    st.markdown(CSS, unsafe_allow_html=True)
    rows = []
    for i in range(MAX_GUESSES):
        if i < len(guesses):
            g = guesses[i]
            fb = feedbacks[i]
            tiles = "".join(
                f'<span class="tile {STATUS_TO_CLASS[s]}">{g[j].upper()}</span>' for j, s in enumerate(fb)
            )
        else:
            tiles = "".join(f'<span class="tile tE">&nbsp;</span>' for _ in range(WORD_LENGTH))
        rows.append(tiles)
    st.markdown("<div>" + "<br>".join(rows) + "</div>", unsafe_allow_html=True)


def render_keyboard(kb: dict[str, int]):
    # Show rows like a QWERTY keyboard
    rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    html_rows = []
    for r in rows:
        pieces = []
        for ch in r:
            s = kb.get(ch, None)
            cls = "tE" if s is None else STATUS_TO_CLASS[s]
            pieces.append(f'<span class="tile kb {cls}">{ch.upper()}</span>')
        html_rows.append("".join(pieces))
    st.markdown("<div>" + "<br>".join(html_rows) + "</div>", unsafe_allow_html=True)


# -------------------- App State --------------------
if "words" not in st.session_state:
    st.session_state.words = load_words()
if "answer" not in st.session_state:
    st.session_state.answer = choose_answer(st.session_state.words)
if "guesses" not in st.session_state:
    st.session_state.guesses = []      # list[str]
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []    # list[list[int]]
if "keyboard" not in st.session_state:
    st.session_state.keyboard = {}     # dict[ch] -> best status (0,1,2)
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# -------------------- Sidebar --------------------
st.sidebar.header("Settings")
st.sidebar.write("Loaded words:", len(st.session_state.words))
if st.sidebar.button("🔁 New Answer / Restart"):
    st.session_state.answer = choose_answer(st.session_state.words)
    st.session_state.guesses = []
    st.session_state.feedbacks = []
    st.session_state.keyboard = {}
    st.session_state.game_over = False
    st.rerun()

# -------------------- Main --------------------
st.title("Slurdle")
st.caption("Type a 5-letter guess and press Enter. You have 6 guesses.")

render_board(st.session_state.guesses, st.session_state.feedbacks)
render_keyboard(st.session_state.keyboard)

if not st.session_state.game_over:
    guess = st.text_input("Your guess:", max_chars=WORD_LENGTH).strip().lower()
    submitted = st.button("Submit guess", type="primary") or (len(guess) == WORD_LENGTH and st.session_state.get("_enter_submit", False))

    # Pressing Enter in the text box should also submit; Streamlit doesn't do this natively
    # so we emulate a tiny state flag when length is exactly WORD_LENGTH.
    if len(guess) == WORD_LENGTH and not submitted:
        st.session_state._enter_submit = True
    else:
        st.session_state._enter_submit = False

    # Validate and process
    if submitted:
        if len(guess) != WORD_LENGTH or not all(ch in string.ascii_lowercase for ch in guess):
            st.error("Please enter exactly five alphabetic letters.")
        # elif guess not in st.session_state.words:
        #     st.warning("Word not in list. (Add it to words.txt if you want it allowed.)")
        else:
            fb = wordle_feedback(guess, st.session_state.answer)
            st.session_state.guesses.append(guess)
            st.session_state.feedbacks.append(fb)
            update_keyboard(st.session_state.keyboard, guess, fb)

            if guess == st.session_state.answer:
                st.success(f"🎉 Correct! The word was **{st.session_state.answer.upper()}**.")
                st.session_state.game_over = True
            elif len(st.session_state.guesses) >= MAX_GUESSES:
                st.error(f"Out of guesses. The word was **{st.session_state.answer.upper()}**.")
                st.session_state.game_over = True

            st.rerun()
else:
    col1, col2 = st.columns(2)
    st.success(f"You lost, you f***ing {st.session_state.answer.upper()}")
    #st.success(f"The word was {st.session_state.answer.upper()}")
    if col1.button("Play again"):
        st.session_state.answer = choose_answer(st.session_state.words)
        st.session_state.guesses = []
        st.session_state.feedbacks = []
        st.session_state.keyboard = {}
        st.session_state.game_over = False
        st.rerun()
    # if col2.button("Reveal a new random word but keep board"):
    #     st.session_state.answer = choose_answer(st.session_state.words)
    #     st.success("New answer chosen. Keep guessing!")
