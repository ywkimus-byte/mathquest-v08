"""Math Quest v0.6 (Streamlit edition) — original Gradio learning logic preserved."""

import random
import html
import copy

# 각 단계는 고정된 학습 개념을 가집니다. 최대 6단계이며 마지막 단계는 반복합니다.
LEVELS = [
    ("5 이하 덧셈", "두 수의 합이 5 이하"),
    ("10 이하 덧셈", "두 수의 합이 10 이하"),
    ("10 만들기", "합이 정확히 10"),
    ("받아올림 연습", "한 자리 수 + 한 자리 수, 합이 11~18"),
    ("20 이하 혼합 덧셈", "합이 20 이하인 덧셈"),
    ("두 자리 수 덧셈", "두 자리 수 + 한 자리 수, 합이 99 이하"),
]
QUESTIONS_PER_ROUND = 5
PASS_SCORE = 4


def make_question(level, avoid=None):
    """단계 학습 목표를 만족하는 덧셈 한 문제 생성."""
    level = min(max(int(level), 1), len(LEVELS))
    avoid = avoid or []
    candidates = []
    if level == 1:
        candidates = [(a, b) for a in range(1, 5) for b in range(a, 5) if a+b <= 5]
    elif level == 2:
        candidates = [(a, b) for a in range(1, 10) for b in range(a, 10) if a+b <= 10]
    elif level == 3:
        candidates = [(a, 10-a) for a in range(1, 6)]
    elif level == 4:
        candidates = [(a, b) for a in range(2, 10) for b in range(a, 10) if 11 <= a+b <= 18]
    elif level == 5:
        candidates = [(a, b) for a in range(1, 20) for b in range(a, 20) if a+b <= 20]
    else:
        candidates = [(a, b) for a in range(10, 90) for b in range(1, 10) if a+b <= 99]
    fresh = [q for q in candidates if q not in avoid]
    return random.choice(fresh or candidates)


def initial_state():
    return {
        "level": 1, "score": 0, "count": 0, "correct": 0,
        "question": make_question(1), "mode": "normal",
        "wrong": [], "review_index": 0, "review_correct": 0,
        "recent": [], "level_attempts": {},
        "badges": [], "streak": 0, "best_streak": 0, "normal_total": 0,
    }


def add_wrong(state, a, b):
    a, b = int(a), int(b)
    for item in state["wrong"]:
        if (item["a"], item["b"]) == (a, b) or (item["a"], item["b"]) == (b, a):
            item["times"] += 1
            return
    state["wrong"].append({"a": a, "b": b, "times": 1})


def show_wrong(state):
    if not state["wrong"]:
        return "### 📒 오답노트\n복습할 오답이 없습니다. 🎉"
    lines = ["### 📒 오답노트", "복습에서 맞히면 목록에서 제거됩니다."]
    for i, item in enumerate(state["wrong"], 1):
        lines.append(f"{i}. **{item['a']} + {item['b']} = {item['a']+item['b']}** (오답 {item['times']}회)")
    return "\n\n".join(lines)


def show_game(state):
    a, b = state["question"]
    level = min(state["level"], len(LEVELS))
    name, description = LEVELS[level-1]
    review = state["mode"] == "review"
    progress = 0 if review else state["count"] / QUESTIONS_PER_ROUND * 100
    status = f"오답 복습: {len(state['wrong'])}문제 남음" if review else f"진행도 {state['count']}/{QUESTIONS_PER_ROUND}"
    return f"""
    <div style="background:linear-gradient(135deg,#e5f8ed,#dceaff);border-radius:22px;padding:28px;text-align:center;color:#213349">
      <h1>{'📘 오답 복습 훈련소' if review else '🏰 Math Quest'}</h1>
      <h2>⭐ 레벨 {level} — {html.escape(name)}</h2>
      <p>{html.escape(description)}</p>
      <div style="font-size:52px">{'📖 🧠 ✏️' if review else '🧙‍♂️ 🗝️ 🏰'}</div>
      <div style="background:#cdd6e3;border-radius:10px;height:14px;overflow:hidden">
        <div style="background:#28a978;height:100%;width:{progress:.0f}%"></div>
      </div>
      <p>{status}</p><h1>{a} + {b} = ?</h1>
      <h3>🏆 점수 {state['score']} | 📒 남은 오답 {len(state['wrong'])}</h3>
    </div>"""


