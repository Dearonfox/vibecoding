<template>
  <div class="dashboard">
    <section class="card">
      <h2>오늘 주문 현황</h2>
      <p>실시간 주문 목록과 상태 관리 영역입니다.</p>
    </section>
    <section class="card">
      <h2>매출 정산</h2>
      <p>일별/월별 판매 금액 정산 페이지가 들어올 영역입니다.</p>
    </section>
    <section class="card">
      <h2>AI 신메뉴 추천</h2>
      <p>신메뉴 추천 결과와 추천 사유를 표시할 영역입니다.</p>
    </section>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.card {
  min-height: 220px;
  border-radius: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 24px rgba(24, 39, 75, 0.08);
}

@media (max-width: 960px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
}
</style>
