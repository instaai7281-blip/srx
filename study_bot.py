import logging
import sys
from telethon import TelegramClient, events, functions
from telethon.tl.types import InputRichMessageMarkdown
from config import API_ID, API_HASH, BOT_TOKEN

# Configure logging
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

bot = TelegramClient("study_bot_session", API_ID, API_HASH)

START_TEXT = """
# 🎓 Study Companion Bot

Welcome to your ultimate study assistant.

To access the complete reference library of formulas, cheat sheets, and trackers, use the main command below:

👉 /maths — Master Formula Reference (Algebra, Arithmetic, Geometry & Science)

---
🛡️ Developed by **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

MATHS_TEXT = """
# 📐 Master Formula Reference

Welcome to the consolidated formula database. Click the section you want to study:
- `/algebra` — Higher Mathematics (Algebra, Calculus & Probability)
- `/arithmetic` — Percentages, Ratios & Financial Mathematics
- `/geometry` — Perimeter, Area & 3D Shape Volume tables
- `/cheatsheet` — Science Quick Reference (Physics & Chemistry)
- `/timetable` — Weekly Study Schedule
- `/checklist` — Syllabus Progress Tracker

---
Compiled by **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

ALGEBRA_TEXT = """
# 📐 Higher Mathematics Formulas

## 1. Algebra & Series
* **Quadratic Formula:**
  If $ax^2 + bx + c = 0$, then:
  $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
* **Binomial Theorem:**
  $$(a+b)^n = \\sum_{k=0}^{n} \\binom{n}{k} a^{n-k} b^k$$

## 2. Calculus
* **Derivative Definition:**
  $$f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}$$
* **Integration by Parts:**
  $$\\int u\\,dv = uv - \\int v\\,du$$

## 3. Probability & Statistics
* **Bayes' Theorem:**
  $$P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}$$
* **Standard Deviation (Sample):**
  $$s = \\sqrt{\\frac{\\sum_{i=1}^{n} (x_i - \\bar{x})^2}{n-1}}$$

---
🛡️ Owner: **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

ARITHMETIC_TEXT = """
# 🧮 Arithmetic: Percentages & Ratios

## 1. Percentages
* **Percentage Change:**
  $$\\text{Percentage Change} = \\frac{\\text{New Value} - \\text{Old Value}}{\\text{Old Value}} \\times 100\\%$$
* **Profit & Loss Percentage:**
  $$\\text{Profit \\%} = \\frac{\\text{Selling Price} - \\text{Cost Price}}{\\text{Cost Price}} \\times 100\\%$$
  $$\\text{Loss \\%} = \\frac{\\text{Cost Price} - \\text{Selling Price}}{\\text{Cost Price}} \\times 100\\%$$
* **Simple Interest:**
  $$I = \\frac{P \\cdot r \\cdot t}{100}$$
* **Compound Interest:**
  $$A = P \\left(1 + \\frac{r}{n}\\right)^{nt}$$
  _Where $A$ is the total amount, $P$ is principal, $r$ is interest rate, $n$ is compounding frequency, and $t$ is time._

## 2. Ratio & Proportion
* **Ratio Equality (Proportion):**
  $$\\frac{a}{b} = \\frac{c}{d} \\implies a \\cdot d = b \\cdot c$$
* **Compound Ratio:**
  $$\\text{Compound of } a:b \\text{ and } c:d \\text{ is } (a \\cdot c) : (b \\cdot d)$$
* **Direct Variation:** $y = k \\cdot x$ (where $k$ is constant)
* **Inverse Variation:** $y = \\frac{k}{x} \\implies x \\cdot y = k$

---
🛡️ Owner: **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

GEOMETRY_TEXT = """
# 📏 Geometry: Area & Volume Formulas

## 1. 2D Shapes (Area & Perimeter)
* **Circle:**
  * $\\text{Area} = \\pi r^2$
  * $\\text{Circumference} = 2\\pi r$
* **Triangle:**
  * $\\text{Area} = \\frac{1}{2} \\cdot b \\cdot h$
  * $\\text{Heron's Formula:} \\sqrt{s(s-a)(s-b)(s-c)} \\quad \\text{where } s = \\frac{a+b+c}{2}$

## 2. 3D Solids (Volume & Surface Area)
| Solid Shape | Volume Formula | Total Surface Area (TSA) |
|:---|:---:|:---|
| **Sphere** | $V = \\frac{4}{3}\\pi r^3$ | $A = 4\\pi r^2$ |
| **Cylinder** | $V = \\pi r^2 h$ | $A = 2\\pi r(r + h)$ |
| **Cone** | $V = \\frac{1}{3}\\pi r^2 h$ | $A = \\pi r(r + \\sqrt{r^2 + h^2})$ |
| **Cube** | $V = a^3$ | $A = 6a^2$ |
| **Rect. Prism** | $V = l \\cdot w \\cdot h$ | $A = 2(lw + lh + wh)$ |

---
🛡️ Owner: **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

CHEATSHEET_TEXT = """
# 📊 Subject Cheat Sheet