def next_normal_question(state):
    state["question"] = make_question(state["level"], state.get("recent", []))
    state["recent"] = (state.get("recent", []) + [state["question"]])[-4:]


def check(answer, state):
    state = copy.deepcopy(state)
    if answer is None or answer == "":
        return show_game(state), "⚠️ 정답을 입력해 주세요.", show_wrong(state), state
    try:
        value = float(answer)
        if not value.is_integer():
            raise ValueError
    except (ValueError, TypeError):
        return show_game(state), "⚠️ 정수를 입력해 주세요.", show_wrong(state), state
    a, b = state["question"]
    correct = int(value) == a+b
    if state["mode"] == "review":
        idx = state["review_index"]
        if correct:
            state["wrong"].pop(idx)
            state["review_correct"] += 1
            state["score"] += 10
            msg = "✅ 복습 성공! 오답노트에서 제거했어요."
        else:
            item = state["wrong"].pop(idx)
            item["times"] += 1
            state["wrong"].append(item)
            msg = f"📚 정답은 {a+b}. 다시 도전해 보세요."
        if not state["wrong"]:
            state["mode"] = "normal"
            state["review_index"] = 0
            next_normal_question(state)
            msg += " 🎉 복습 완료!"
        else:
            state["review_index"] = idx % len(state["wrong"])
            item = state["wrong"][state["review_index"]]
            state["question"] = (item["a"], item["b"])
    else:
        state["count"] += 1
        state["normal_total"] += 1
        if correct:
            state["correct"] += 1
            state["score"] += 10
            state["streak"] += 1
            state["best_streak"] = max(state["best_streak"], state["streak"])
            msg = "🎉 정답입니다!"
        else:
            add_wrong(state, a, b)
            state["streak"] = 0
            msg = f"📚 정답은 {a+b}. 오답노트에 저장했습니다."
        if state["count"] == QUESTIONS_PER_ROUND:
            lvl = state["level"]
            state["level_attempts"].setdefault(str(lvl), []).append(state["correct"])
            if state["correct"] >= PASS_SCORE:
                if lvl < len(LEVELS):
                    state["level"] += 1
                    msg += " 🏆 다음 레벨을 열었습니다!"
                else:
                    msg += " 🏅 모든 레벨 통과! 최고 레벨을 계속 연습합니다."
            else:
                msg += " 🔄 현재 레벨에서 다시 도전합니다."
            state["count"], state["correct"] = 0, 0
        next_normal_question(state)
    earned = grant_badges(state)
    if earned:
        msg += " 🎖️ 새 배지: " + ", ".join(earned)
    return show_game(state), msg, show_wrong(state), state


def start_review(state):
    state = copy.deepcopy(state)
    if not state["wrong"]:
        return show_game(state), "📒 복습할 문제가 없습니다.", show_wrong(state), state
    state["mode"] = "review"
    state["review_index"] = 0
    item = state["wrong"][0]
    state["question"] = (item["a"], item["b"])
    return show_game(state), "📘 오답 복습을 시작합니다.", show_wrong(state), state


def go_normal(state):
    state = copy.deepcopy(state)
    state["mode"] = "normal"
    next_normal_question(state)
    return show_game(state), "🏰 일반 학습으로 돌아왔습니다.", show_wrong(state), state

BADGE_RULES = {
    "🌱 첫걸음": "첫 문제를 맞혔어요",
    "🔥 연속 정답": "연속 5문제를 맞혔어요",
    "📘 오답 정복자": "오답 5문제를 복습하여 해결했어요",
    "🏅 덧셈 마스터": "최종 레벨을 통과했어요",
}


def grant_badges(state):
    earned = []
    checks = [
        ("🌱 첫걸음", state["score"] >= 10),
        ("🔥 연속 정답", state["best_streak"] >= 5),
        ("📘 오답 정복자", state["review_correct"] >= 5),
        ("🏅 덧셈 마스터", any(n >= PASS_SCORE for n in state["level_attempts"].get(str(len(LEVELS)), []))),
    ]
    for badge, yes in checks:
        if yes and badge not in state["badges"]:
            state["badges"].append(badge)
            earned.append(badge)
    return earned


