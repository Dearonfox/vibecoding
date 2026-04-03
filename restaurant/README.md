# Restaurant Platform

식당 주문/관리 플랫폼의 모노레포 초안이다.

## 구성

- `frontend/customer-web`: 고객용 Vue 3 + Vite 앱
- `frontend/admin-web`: 관리자용 Vue 3 + Vite 앱
- `backend/gateway-service`: API Gateway
- `backend/auth-service`: 인증 서비스
- `backend/menu-service`: 메뉴 서비스
- `backend/order-service`: 주문 서비스
- `backend/review-service`: 후기 서비스
- `ai-backend/ai-gateway`: FastAPI 기반 AI 게이트웨이
- `infra/compose/docker-compose.local.yml`: 로컬 실행용 Compose
- `docs/`: 설계 문서

## 문서

- `docs/msa-architecture.md`
- `docs/service-architecture.md`

## 빠른 시작

1. `.env.example`을 참고해 `.env`를 준비한다.
2. Docker Compose로 Redis와 백엔드를 함께 띄운다.
3. 프론트는 각 폴더에서 개발 서버를 실행한다.

## 현재 상태

현재는 MVP 시작용 스캐폴딩이 포함되어 있다.

- 서비스별 디렉터리 구조
- 기본 엔드포인트
- Dockerfile 및 Compose 초안
- 공통 환경 변수 예시

## 다음 추천 작업

1. 인증/JWT 실제 구현
2. SQLite 연결 및 엔티티 설계
3. 프론트 화면 라우팅 및 상태 관리
4. AI 프롬프트와 moderation 로직 구현
