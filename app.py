"""Math Quest v08 — Streamlit Community Cloud entry point."""
import json
import html
import streamlit as st
import learning as L

VERSION = '08'
IS_V08 = VERSION == '08'
st.set_page_config(page_title=f'Math Quest v{VERSION}',page_icon='🏰', layout='wide')
st.markdown("""<style>
.block-container{max-width:1080px;padding-top:1.3rem}
/* Streamlit 기본 통계도 현재 테마의 글자색을 사용하도록 설정 */
[data-testid="stMetric"]{background:var(--secondary-background-color);padding:12px;border-radius:12px;border:1px solid rgba(125,137,155,.18)}
[data-testid="stMetric"] [data-testid="stMetricValue"],
[data-testid="stMetric"] [data-testid="stMetricLabel"]{color:var(--text-color)!important}
.mq-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:12px 0 20px}
.mq-stat{background:#eff5ff;color:#172b4d;border:1px solid #c8d8f4;border-radius:16px;padding:16px 18px;min-height:104px;box-shadow:0 2px 9px rgba(24,54,95,.05)}
.mq-stat-label{color:#435778;font-size:15px;font-weight:700;margin-bottom:9px}
.mq-stat-number{color:#102342!important;font-size:31px;font-weight:800;line-height:1.15;font-variant-numeric:tabular-nums}
.mq-stat:nth-child(2){background:#e9f8f0;border-color:#b3dfc5}
.mq-stat:nth-child(3){background:#fff5e7;border-color:#f2d6a7}
@media(max-width:640px){.mq-stats{gap:7px}.mq-stat{padding:12px 9px;min-height:88px}.mq-stat-label{font-size:12px}.mq-stat-number{font-size:22px}}
div.stButton>button {border-radius:12px}
.quest{background:linear-gradient(115deg,#e1f8ed,#e3edff);color:#22324b;padding:20px 28px;border-radius:20px;text-align:center;margin-bottom:10px}
.quest h1{font-size:2.3rem;margin:8px}
.worlds{display:flex;flex-wrap:wrap;gap:10px}.world{flex:1;min-width:120px;border-radius:13px;padding:12px;text-align:center;background:#eef1f5;color:#22324b}
</style>""",unsafe_allow_html=True)

if 'mq' not in st.session_state:
    s=L.new_state();L.begin_round(s);st.session_state.mq=s
if 'mq_note' not in st.session_state:st.session_state.mq_note='수학 왕국 탐험을 시작해 보세요!'
s=st.session_state.mq

def replace(state,note):
    st.session_state.mq=state
    st.session_state.mq_note=note
    st.rerun()

def app_question(s):
    a,b=s['question'];level=s.get('question_level',s['level'])
    assessment=s['mode']=='assessment'
    mode_label={'normal':'🏰 단계별 학습','review':'📒 오답 복습','remedial':'🎯 맞춤 보충','assessment':'📝 사전·사후 평가'}[s['mode']]
    if assessment:
        progress=f"{s['assessment_index']+1} / 18 문제"
    elif s['mode']=='normal':
        progress=f"{s['count']+1} / 10 문제"
    elif s['mode']=='remedial':
        progress=f"{s['remedial_count']+1} / 4 문제"
    else:
        progress=f"오답 {len(s['wrong'])}개 남음"
    st.markdown(f'<div class="quest"><div>{mode_label} · {html.escape(progress)}</div><h1>{a} + {b} = ?</h1><div>⭐ 단계 {level} · {html.escape(L.LEVELS[level-1][0])}</div></div>',unsafe_allow_html=True)
    if not assessment:
        hints=int(s.get('current_hints',0))
        cols=st.columns([2,1])
        with cols[0]:
            for h in range(1,hints+1):
                st.info(f'💡 힌트 {h}: {L.hint_text(level,a,b,h)}')
            if hints>=2 and a<10 and b<10:
                st.caption(L.hint_dots(a,b))
        with cols[1]:
            if st.button('💡 다음 힌트',disabled=hints>=3,use_container_width=True):
                replace(L.use_hint(s),'힌트를 참고하여 문제를 풀어 보세요.')
    with st.form(f"answer_{s['mode']}",clear_on_submit=True):
        answer=st.number_input('정답 입력',min_value=0,max_value=9999,step=1,value=None,placeholder='숫자를 입력하세요')
        submitted=st.form_submit_button('✅ 정답 제출',type='primary',use_container_width=True)
    if submitted:
        if answer is None:
            st.warning('정답을 입력해 주세요.')
        else:
            try:
                if assessment:
                    ns,msg=L.submit_assessment(s,int(answer))
                else:
                    ns,msg=L.submit_answer(s,int(answer))
                replace(ns,msg)
            except (ValueError,IndexError,KeyError) as e:
                st.error(f'처리 오류: {e}')