def show_badges(state):
    items = []
    for badge, desc in BADGE_RULES.items():
        unlocked = badge in state["badges"]
        items.append(f"<div style='background:{'#e4f9ec' if unlocked else '#f0f1f4'};padding:14px;border-radius:14px;min-width:150px;flex:1'>"
                     f"<b>{badge if unlocked else '🔒 '+html.escape(badge.split(' ',1)[1])}</b><br>"
                     f"<small>{html.escape(desc)}</small></div>")
    return "<div style='display:flex;flex-wrap:wrap;gap:9px;color:#203047'>" + "".join(items) + "</div>"

WORLD_NAMES = ["숫자 숲", "덧셈 마을", "10의 탑", "받아올림 성", "모험 동굴", "수학 왕궁"]
WORLD_ICONS = ["🌲", "🏘️", "🗼", "🏰", "🪨", "👑"]


def show_map(state):
    current = state["level"]
    cards = []
    for idx, (name, icon) in enumerate(zip(WORLD_NAMES, WORLD_ICONS), 1):
        status = "✅ 완료" if idx < current else ("▶️ 도전 중" if idx == current else "🔒 잠김")
        bg = "#d6f4e1" if idx < current else ("#ffedbd" if idx == current else "#edf0f4")
        cards.append(f"<div style='background:{bg};padding:17px;border-radius:18px;min-width:130px;flex:1;text-align:center'>"
                     f"<div style='font-size:37px'>{icon}</div><b>{idx}. {html.escape(name)}</b>"
                     f"<div style='font-size:13px'>{status}</div></div>")
    return "<div style='display:flex;flex-wrap:wrap;gap:10px;color:#26364b'>"+"".join(cards)+"</div>"

import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone


def show_stats(state):
    attempts = state.get("level_attempts", {})
    cards = [f"<div style='padding:12px;border-radius:12px;background:#eef7ff;flex:1'>"
             f"<b>레벨 {level}</b><br>최근 결과: {values[-1]}/5점<br>도전 {len(values)}회</div>"
             for level, values in sorted(attempts.items(), key=lambda e: int(e[0])) if values]
    if not cards:
        return "<p>아직 완료된 5문제 묶음이 없습니다. 문제를 풀면 여기에 기록됩니다.</p>"
    return "<div style='display:flex;flex-wrap:wrap;gap:10px;color:#26364b'>"+"".join(cards)+"</div>"


def validate_record(data):
    if not isinstance(data, dict):
        raise ValueError("학습 기록 형식이 올바르지 않습니다.")
    if data.get("app") != "mathquest" or data.get("schema") != 1:
        raise ValueError("Math Quest 저장 파일이 아닙니다.")
    s = data.get("state")
    if not isinstance(s, dict):
        raise ValueError("학습 상태가 없습니다.")
    needed = ("level", "score", "count", "correct", "question", "wrong", "mode")
    if any(k not in s for k in needed):
        raise ValueError("필수 학습 기록이 누락되었습니다.")
    if not isinstance(s["level"], int) or not 1 <= s["level"] <= len(LEVELS):
        raise ValueError("잘못된 레벨입니다.")
    if s["mode"] not in ("normal", "review"):
        raise ValueError("잘못된 학습 모드입니다.")
    if not isinstance(s["question"], list) or len(s["question"]) != 2:
        raise ValueError("문제 형식이 올바르지 않습니다.")
    if not isinstance(s["wrong"], list) or len(s["wrong"]) > 5000:
        raise ValueError("오답 기록이 올바르지 않습니다.")
    for item in s["wrong"]:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), int) for k in ("a", "b", "times")):
            raise ValueError("오답 항목이 올바르지 않습니다.")
    normalized = initial_state()
    normalized.update({k: v for k, v in s.items() if k in normalized})
    normalized["question"] = tuple(normalized["question"])
    normalized["recent"] = [tuple(q) for q in normalized.get("recent", [])]
    if normalized["mode"] == "review":
        if not normalized["wrong"]:
            normalized["mode"] = "normal"
            next_normal_question(normalized)
        else:
            normalized["review_index"] = min(max(0, int(normalized["review_index"])), len(normalized["wrong"])-1)
            item = normalized["wrong"][normalized["review_index"]]
            normalized["question"] = (item["a"], item["b"])
    return normalized


