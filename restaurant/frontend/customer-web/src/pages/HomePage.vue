<script setup lang="ts">
const categories = ["한식", "중식", "일식", "분식", "음료"];
const cart = [
  { name: "김치볶음밥", quantity: 1, price: 9000 },
  { name: "제육덮밥", quantity: 2, price: 10000 }
];
</script>

<template>
  <div class="layout">
    <aside class="sidebar">
      <h2>카테고리</h2>
      <button v-for="category in categories" :key="category" class="category-button">
        {{ category }}
      </button>
    </aside>

    <section class="panel">
      <h2>메뉴 목록</h2>
      <p>선택한 카테고리의 메뉴가 이 영역에 표시됩니다.</p>
      <div class="placeholder-card">
        메뉴 API와 연결되면 실데이터가 노출됩니다.
      </div>
    </section>

    <section class="panel">
      <h2>장바구니</h2>
      <ul class="cart-list">
        <li v-for="item in cart" :key="item.name">
          {{ item.name }} x {{ item.quantity }} / {{ item.price.toLocaleString() }}원
        </li>
      </ul>
      <button class="order-button">주문하기</button>
    </section>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  grid-template-columns: 220px 1fr 320px;
  gap: 20px;
}

.sidebar,
.panel {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  padding: 20px;
  box-shadow: 0 12px 30px rgba(74, 44, 27, 0.08);
}

.category-button,
.order-button {
  width: 100%;
  margin-top: 10px;
  border: 0;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
}

.category-button {
  background: #f1dfcf;
}

.order-button {
  background: #8d4b32;
  color: white;
}

.placeholder-card {
  margin-top: 16px;
  padding: 20px;
  border-radius: 14px;
  background: #fff5ea;
}

.cart-list {
  padding-left: 18px;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>
