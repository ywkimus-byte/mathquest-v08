# Math Quest v08 — Streamlit 배포용

초등 수학 덧셈 학습 앱입니다. 이전 버전(v06, v07)의 레벨·오답·배지·학습 기록을 가져올 수 있습니다.

## 이번 버전의 개선점

- **현재 레벨 / 누적 점수 / 남은 오답**을 앱 본문 상단의 고대비 카드로 표시합니다. 밝은 테마·어두운 테마에서 글자가 잘 보이도록 카드의 배경색과 글자색을 지정했습니다.
- v07: 6단계 덧셈, 개념별 오답 분석, 맞춤형 4문제 보충 미션, 3단계 힌트, 10문제 숙달 판정.
- v08: 총 18문항 사전 평가, 총 18문항 사후 평가, 레벨별 성장 그래프, CSV/HTML 보고서.
- 기존의 오답 복습, 배지, 모험 지도, JSON 기록 저장/복원 유지.

## GitHub 업로드

기존 `mathquest-v07` 저장소를 유지하려면 **새 저장소 `mathquest-v08`**을 만들고 이 폴더의 다음 파일을 업로드하세요.

```text
app.py
learning.py
requirements.txt
README.md
tests/test_learning.py
```

중요: `app.py`와 `learning.py`는 저장소 **최상위(동일한 폴더)**에 있어야 합니다.

## Streamlit Community Cloud

1. https://share.streamlit.io 에 로그인합니다.
2. Create app → GitHub 저장소에서 앱 배포를 선택합니다.
3. Repository: `<GitHub 계정>/mathquest-v08` / Branch: `main` / Main file path: `app.py`.
4. Deploy를 누르고 생성된 URL에서 앱 기능을 확인합니다.

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 자동 테스트

```bash
pip install pytest
python -m pytest tests -q
```

## 주의사항

- 앱의 현재 학습 상태는 접속한 브라우저 세션에 임시로 유지됩니다. **학습 후 JSON 파일을 내려받고 나중에 다시 업로드**하세요.
- 사전·사후 평가의 정답률 비교는 교육적 효과를 인과적으로 입증하는 자료가 아닙니다.
- 앱은 정식 학생 계정이나 서버 데이터베이스를 제공하지 않습니다. 개인 식별정보를 공개 GitHub에 업로드하지 마세요.
