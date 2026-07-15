<script setup>
import {
  computed,
  reactive,
  ref,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../api/axios";

const route = useRoute();
const router = useRouter();

const form = reactive({
  email: "",
  password: "",
});

const loading = ref(false);
const errorMessage = ref("");

const registrationMessage = computed(() => {
  if (route.query.registered === "true") {
    return "Registration successful. Log in using your new account.";
  }

  return "";
});

async function submitLogin() {
  errorMessage.value = "";
  loading.value = true;

  try {
    const response = await api.post(
      "/login",
      {
        email: form.email.trim(),
        password: form.password,
      },
    );

    const token =
      response.data.data.authentication_token;

    const user =
      response.data.data.user;

    localStorage.setItem(
      "authToken",
      token,
    );

    localStorage.setItem(
      "authUser",
      JSON.stringify(user),
    );

    const redirectPath =
      typeof route.query.redirect === "string"
        ? route.query.redirect
        : "/dashboard";

    await router.replace(redirectPath);
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Login failed. Check your credentials and try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-layout">
      <div class="auth-introduction">
        <span class="eyebrow">Placement preparation</span>

        <h1>
          Turn coding practice into measurable progress.
        </h1>

        <p>
          Track solved problems, attempts, revision stages,
          weak topics and daily targets from a single
          dashboard.
        </p>

        <div class="auth-feature-list">
          <div>
            <strong>Topic analytics</strong>
            <span>Identify strengths and weak areas.</span>
          </div>

          <div>
            <strong>Daily targets</strong>
            <span>Build a consistent coding routine.</span>
          </div>

          <div>
            <strong>Revision tracking</strong>
            <span>Convert solved problems into mastery.</span>
          </div>
        </div>
      </div>

      <div class="auth-card">
        <div class="auth-card__header">
          <span class="navbar__brand-mark">CP</span>

          <div>
            <h2>Student Login</h2>
            <p>Access your coding analytics dashboard.</p>
          </div>
        </div>

        <div
          v-if="registrationMessage"
          class="alert alert--success"
        >
          {{ registrationMessage }}
        </div>

        <div
          v-if="errorMessage"
          class="alert alert--error"
        >
          {{ errorMessage }}
        </div>

        <form
          class="form"
          @submit.prevent="submitLogin"
        >
          <div class="form-group">
            <label for="login-email">
              Email address
            </label>

            <input
              id="login-email"
              v-model.trim="form.email"
              type="email"
              autocomplete="email"
              placeholder="student@example.com"
              required
            />
          </div>

          <div class="form-group">
            <label for="login-password">
              Password
            </label>

            <input
              id="login-password"
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            class="button button--primary button--full"
            type="submit"
            :disabled="loading"
          >
            {{
              loading
                ? "Signing in..."
                : "Login"
            }}
          </button>
        </form>

        <div class="demo-login-box">
          <strong>Demo account</strong>
          <span>Email: student@example.com</span>
          <span>Password: student123</span>
        </div>

        <p class="auth-card__footer">
          Do not have an account?

          <RouterLink :to="{ name: 'register' }">
            Register here
          </RouterLink>
        </p>
      </div>
    </div>
  </section>
</template>