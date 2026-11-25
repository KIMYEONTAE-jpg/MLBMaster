# BASEBALL MASTER - MLB 야구 도감

업로드된 Tkinter 프로그램을 바탕으로 Windows EXE 배포판과 브라우저용 웹판을 함께 구성했습니다.

## 구성
- `baseball_master.py`: 기존 Tkinter 데스크톱 앱
- `app.py`: Streamlit 웹 앱
- `baseball_content.py`: 원본 프로그램의 역사·기술·규칙·용어·구단 데이터
- `.github/workflows/build-windows-exe.yml`: GitHub Actions Windows EXE 자동 빌드
- `requirements.txt`: 웹 앱 실행 패키지

## 1. Windows EXE 만들기
1. 이 폴더의 파일 전체를 GitHub 저장소에 업로드합니다.
2. GitHub 저장소의 Actions 탭에서 `Build Windows EXE`를 선택합니다.
3. `Run workflow`를 눌러 실행합니다.
4. 완료된 작업을 열어 `BASEBALL_MASTER-Windows` artifact를 다운로드합니다.
5. ZIP을 풀고 `BASEBALL_MASTER.exe`를 실행합니다.

버전 태그를 `v1.0.0`처럼 만들어 push하면 GitHub Releases에도 EXE가 자동 첨부됩니다.

## 2. 웹 버전 배포
Streamlit Community Cloud를 사용합니다. GitHub에 저장소를 올린 뒤 https://share.streamlit.io/ 에서 로그인하고 저장소·브랜치·`app.py`를 지정해 배포합니다. 배포가 끝나면 공유 가능한 웹 주소가 발급됩니다.

웹 앱은 GitHub Pages 자체에서 직접 실행되는 정적 페이지가 아니라, GitHub에 소스를 보관하고 Streamlit Cloud가 Python 앱을 실행하는 구조입니다.

## 3. 내 PC에서 웹 버전 실행
Windows에서 Python 3.10 이상을 설치한 뒤 `실행_웹버전_로컬.bat`을 실행합니다.

## 데이터 관련 안내
연도별 수상 기록과 시즌 리더는 원본 Tkinter 앱과 동일하게 Lahman 데이터 CSV 미러를 인터넷으로 읽습니다. 원본 코드에 적힌 미러 주소를 유지했습니다. 미러의 가용성·갱신 시점·수록 범위는 보장되지 않으며 MLB 공식 데이터와 완전히 동일하다고 볼 수 없습니다. 특히 타율 리더는 원본 프로그램의 계산 기준인 100타수 이상 참고값을 사용하며 공식 규정타석과 다를 수 있습니다.

## 참고
- MLB Awards: https://www.mlb.com/awards
- SABR Lahman Database: https://sabr.org/lahman-database/
- Lahman CSV mirror used by original source: https://github.com/cbwinslow/lahman-database-csv

## 주의
GitHub Actions에서 EXE를 실제 빌드하려면 이 폴더를 본인 GitHub 저장소에 업로드하고 Actions 실행 권한을 허용해야 합니다. 현재 제공되는 ZIP에는 EXE 바이너리가 포함되어 있지 않습니다. Windows 실행 파일은 GitHub의 Windows 빌드 환경에서 생성됩니다.