st.title(f'🎮 Math Quest v{VERSION}')
st.caption('단계별 수학 학습 · 오답 분석 · 맞춤형 보충 · 힌트 · 배지 · 모험 지도' + (' · 사전·사후 평가' if IS_V08 else ''))
st.markdown(
    f"""<section class="mq-stats" aria-label="학습 현황">
      <div class="mq-stat"><div class="mq-stat-label">🏰 현재 레벨</div><div class="mq-stat-number">{s['level']} <span style="font-size:.6em;color:#51617a">/ 6</span></div></div>
      <div class="mq-stat"><div class="mq-stat-label">⭐ 누적 점수</div><div class="mq-stat-number">{s['score']:,}</div></div>
      <div class="mq-stat"><div class="mq-stat-label">📒 남은 오답</div><div class="mq-stat-number">{len(s['wrong'])}</div></div>
    </section>""", unsafe_allow_html=True
)
with st.sidebar:
    st.header('🧭 모험 메뉴')
    st.caption(f"현재 레벨 {s['level']} / 6 · 점수 {s['score']:,} · 오답 {len(s['wrong'])}개")
    mode=s['mode']
    if mode=='assessment':
        st.warning('진단 평가 중에는 다른 학습 모드로 이동할 수 없습니다.')
    else:
        if st.button('🏰 일반 학습',use_container_width=True):
            replace(*L.go_to_normal(s))
        if st.button('📒 오답 복습',use_container_width=True):
            replace(*L.begin_review(s))
        if st.button('🎯 맞춤 보충 미션',use_container_width=True):
            replace(*L.begin_remedial(s))
    st.divider()
    st.caption('기록은 서버에 자동 저장되지 않습니다. 아래 저장 메뉴에서 JSON 파일을 다운로드하세요.')

if IS_V08 and s['mode']!='assessment':
    with st.expander('📝 사전·사후 학습 평가',expanded=s.get('pretest') is None):
        st.write('평가별 18문제(6단계 × 3문제). 평가 도중에는 힌트와 즉시 정답 공개가 없습니다.')
        b1,b2=st.columns(2)
        with b1:
            if st.button('사전 평가 시작',disabled=s.get('pretest') is not None,use_container_width=True):
                replace(L.begin_assessment(s,'pre'),'사전 평가를 시작합니다. 정답은 평가 종료 후 확인합니다.')
        with b2:
            if st.button('사후 평가 시작',disabled=s.get('pretest') is None or s.get('posttest') is not None,use_container_width=True):
                replace(L.begin_assessment(s,'post'),'사후 평가를 시작합니다. 정답은 평가 종료 후 확인합니다.')
        if s.get('pretest') and not s.get('posttest'):
            st.caption(f"사전 평가: {s['pretest']['correct']}/18 · 추천 시작 단계: {s.get('suggested_level',s['level'])}")
        if s.get('posttest'):
            st.success('사전·사후 평가가 완료되었습니다. 성장 분석 탭에서 결과를 확인하세요.')

st.info(st.session_state.mq_note)
app_question(s)
st.divider()
sections=['📒 오답노트','🏅 배지','🗺️ 모험 지도','📊 학습·진단 분석','💾 저장·복원']
tabs=st.tabs(sections)
with tabs[0]:
    st.markdown(L.show_wrong(s))
    if s.get('skill_history'):
        st.subheader('개념별 최근 학습')
        for skill in L.SKILLS:
            acc,n=L.accuracy_for_skill(s,skill)
            if n:
                st.write(f"**{L.SKILL_NAMES[skill]}:** 최근 {n}문제 중 {round(acc*n)}문제 정답 ({acc:.0%})" + (' — 보충 권장' if n>=5 and acc<0.8 else ''))
