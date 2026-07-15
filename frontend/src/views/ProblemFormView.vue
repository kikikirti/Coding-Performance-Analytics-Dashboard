<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import api from "../api/axios";

const route = useRoute();
const router = useRouter();

const isEditing = computed(() => {
  return Boolean(route.params.id);
});

const loading = ref(false);
const loadingProblem = ref(false);
const errorMessage = ref("");
const fieldErrors = ref({});

const form = reactive({
  title: "",
  platform: "LeetCode",
  platform_link: "",
  topic: "Array",
  difficulty: "Easy",
  status: "Unsolved",
  attempts: 0,
  time_spent_minutes: 0,
  revision_status: "Not Started",
  notes: "",
  solved_date: "",
});

const platforms = [
  "LeetCode",
  "HackerRank",
  "CodeChef",
  "GeeksforGeeks",
  "Other",
];

const topics = [
  "Array",
  "String",
  "Linked List",
  "Stack",
  "Queue",
  "Tree",
  "Binary Search Tree",
  "Graph",
  "Heap",
  "Greedy",
  "Dynamic Programming",
  "Recursion",
  "Divide and Conquer",
  "Hashing",
  "Sorting",
  "Searching",
  "Binary Search",
];

const difficulties = [
  "Easy",
  "Medium",
  "Hard",
];

const statuses = [
  "Unsolved",
  "Solved",
  "Revision Needed",
];

const revisionStatuses = [
  "Not Started",
  "First Revision",
  "Second Revision",
  "Mastered",
];

async function loadProblem() {
  if (!isEditing.value) {
    return;
  }

  loadingProblem.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get(
      `/api/problems/${route.params.id}`,
    );

    const problem =
      response.data.data.problem;

    Object.assign(
      form,
      {
        title: problem.title || "",
        platform: problem.platform || "LeetCode",
        platform_link:
          problem.platform_link || "",
        topic: problem.topic || "Array",
        difficulty:
          problem.difficulty || "Easy",
        status:
          problem.status || "Unsolved",
        attempts:
          problem.attempts ?? 0,
        time_spent_minutes:
          problem.time_spent_minutes ?? 0,
        revision_status:
          problem.revision_status ||
          "Not Started",
        notes:
          problem.notes || "",
        solved_date:
          problem.solved_date || "",
      },
    );
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The coding problem could not be loaded.";
  } finally {
    loadingProblem.value = false;
  }
}

async function submitProblem() {
  loading.value = true;
  errorMessage.value = "";
  fieldErrors.value = {};

  const payload = {
    title: form.title.trim(),
    platform: form.platform,
    platform_link:
      form.platform_link.trim() || null,
    topic: form.topic,
    difficulty: form.difficulty,
    status: form.status,
    attempts: Number(form.attempts),
    time_spent_minutes:
      Number(form.time_spent_minutes),
    revision_status:
      form.revision_status,
    notes:
      form.notes.trim() || null,
    solved_date:
      form.status === "Solved"
        ? form.solved_date
        : null,
  };

  try {
    if (isEditing.value) {
      await api.put(
        `/api/problems/${route.params.id}`,
        payload,
      );
    } else {
      await api.post(
        "/api/problems",
        payload,
      );
    }

    await router.push({
      name: "problems",
    });
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The coding problem could not be saved.";

    fieldErrors.value =
      error.response?.data?.errors || {};
  } finally {
    loading.value = false;
  }
}

watch(
  () => form.status,
  (status) => {
    if (status !== "Solved") {
      form.solved_date = "";
    }
  },
);

onMounted(loadProblem);
</script>