def export_record(state):
    content = {"app": "mathquest", "schema": 1, "saved_at": datetime.now(timezone.utc).isoformat(), "state": state}
    path = Path(tempfile.mkdtemp(prefix="mathquest_")) / "mathquest_record.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path), "✅ 저장 파일을 다운로드하여 보관하세요."


def import_record(file, state):
    if file is None:
        return (show_game(state), "⚠️ 복원할 JSON 파일을 선택하세요.", show_wrong(state),
                show_badges(state), show_map(state), show_stats(state), state)
    try:
        path = file if isinstance(file, str) else file.name
        if Path(path).stat().st_size > 2_000_000:
            raise ValueError("저장 파일이 너무 큽니다.")
        saved = json.loads(Path(path).read_text(encoding="utf-8"))
        loaded = validate_record(saved)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return (show_game(state), f"⚠️ 불러오기 실패: {html.escape(str(exc))}", show_wrong(state),
                show_badges(state), show_map(state), show_stats(state), state)
    return (show_game(loaded), "✅ 저장한 학습 기록을 복원했습니다.", show_wrong(loaded),
            show_badges(loaded), show_map(loaded), show_stats(loaded), loaded)


def screen_check(answer, state):
    game, msg, wrong, st = check(answer, state)
    return (game, msg, wrong, show_badges(st), show_map(st), show_stats(st), st)

def screen_review(state):
    game, msg, wrong, st = start_review(state)
    return (game, msg, wrong, show_badges(st), show_map(st), show_stats(st), st)

def screen_normal(state):
    game, msg, wrong, st = go_normal(state)
    return (game, msg, wrong, show_badges(st), show_map(st), show_stats(st), st)




# ===== v07/v08 pure learning extensions (the v06 functions above remain available) =====
from collections import defaultdict
from datetime import datetime, timezone
import io
import csv

SCHEMA_VERSION = 3
SKILLS = ["BASIC_ADD", "ADD_WITHIN_10", "MAKE_10", "CARRY_ADD", "MIXED_ADD", "TWO_DIGIT_ADD"]
SKILL_NAMES = dict(zip(SKILLS, [v[0] for v in LEVELS]))
PREDECESSOR = {"CARRY_ADD":"MAKE_10", "MIXED_ADD":"CARRY_ADD", "TWO_DIGIT_ADD":"ADD_WITHIN_10",
               "MAKE_10":"ADD_WITHIN_10", "ADD_WITHIN_10":"BASIC_ADD"}
ROUND_SIZE = 10

def skill_for(level):
    return SKILLS[max(0, min(int(level)-1, 5))]

def candidates_for(level):
    # Grounded in the original v06 problem pools; no huge random runtime loops.
    level=int(level)
    if level==1:
        return [(a,b) for a in range(1,5) for b in range(a,5) if a+b<=5]
    if level==2:
        return [(a,b) for a in range(1,10) for b in range(a,10) if a+b<=10]
    if level==3:
        return [(a,10-a) for a in range(1,6)]
    if level==4:
        return [(a,b) for a in range(2,10) for b in range(a,10) if 11<=a+b<=18]
    if level==5:
        return [(a,b) for a in range(1,20) for b in range(a,20) if a+b<=20]
    return [(a,b) for a in range(10,90) for b in range(1,10) if a+b<=99]

def new_state():
    s=initial_state()
    s.update({"schema_source": 3, "skill_history":[],"hint_history":[], "current_hints":0,
              "round_log":[],"remedial_skill":None,"remedial_count":0,"mode":"normal",
              "review_return_mode":"normal", "pretest":None,"posttest":None,
              "assessment_answers":[], "assessment_items":[], "assessment_index":0,
              "assessment_form":None, "learning_sessions":[]})
    s['count']=0; s['correct']=0
    s['question']=make_question(1)
    return s

