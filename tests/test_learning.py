import copy
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import learning as L

def setup():
    s=L.new_state();L.begin_round(s);return s

def test_level_pools_and_hints():
    for lvl in range(1,7):
        for _ in range(20):
            a,b=L.generate_problem(lvl)
            assert (a,b) in L.candidates_for(lvl)
    assert '10' in L.hint_text(4,8,7,1)
    assert '15' in L.hint_text(4,8,7,3)
    s=setup();s=L.use_hint(s);assert s['current_hints']==1

def test_normal_round_pass_and_fail():
    s=setup()
    for i in range(10):
        a,b=s['question'];s,msg=L.submit_answer(s,a+b)
    assert s['level']==2
    assert s['level_attempts']['1']==[10]
    assert s['score']==100
    s=setup()
    for i in range(10):
        s,msg=L.submit_answer(s,999)
    assert s['level']==1
    assert s['level_attempts']['1']==[0]
    assert len(s['wrong'])>=1

def test_hints_not_counted_for_independent_mastery():
    s=setup()
    for i in range(10):
        if i<5:s=L.use_hint(s)
        a,b=s['question'];s,_=L.submit_answer(s,a+b)
    assert s['level']==1

def test_remedial_flow_and_review():
    s=setup()
    for _ in range(5):s,_=L.submit_answer(s,999)
    assert L.recommended_skill(s)==L.skill_for(1)
    s,msg=L.begin_remedial(s)
    assert s['mode']=='remedial'
    for _ in range(4):
        a,b=s['question'];s,_=L.submit_answer(s,a+b)
    assert s['mode']=='normal'
    s,msg=L.begin_review(s)
    assert s['mode']=='review'
    while s['mode']=='review':
        a,b=s['question'];s,_=L.submit_answer(s,a+b)
    assert not s['wrong']

def test_legacy_json_import():
    old=L.initial_state();old['level']=3;old['score']=70
    old['wrong']=[{'a':8,'b':7,'times':2}];old['badges']=['🌱 첫걸음']
    blob={'app':'mathquest','schema':1,'state':json.loads(json.dumps(old))}
    loaded=L.upgrade_record(blob)
    assert loaded['level']==3 and loaded['score']==70
    assert loaded['wrong']==old['wrong'] and loaded['badges']==old['badges']
    assert loaded['count']==0 and len(loaded['round_plan'])==10
    restored=L.upgrade_record(json.loads(json.dumps(L.as_record(loaded,2))))
    assert restored['score']==70

def test_assessment_and_reports():
    s=setup();s=L.begin_assessment(s,'pre')
    assert len(s['assessment_items'])==18
    assert len([x for x in s['assessment_items'] if x['level']==3])==3
    for i in range(18):
        a,b=s['question'];s,msg=L.submit_assessment(s,a+b)
    assert s['pretest']['correct']==18
    assert s['mode']=='normal'
    s=L.begin_assessment(s,'post')
    for i in range(18):s,msg=L.submit_assessment(s,0)
    assert s['posttest']['correct']==0
    assert 'level,concept' in L.csv_report(s)
    assert '개인별 학습 결과' in L.html_report(s)
    assert L.report_rows(s)[0]['pre_correct']==3
    assert L.report_rows(s)[0]['post_correct']==0
    assert len(L.create_assessment('pre'))==18
    assert L.create_assessment('pre')!=L.create_assessment('post')
    blob=json.loads(json.dumps(L.as_record(s,3)))
    re=L.upgrade_record(blob)
    assert re['posttest']['correct']==0

def test_wrong_two_digit_order():
    s=setup()
    L.add_wrong(s,23,6)
    assert s['wrong'][-1]['a']==23