| Subject | Topic | Key Formula | Explanation |
|:---|:---|:---:|:---|
| **Physics** | Gravity | $F = G \\frac{m_1 m_2}{r^2}$ | Universal Gravitational Force |
| **Physics** | Einstein | $E = mc^2$ | Mass-energy Equivalence |
| **Chemistry**| Ideal Gas | $PV = nRT$ | Pressure, Vol, Temp relation |
| **Chemistry**| pH Value | $\\text{pH} = -\\log_{10}[\\text{H}^+]$ | Acidity/Alkalinity measure |
| **Math** | Euler Poly | $V - E + F = 2$ | Vertices, Edges, Faces |
| **Math** | Euler Identity| $e^{i\\pi} + 1 = 0$ | Linking 5 major constants |

---
🛡️ Owner: **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

TIMETABLE_TEXT = """
# 📅 Study Timetable

| Day | 09:00 - 12:00 | 14:00 - 17:00 | 19:00 - 22:00 |
|:---|:---:|:---:|:---:|
| **Mon** | Math (Algebra) 📐 | Physics (Mechanics) ⚛️ | Revision & Homework 📝 |
| **Tue** | Chemistry (Organic) 🧪| English Literature 📖 | Coding Practice 💻 |
| **Wed** | Biology (Genetics) 🌿 | History (World War) 🏛️ | Mock Test Practice ⏱️ |
| **Thu** | Math (Calculus) 📐 | Physics (Optics) ⚛️ | Coding Practice 💻 |
| **Fri** | Chemistry (Inorg) 🧪 | Revision 📝 | Project Work 🚀 |
| **Sat** | Full Mock Test 🏆 | Performance Analysis 📊 | General Knowledge 🌍 |
| **Sun** | Off / Buffer Time 🏖️ | Plan Next Week 📅 | Reading Books 📚 |

---
🛡️ Owner: **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

CHECKLIST_TEXT = """
# 📋 Syllabus Tracker Checklist

## 1. Mathematics
- [x] Algebra: Quadratic Equations & Binomials
- [x] Calculus: Limits & Basic Derivatives
- [ ] Integration: Definite & Indefinite Integrals
- [ ] Statistics: Variance & Standard Deviation

## 2. Arithmetic
- [x] Ratio & Proportion rules
- [x] Simple & Compound Interest formulas
- [ ] Percentage profit, loss & discount hacks

## 3. Physics
- [x] Mechanics: Newton's Laws & Friction
- [ ] Gravity & Orbital Mechanics
- [ ] Thermodynamics & Heat Transfer

---
🛡️ Owner: **𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝**
"""

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Study Reference Menu",
        rich_message=InputRichMessageMarkdown(markdown=START_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/maths"))
async def maths_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Master Reference",
        rich_message=InputRichMessageMarkdown(markdown=MATHS_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/algebra"))
async def algebra_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Algebra Formulas",
        rich_message=InputRichMessageMarkdown(markdown=ALGEBRA_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/arithmetic"))
async def arithmetic_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Arithmetic Formulas",
        rich_message=InputRichMessageMarkdown(markdown=ARITHMETIC_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/geometry"))
async def geometry_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Geometry Formulas",
        rich_message=InputRichMessageMarkdown(markdown=GEOMETRY_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/cheatsheet"))
async def cheatsheet_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Science Cheat Sheet",
        rich_message=InputRichMessageMarkdown(markdown=CHEATSHEET_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/timetable"))
async def timetable_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Study Timetable",
        rich_message=InputRichMessageMarkdown(markdown=TIMETABLE_TEXT),
    ))

@bot.on(events.NewMessage(pattern="/checklist"))
async def checklist_handler(e):
    await bot(functions.messages.SendMessageRequest(
        peer=await e.get_input_chat(),
        message="Syllabus Tracker",
        rich_message=InputRichMessageMarkdown(markdown=CHECKLIST_TEXT),
    ))

if __name__ == "__main__":
    print("[INFO] Starting Study Companion Bot...")
    bot.start(bot_token=BOT_TOKEN)
    print("[INFO] Bot is running...")
    bot.run_until_disconnected()