def generate_problem(level, avoid=None):
    pool=candidates_for(level)
    avoid={tuple(q) for q in (avoid or [])}
    fresh=[q for q in pool if q not in avoid and (q[1],q[0]) not in avoid]
    return tuple(random.choice(fresh or pool))

def hint_text(level,a,b,step):
    if step==1:
        if level==3: return "10이 되도록 두 수를 합해 보세요."
        if level>=4 and a<10 and b<10 and a+b>10: return f"{a}에 얼마를 더하면 10이 될까요?"
        return "수를 두 부분으로 나누거나 수를 세어 보세요."
    if step==2:
        if level>=4 and a<10 and b<10 and a+b>10:
            need=10-a
            return f"{b}를 {need}와 {b-need}로 나누면 10 만들기를 할 수 있어요."
        return f"● {a}개와 ● {b}개를 모아서 세어 보세요."
    if step==3:
        if level>=4 and a<10 and b<10 and a+b>10:
            need=10-a
            return f"{a} + {b} = ({a} + {need}) + {b-need} = {a+b}"
        return f"{a} + {b} = {a+b}"
    return ""

def hint_dots(a,b):
    return ' '.join(['🔵']*min(a,10)) + '   +   ' + ' '.join(['🟢']*min(b,10))

def record_attempt(s,level,question,answer,correct,hints,mode):
    s['skill_history'].append({"skill":skill_for(level),"level":level,"a":question[0],"b":question[1],
        "answer":answer,"correct":bool(correct),"hints":hints,"mode":mode,"at":datetime.now(timezone.utc).isoformat()})
    s['skill_history']=s['skill_history'][-3000:]
    if hints:
        s['hint_history'].append({"skill":skill_for(level),"count":hints})

def accuracy_for_skill(s,skill):
    xs=[r for r in s['skill_history'] if r['skill']==skill and r['mode'] in ('normal','remedial')]
    xs=xs[-5:]
    if not xs: return None,0
    return sum(bool(x['correct']) for x in xs)/len(xs),len(xs)

def recommended_skill(s):
    # Diagnose only after five recent attempts within a skill; never overinfer a single error.
    current=skill_for(s['level'])
    score,n=accuracy_for_skill(s,current)
    if n<5: return None
    return current if score<0.8 else None

def round_plan(level):
    # 8 current-level problems, 2 cumulative review (at level 1, all from level 1).
    levels=[level]*8+[max(1,level-1)]*2
    random.shuffle(levels)
    return levels

def begin_round(s):
    s['round_plan']=round_plan(s['level']); s['round_log']=[]; s['count']=0; s['correct']=0
    s['mode']='normal'
    s['question_level']=s['round_plan'][0]
    s['question']=generate_problem(s['question_level'])
    s['current_hints']=0

def ensure_ready(s):
    if not s.get('round_plan') or len(s.get('round_log',[]))>=10:
        begin_round(s)
    return s

def finish_round(s):
    logs=s['round_log']
    target=[r for r in logs if r['level']==s['level']]
    prior=[r for r in logs if r['level']!=s['level']]
    passed=sum(r['correct'] for r in logs)>=9 and sum(r['correct'] and r['hints']==0 for r in target)>=7 and all(r['correct'] for r in prior)
    s['level_attempts'].setdefault(str(s['level']),[]).append(sum(r['correct'] for r in logs))
    s['learning_sessions'].append({"level":s['level'],"correct":sum(r['correct'] for r in logs), "total":10,
          "passed":passed, "at":datetime.now(timezone.utc).isoformat()})
    s['learning_sessions']=s['learning_sessions'][-500:]
    if passed and s['level']<6: s['level']+=1
    begin_round(s)
    grant_badges(s)
    return passed

