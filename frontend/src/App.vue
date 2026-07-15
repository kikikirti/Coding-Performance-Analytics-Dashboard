<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

import Navbar from "./components/Navbar.vue";

const route = useRoute();

const showNavbar = computed(() => {
  return Boolean(route.meta.requiresAuth);
});
</script>

<template>
  <div class="app-shell">
    <Navbar v-if="showNavbar" />

    <main
      class="main-content"
      :class="{ 'main-content--auth': !showNavbar }"
    >
      <RouterView />
    </main>
  </div>
</template>