<script setup>
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const mobileMenuOpen = ref(false);

const user = computed(() => {
  const storedUser = localStorage.getItem("authUser");

  if (!storedUser) {
    return null;
  }

  try {
    return JSON.parse(storedUser);
  } catch {
    return null;
  }
});

const links = [
  {
    label: "Dashboard",
    routeName: "dashboard",
  },
  {
    label: "Problems",
    routeName: "problems",
  },
  {
    label: "Daily Target",
    routeName: "daily-targets",
  },
  {
    label: "Revision",
    routeName: "revision",
  },
  {
    label: "Weak Topics",
    routeName: "weak-topics",
  },
];

function isActive(routeName) {
  return route.name === routeName;
}

function closeMenu() {
  mobileMenuOpen.value = false;
}

async function logout() {
  localStorage.removeItem("authToken");
  localStorage.removeItem("authUser");

  mobileMenuOpen.value = false;

  await router.replace({
    name: "login",
  });
}
</script>

<template>
  <header class="navbar">
    <div class="navbar__inner">
      <RouterLink
        :to="{ name: 'dashboard' }"
        class="navbar__brand"
        @click="closeMenu"
      >
        <span class="navbar__brand-mark">CP</span>

        <span class="navbar__brand-text">
          <strong>Coding Performance</strong>
          <small>Analytics Dashboard</small>
        </span>
      </RouterLink>

      <button
        class="navbar__toggle"
        type="button"
        aria-label="Toggle navigation menu"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <div
        class="navbar__content"
        :class="{ 'navbar__content--open': mobileMenuOpen }"
      >
        <nav class="navbar__links">
          <RouterLink
            v-for="link in links"
            :key="link.routeName"
            :to="{ name: link.routeName }"
            class="navbar__link"
            :class="{
              'navbar__link--active': isActive(link.routeName),
            }"
            @click="closeMenu"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <div class="navbar__account">
          <span
            v-if="user?.email"
            class="navbar__email"
          >
            {{ user.email }}
          </span>

          <button
            type="button"
            class="button button--danger-outline button--small"
            @click="logout"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </header>
</template>