def submit_answer(s,answer):
    if s['mode']=='assessment': raise ValueError('진단 평가는 별도의 제출 함수를 사용합니다.')
    if not isinstance(answer,int) or isinstance(answer,bool) or answer<0: raise ValueError('0 이상의 정수를 입력하세요.')
    s=copy.deepcopy(s)
    q=tuple(s['question']); a,b=q
    level=int(s.get('question_level',s['level']))
    correct=(answer==a+b)
    mode=s['mode']
    if mode=='normal':
        ensure_ready(s)
        level=s['question_level'];q=tuple(s['question']);a,b=q;correct=(answer==a+b)
        hints=s['current_hints']
        record_attempt(s,level,q,answer,correct,hints,mode)
        s['round_log'].append({"level":level,"correct":correct,"hints":hints})
        s['count']=len(s['round_log']);s['correct']=sum(x['correct'] for x in s['round_log'])
        s['normal_total']+=1
        if correct:
            s['score']+=10;s['streak']+=1;s['best_streak']=max(s['best_streak'],s['streak'])
        else:
            add_wrong(s,a,b);s['streak']=0
        if s['count']>=10:
            passed=finish_round(s)
            msg='🏆 숙달 기준 통과! ' if passed else '🔄 숙달 기준 미충족: 현재 단계에서 다시 연습합니다. '
        else:
            next_level=s['round_plan'][s['count']]
            s['question_level']=next_level
            recent=[tuple(x) for x in s.get('recent',[])]
            s['question']=generate_problem(next_level,recent)
            s['recent']=(recent+[tuple(s['question'])])[-4:]
            s['current_hints']=0
            msg='🎉 정답!' if correct else f'📘 정답은 {a+b}. 오답노트에 기록했습니다.'
    elif mode=='review':
        idx=int(s['review_index'])
        hints=s['current_hints']
        record_attempt(s,level,q,answer,correct,hints,'review')
        if correct:
            s['wrong'].pop(idx);s['score']+=10;s['review_correct']+=1
            msg='✅ 오답 복습 성공!'
        else:
            s['wrong'][idx]['times']+=1
            msg=f'📘 정답은 {a+b}. 다시 복습합니다.'
        s['current_hints']=0
        if s['wrong']:
            s['review_index']=(idx+(0 if correct else 1))%len(s['wrong'])
            item=s['wrong'][s['review_index']]
            s['question']=(item['a'],item['b'])
            s['question_level']=infer_level(s['question'])
        else:
            begin_round(s);msg+=' 모든 오답을 해결했습니다.'
    elif mode=='remedial':
        record_attempt(s,level,q,answer,correct,s['current_hints'],'remedial')
        if correct: s['score']+=10
        else: add_wrong(s,a,b)
        s['remedial_count']+=1
        s['current_hints']=0
        if s['remedial_count']>=4:
            begin_round(s)
            msg='✅ 보충 훈련 완료! 일반 학습으로 돌아갑니다.'
        else:
            s['question'],s['question_level']=remedial_problem(s['remedial_skill'],s['remedial_count'])
            msg='✅ 잘했어요!' if correct else f'📘 정답은 {a+b}. 함께 다시 연습해요.'
    else: raise ValueError('알 수 없는 학습 모드입니다.')
    grant_badges(s)
    return s,msg

def infer_level(q):
    a,b=q
    if a>=10 or b>=10: return 6
    if a+b==10: return 3
    if a+b>10: return 4
    if a+b<=5: return 1
    return 2

def remedial_problem(skill,index):
    level=SKILLS.index(skill)+1
    if skill=='CARRY_ADD':
        # Scaffolding: 10-making -> add to 10 -> carry -> independent transfer.
        return [((8,2),3),((10,5),6),((8,7),4),((9,6),4)][index%4]
    prior=SKILLS.index(PREDECESSOR.get(skill,skill))+1
    requested=[prior,prior,level,level][index%4]
    return generate_problem(requested),requested

def begin_remedial(s):
    s=copy.deepcopy(s)
    skill=recommended_skill(s)
    if skill is None:
        return s,'ℹ️ 현재 단계의 취약 유형을 확정하기 위한 풀이 기록이 부족하거나 정답률이 양호합니다.'
    s['mode']='remedial';s['remedial_skill']=skill;s['remedial_count']=0
    s['question'],s['question_level']=remedial_problem(skill,0)
    s['current_hints']=0
    return s, f'🎯 {SKILL_NAMES[skill]} 개념을 보충하는 4문제 미션입니다.'

def begin_review(s):
    s=copy.deepcopy(s)
    if not s['wrong']: return s,'📒 복습할 오답이 없습니다.'
    s['mode']='review';s['review_index']=0;s['current_hints']=0
    item=s['wrong'][0];s['question']=(item['a'],item['b'])
    s['question_level']=infer_level(s['question'])
    return s,'📒 오답 복습을 시작합니다.'