<template>
  <section class="page page--narrow">
    <div class="page-header">
      <div>
        <span class="eyebrow">
          {{ isEditing ? "Update record" : "New record" }}
        </span>

        <h1>
          {{
            isEditing
              ? "Edit Coding Problem"
              : "Add Coding Problem"
          }}
        </h1>

        <p>
          Record problem details, attempts, time spent,
          solving status and revision progress.
        </p>
      </div>

      <RouterLink
        :to="{ name: 'problems' }"
        class="button button--secondary"
      >
        Back to Problems
      </RouterLink>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loadingProblem"
      class="loading-panel"
    >
      Loading problem details...
    </div>

    <form
      v-else
      class="panel form"
      @submit.prevent="submitProblem"
    >
      <div class="form-section">
        <div class="form-section__header">
          <h2>Problem Information</h2>
          <p>Enter the source and classification details.</p>
        </div>

        <div class="form-grid">
          <div class="form-group form-group--full">
            <label for="problem-title">
              Problem Title
            </label>

            <input
              id="problem-title"
              v-model="form.title"
              type="text"
              placeholder="Example: Number of Islands"
              required
            />

            <small
              v-if="fieldErrors.title"
              class="form-error"
            >
              {{ fieldErrors.title[0] }}
            </small>
          </div>

          <div class="form-group">
            <label for="problem-platform">
              Platform
            </label>

            <select
              id="problem-platform"
              v-model="form.platform"
            >
              <option
                v-for="platform in platforms"
                :key="platform"
                :value="platform"
              >
                {{ platform }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="problem-topic">
              Topic
            </label>

            <select
              id="problem-topic"
              v-model="form.topic"
              required
            >
              <option
                v-for="topic in topics"
                :key="topic"
                :value="topic"
              >
                {{ topic }}
              </option>
            </select>

            <small
              v-if="fieldErrors.topic"
              class="form-error"
            >
              {{ fieldErrors.topic[0] }}
            </small>
          </div>

          <div class="form-group form-group--full">
            <label for="problem-link">
              Platform Link
            </label>

            <input
              id="problem-link"
              v-model="form.platform_link"
              type="url"
              placeholder="https://leetcode.com/problems/..."
            />

            <small class="form-hint">
              Optional direct link to the coding problem.
            </small>
          </div>

          <div class="form-group">
            <label for="problem-difficulty">
              Difficulty
            </label>

            <select
              id="problem-difficulty"
              v-model="form.difficulty"
            >
              <option
                v-for="difficulty in difficulties"
                :key="difficulty"
                :value="difficulty"
              >
                {{ difficulty }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="problem-status">
              Solving Status
            </label>

            <select
              id="problem-status"
              v-model="form.status"
            >
              <option
                v-for="status in statuses"
                :key="status"
                :value="status"
              >
                {{ status }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="form-section">
        <div class="form-section__header">
          <h2>Performance Details</h2>
          <p>Record effort and completion information.</p>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="attempts">
              Number of Attempts
            </label>

            <input
              id="attempts"
              v-model.number="form.attempts"
              type="number"
              min="0"
              step="1"
              required
            />

            <small
              v-if="fieldErrors.attempts"
              class="form-error"
            >
              {{ fieldErrors.attempts[0] }}
            </small>
          </div>

          <div class="form-group">
            <label for="time-spent">
              Time Spent in Minutes
            </label>

            <input
              id="time-spent"
              v-model.number="form.time_spent_minutes"
              type="number"
              min="0"
              step="1"
              required
            />

            <small
              v-if="fieldErrors.time_spent_minutes"
              class="form-error"
            >
              {{ fieldErrors.time_spent_minutes[0] }}
            </small>
          </div>

          <div class="form-group">
            <label for="revision-status">
              Revision Status
            </label>

            <select
              id="revision-status"
              v-model="form.revision_status"
            >
              <option
                v-for="status in revisionStatuses"
                :key="status"
                :value="status"
              >
                {{ status }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="solved-date">
              Solved Date
            </label>

            <input
              id="solved-date"
              v-model="form.solved_date"
              type="date"
              :required="form.status === 'Solved'"
              :disabled="form.status !== 'Solved'"
            />

            <small
              v-if="fieldErrors.solved_date"
              class="form-error"
            >
              {{ fieldErrors.solved_date[0] }}
            </small>

            <small
              v-else
              class="form-hint"
            >
              Required only when the problem is solved.
            </small>
          </div>

          <div class="form-group form-group--full">
            <label for="problem-notes">
              Notes
            </label>

            <textarea
              id="problem-notes"
              v-model="form.notes"
              rows="5"
              placeholder="Approach used, mistakes, edge cases or revision notes..."
            ></textarea>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <RouterLink
          :to="{ name: 'problems' }"
          class="button button--secondary"
        >
          Cancel
        </RouterLink>

        <button
          type="submit"
          class="button button--primary"
          :disabled="loading"
        >
          {{
            loading
              ? "Saving..."
              : isEditing
                ? "Update Problem"
                : "Create Problem"
          }}
        </button>
      </div>
    </form>
  </section>
</template>