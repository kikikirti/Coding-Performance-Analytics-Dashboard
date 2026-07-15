<script setup>
import {
  reactive,
  ref,
} from "vue";

import { useRouter } from "vue-router";

import api from "../api/axios";

const router = useRouter();

const form = reactive({
  email: "",
  password: "",
  confirmPassword: "",
});

const loading = ref(false);
const errorMessage = ref("");
const fieldErrors = ref({});

async function submitRegistration() {
  errorMessage.value = "";
  fieldErrors.value = {};

  if (form.password !== form.confirmPassword) {
    fieldErrors.value = {
      confirmPassword: [
        "Password confirmation does not match.",
      ],
    };

    return;
  }

  loading.value = true;

  try {
    await api.post(
      "/register",
      {
        email: form.email.trim(),
        password: form.password,
      },
    );

    await router.replace({
      name: "login",
      query: {
        registered: "true",
      },
    });
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Registration failed.";

    fieldErrors.value =
      error.response?.data?.errors || {};
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section class="auth-page">
    <div class="auth-layout auth-layout--register">
      <div class="auth-introduction">
        <span class="eyebrow">Create your account</span>

        <h1>
          Build a structured placement preparation system.
        </h1>

        <p>
          Store coding problems from multiple platforms,
          monitor topic-wise progress and plan revision using
          real performance data.
        </p>
      </div>

      <div class="auth-card">
        <div class="auth-card__header">
          <span class="navbar__brand-mark">CP</span>

          <div>
            <h2>Student Registration</h2>
            <p>Create a new dashboard account.</p>
          </div>
        </div>

        <div
          v-if="errorMessage"
          class="alert alert--error"
        >
          {{ errorMessage }}
        </div>

        <form
          class="form"
          @submit.prevent="submitRegistration"
        >
          <div class="form-group">
            <label for="register-email">
              Email address
            </label>

            <input
              id="register-email"
              v-model.trim="form.email"
              type="email"
              autocomplete="email"
              placeholder="student@example.com"
              required
            />

            <small
              v-if="fieldErrors.email"
              class="form-error"
            >
              {{ fieldErrors.email[0] }}
            </small>
          </div>

          <div class="form-group">
            <label for="register-password">
              Password
            </label>

            <input
              id="register-password"
              v-model="form.password"
              type="password"
              autocomplete="new-password"
              minlength="8"
              placeholder="Minimum 8 characters"
              required
            />

            <small
              v-if="fieldErrors.password"
              class="form-error"
            >
              {{ fieldErrors.password[0] }}
            </small>
          </div>

          <div class="form-group">
            <label for="confirm-password">
              Confirm password
            </label>

            <input
              id="confirm-password"
              v-model="form.confirmPassword"
              type="password"
              autocomplete="new-password"
              placeholder="Re-enter your password"
              required
            />

            <small
              v-if="fieldErrors.confirmPassword"
              class="form-error"
            >
              {{ fieldErrors.confirmPassword[0] }}
            </small>
          </div>

          <button
            class="button button--primary button--full"
            type="submit"
            :disabled="loading"
          >
            {{
              loading
                ? "Creating account..."
                : "Register"
            }}
          </button>
        </form>

        <p class="auth-card__footer">
          Already have an account?

          <RouterLink :to="{ name: 'login' }">
            Login here
          </RouterLink>
        </p>
      </div>
    </div>
  </section>
</template>