with tabs[1]:
    st.markdown(L.show_badges(s),unsafe_allow_html=True)
with tabs[2]:
    st.markdown(L.show_map(s),unsafe_allow_html=True)
with tabs[3]:
    st.subheader('학습 진행 요약')
    st.metric('총 일반 학습 문제',s['normal_total'])
    st.metric('최고 연속 정답',s['best_streak'])
    records=s.get('learning_sessions',[])
    if records:
        st.bar_chart({f"도전 {i+1} · Lv{r['level']}":r['correct'] for i,r in enumerate(records[-12:])},horizontal=True,x_label='정답 개수 (10문제)')
    elif s.get('level_attempts'):
        st.write('이전 v06에서 가져온 기록 (한 회차 5문제 기준):')
        st.json(s['level_attempts'],expanded=False)
    else:
        st.caption('10문제 회차를 마치면 학습 기록이 표시됩니다.')
    if IS_V08:
        st.divider()
        st.subheader('📈 사전·사후 진단 결과')
        pre,post=s.get('pretest'),s.get('posttest')
        if not pre:
            st.info('사전 진단을 완료하면 결과가 표시됩니다.')
        else:
            c1,c2,c3=st.columns(3)
            c1.metric('사전 정답률',f"{pre['correct']/18:.1%}")
            c2.metric('사후 정답률',f"{post['correct']/18:.1%}" if post else '미실시')
            c3.metric('향상 폭',f"{(post['correct']-pre['correct'])/18*100:+.1f}%p" if post else '—')
            rows=L.report_rows(s)
            st.dataframe([{'레벨':r['level'],'학습 개념':r['concept'],'사전 정답 수':r['pre_correct'],'사후 정답 수':r['post_correct']} for r in rows],hide_index=True,use_container_width=True)
            if post:
                chart={f"레벨 {r['level']}":{'사전':r['pre_correct']/3*100,'사후':r['post_correct']/3*100} for r in rows}
                st.bar_chart(chart,y_label='정답률 (%)',x_label='학습 단계')
            st.download_button('📊 학습 결과 CSV 다운로드',data=L.csv_report(s),file_name='mathquest_learning_report.csv',mime='text/csv',use_container_width=True)
            st.download_button('🧾 학습 결과 HTML 보고서',data=L.html_report(s).encode('utf-8'),file_name='mathquest_learning_report.html',mime='text/html',use_container_width=True)
            st.caption('이 분석은 학습 전후 성적 변화의 기술적 비교이며, 앱의 인과적 교육 효과를 입증하지는 않습니다.')
with tabs[4]:
    st.subheader('💾 JSON 학습 기록')
    st.download_button('⬇️ 현재 기록 다운로드',data=json.dumps(L.as_record(s,3 if IS_V08 else 2),ensure_ascii=False,indent=2),file_name=f'mathquest_v{VERSION}_record.json',mime='application/json',use_container_width=True)
    uploaded=st.file_uploader('v06·v07·v08 JSON 기록 가져오기',type=['json'])
    if st.button('📂 기록 불러오기',disabled=uploaded is None,use_container_width=True):
        try:
            if uploaded.size>2_000_000:raise ValueError('2MB 이하의 파일만 허용합니다.')
            record=json.loads(uploaded.getvalue().decode('utf-8'))
            if record.get('schema')==3 and not IS_V08:
                st.warning('v08 평가 기록은 v07에서 일부 보존할 수 없습니다. v08에서 불러오세요.')
            else:
                loaded=L.upgrade_record(record,version=3 if IS_V08 else 2)
                replace(loaded,'✅ 이전 학습 기록을 불러왔습니다.')
        except (ValueError,UnicodeDecodeError,TypeError,KeyError,IndexError,AttributeError) as e:
            st.error(f'불러오기 실패: {e}')
    st.caption('v06 기록은 레벨·점수·오답·배지를 보존합니다. v06의 진행 중인 5문제 회차는 v07의 10문제 회차로 새로 시작합니다.')