def go_to_normal(s):
    s=copy.deepcopy(s);begin_round(s)
    return s,'🏰 일반 학습으로 돌아왔습니다. 현재 회차는 새로 시작합니다.'

def use_hint(s):
    s=copy.deepcopy(s)
    if s['mode']=='assessment':return s
    s['current_hints']=min(3,s.get('current_hints',0)+1)
    return s

def upgrade_record(data,version=3):
    if not isinstance(data,dict) or data.get('app')!='mathquest' or data.get('schema') not in (1,2,3):
        raise ValueError('Math Quest v06~v08 JSON 파일만 불러올 수 있습니다.')
    schema=data['schema']; raw=data.get('state')
    if not isinstance(raw,dict):raise ValueError('학습 상태가 없습니다.')
    if schema==1:
        # Use the original v06 validator for legacy structural checks.
        base=validate_record(data)
        s=new_state()
        for k in base:
            if k in s:s[k]=copy.deepcopy(base[k])
        s['mode']='normal' # v06 5-question partial progress cannot be converted to a 10-question round
        begin_round(s)
        return s
    s=new_state()
    for key,val in raw.items():
        if key in s:s[key]=copy.deepcopy(val)
    if not isinstance(s['level'],int) or not 1<=s['level']<=6:raise ValueError('레벨이 올바르지 않습니다.')
    if not isinstance(s['score'],int) or s['score']<0:raise ValueError('점수가 올바르지 않습니다.')
    if not isinstance(s['wrong'],list) or len(s['wrong'])>5000:raise ValueError('오답 기록이 너무 많습니다.')
    if not isinstance(s.get('skill_history'),list) or len(s['skill_history'])>3000:raise ValueError('학습 기록이 올바르지 않습니다.')
    for item in s['wrong']:
        if not isinstance(item,dict) or any(not isinstance(item.get(k),int) or item.get(k)<1 for k in ('a','b','times')):
            raise ValueError('오답 항목이 올바르지 않습니다.')
    if s['mode'] not in ('normal','review','remedial','assessment'):raise ValueError('학습 모드 오류')
    if s['mode']=='assessment' and (not s.get('assessment_items') or not 0<=s.get('assessment_index',-1)<len(s['assessment_items'])):
        begin_round(s)
    elif s['mode']=='normal' and not s.get('round_plan'):
        begin_round(s)
    else:
        if not isinstance(s['question'],(list,tuple)) or len(s['question'])!=2:raise ValueError('문제 형식 오류')
        s['question']=tuple(s['question'])
    return s

def as_record(s,version=3):
    state=copy.deepcopy(s)
    return {"app":"mathquest","schema":version,"saved_at":datetime.now(timezone.utc).isoformat(),"state":state}

# v08: balanced before/after item sets, scored only after all answers.
def assessment_pool(level, form):
    pool=candidates_for(level)
    # Deterministic pools, avoid exact same ordered questions when sufficient.
    if level==3:
        # 10-making has only 5 unique unordered combinations; alternate operand order.
        return [(b,a) if form=='post' else (a,b) for a,b in pool]
    rng=random.Random(801+level)
    rng.shuffle(pool)
    return pool[3:] if form=='post' else pool[:3]

def create_assessment(form):
    rng=random.Random(2027 if form=='pre' else 2028)
    items=[]
    for level in range(1,7):
        pool=assessment_pool(level,form)
        if len(pool)<3:raise RuntimeError('진단 문제은행 부족')
        for q in pool[:3]:items.append({'level':level,'a':q[0],'b':q[1]})
    rng.shuffle(items)
    return items

def begin_assessment(s,form):
    if form not in ('pre','post'): raise ValueError('잘못된 평가 유형')
    if form=='post' and not s.get('pretest'):raise ValueError('먼저 사전 진단을 완료하세요.')
    s=copy.deepcopy(s)
    s['mode']='assessment';s['assessment_form']=form
    s['assessment_items']=create_assessment(form)
    s['assessment_answers']=[];s['assessment_index']=0;s['current_hints']=0
    q=s['assessment_items'][0];s['question']=(q['a'],q['b']);s['question_level']=q['level']
    return s

