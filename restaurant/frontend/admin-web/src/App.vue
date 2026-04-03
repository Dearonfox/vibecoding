<template>
  <div class="app-shell">
    <header class="hero">
      <h1>Restaurant Admin Web</h1>
      <p>주문 조회, 메뉴 관리, 정산 페이지를 위한 관리자용 앱 시작점입니다.</p>
    </header>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style>
:root {
  color: #14213d;
  background: linear-gradient(180deg, #f7f4ef 0%, #e7ebf2 100%);
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
  background: #25344f;
  color: #f8fafc;
}

.hero h1 {
  margin: 0 0 8px;
}

.content {
  padding: 24px;
}
</style>
