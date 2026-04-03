<template>
  <div class="app-shell">
    <header class="hero">
      <h1>Restaurant Customer Web</h1>
      <p>카테고리 기반 메뉴 조회와 장바구니 주문을 위한 고객용 앱 시작점입니다.</p>
    </header>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style>
:root {
  color: #1f2937;
  background: linear-gradient(180deg, #fff8ef 0%, #f4efe7 100%);
  font-family: "Segoe UI", sans-serif;
}

body {
  margin: 0;
}

.app-shell {
  min-height: 100vh;
}

.hero {
  padding: 32px 24px 16px;
  background: #8d4b32;
  color: #fff8ef;
}

.hero h1 {
  margin: 0 0 8px;
}

.content {
  padding: 24px;
}
</style>