def submit_assessment(s,answer):
    if not isinstance(answer,int) or isinstance(answer,bool) or answer<0:raise ValueError('0 이상의 정수를 입력하세요.')
    s=copy.deepcopy(s)
    if s['mode']!='assessment':raise ValueError('진단 평가 상태가 아닙니다.')
    idx=s['assessment_index']; q=s['assessment_items'][idx]
    s['assessment_answers'].append({'level':q['level'],'a':q['a'],'b':q['b'], 'answer':answer,
                                    'correct':answer==q['a']+q['b']})
    s['assessment_index']+=1
    if s['assessment_index']<len(s['assessment_items']):
        q=s['assessment_items'][s['assessment_index']]
        s['question']=(q['a'],q['b']);s['question_level']=q['level']
        return s,'답안이 저장되었습니다. 다음 문제를 풀어 주세요.'
    answers=s['assessment_answers']
    results={str(lvl):sum(r['correct'] for r in answers if r['level']==lvl) for lvl in range(1,7)}
    record={'total':len(answers),'correct':sum(r['correct'] for r in answers), 'by_level':results,
            'answers':copy.deepcopy(answers),'completed_at':datetime.now(timezone.utc).isoformat()}
    form=s['assessment_form'];s['pretest' if form=='pre' else 'posttest']=record
    # 3 items are a screening tool only, do not assign definitive mastery.
    if form=='pre':
        start=next((lvl for lvl in range(1,7) if results[str(lvl)]<3),6)
        s['suggested_level']=start
        s['level']=start
    begin_round(s)
    s['assessment_items']=[];s['assessment_answers']=[];s['assessment_index']=0;s['assessment_form']=None
    return s,f"✅ {'사전' if form=='pre' else '사후'} 평가 완료: {record['correct']}/18 정답."

def report_rows(s):
    pre=s.get('pretest');post=s.get('posttest')
    return [{'level':i,'concept':LEVELS[i-1][0],
             'pre_correct':None if not pre else pre['by_level'].get(str(i)),
             'post_correct':None if not post else post['by_level'].get(str(i))} for i in range(1,7)]

def csv_report(s):
    stream=io.StringIO()
    writer=csv.writer(stream)
    writer.writerow(['level','concept','pre_correct_out_of_3','post_correct_out_of_3'])
    for row in report_rows(s):
        writer.writerow([row['level'],row['concept'],row['pre_correct'],row['post_correct']])
    return '\ufeff'+stream.getvalue()


def html_report(s):
    pre=s.get('pretest');post=s.get('posttest')
    if not pre:raise ValueError('먼저 사전 평가가 필요합니다.')
    rows=''.join('<tr><td>{}</td><td>{}</td><td>{}/3</td><td>{}</td></tr>'.format(
        r['level'],html.escape(r['concept']),r['pre_correct'],
        '미실시' if r['post_correct'] is None else str(r['post_correct'])+'/3') for r in report_rows(s))
    improvement='미실시' if not post else '{:+.1f}%p'.format((post['correct']-pre['correct'])/18*100)
    return '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Math Quest 학습 결과</title>
<style>body{{font-family:Arial,'Malgun Gothic',sans-serif;max-width:780px;margin:36px auto;color:#24344e;padding:20px}}h1{{color:#245c88}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ccd5e2;padding:10px;text-align:left}}.note{{background:#eef5ff;padding:15px;border-radius:10px}}</style>
</head><body><h1>Math Quest · 개인별 학습 결과</h1>
<p>사전 평가: {}/18 &nbsp;|&nbsp; 사후 평가: {} &nbsp;|&nbsp; 정답률 변화: {}</p>
<h2>개념별 평가 결과</h2><table><tr><th>단계</th><th>학습 개념</th><th>사전</th><th>사후</th></tr>{}</table>
<p class="note">이 결과는 개인의 평가 점수 변화를 나타내며, 교육적 효과의 인과적 증거는 아닙니다. 각 개념별 문항은 3개로 제한됩니다.</p></body></html>'''.format(pre['correct'], ('미실시' if not post else str(post['correct'])+'/18'),improvement,rows)
