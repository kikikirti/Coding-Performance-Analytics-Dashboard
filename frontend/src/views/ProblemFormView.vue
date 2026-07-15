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

const isEditing = computed(() =>
  Boolean(route.params.id),
);

const pageTitle = computed(() =>
  isEditing.value
    ? "Edit Coding Problem"
    : "Add Coding Problem",
);

const submitLabel = computed(() => {
  if (saving.value) {
    return "Saving...";
  }

  return isEditing.value
    ? "Update Problem"
    : "Create Problem";
});

const saving = ref(false);
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
  solved_date: "",
  notes: "",
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

function firstError(fieldName) {
  const error = fieldErrors.value[fieldName];

  if (Array.isArray(error)) {
    return error[0] || "";
  }

  return typeof error === "string"
    ? error
    : "";
}

function hasError(fieldName) {
  return Boolean(firstError(fieldName));
}

function clearFieldError(fieldName) {
  if (!fieldErrors.value[fieldName]) {
    return;
  }

  const updatedErrors = {
    ...fieldErrors.value,
  };

  delete updatedErrors[fieldName];
  fieldErrors.value = updatedErrors;
}

function normalizeApiErrors(errors) {
  if (!errors || typeof errors !== "object") {
    return {};
  }

  return Object.fromEntries(
    Object.entries(errors).map(
      ([field, messages]) => [
        field,
        Array.isArray(messages)
          ? messages
          : [String(messages)],
      ],
    ),
  );
}

function isNonNegativeInteger(value) {
  if (
    value === "" ||
    value === null ||
    value === undefined
  ) {
    return false;
  }

  const numberValue = Number(value);

  return (
    Number.isInteger(numberValue) &&
    numberValue >= 0
  );
}

function validateForm() {
  const errors = {};

  if (!form.title.trim()) {
    errors.title = ["Title is required."];
  }

  if (!form.topic) {
    errors.topic = ["Topic is required."];
  }

  if (!form.difficulty) {
    errors.difficulty = [
      "Difficulty is required.",
    ];
  }

  if (!form.status) {
    errors.status = ["Status is required."];
  }

  if (!isNonNegativeInteger(form.attempts)) {
    errors.attempts = [
      "Attempts must be a non-negative whole number.",
    ];
  }

  if (
    !isNonNegativeInteger(
      form.time_spent_minutes,
    )
  ) {
    errors.time_spent_minutes = [
      "Time spent must be a non-negative whole number.",
    ];
  }

  if (
    form.status === "Solved" &&
    !form.solved_date
  ) {
    errors.solved_date = [
      "Solved date is required when status is Solved.",
    ];
  }

  fieldErrors.value = errors;

  if (Object.keys(errors).length > 0) {
    errorMessage.value =
      "Please correct the highlighted fields before saving.";

    return false;
  }

  return true;
}

function buildPayload() {
  return {
    title: form.title.trim(),
    platform: form.platform,
    platform_link:
      form.platform_link.trim() || null,
    topic: form.topic,
    difficulty: form.difficulty,
    status: form.status,
    attempts: Number(form.attempts),
    time_spent_minutes: Number(
      form.time_spent_minutes,
    ),
    revision_status: form.revision_status,
    solved_date:
      form.status === "Solved"
        ? form.solved_date
        : null,
    notes: form.notes.trim() || null,
  };
}

async function loadProblem() {
  if (!isEditing.value) {
    return;
  }

  loadingProblem.value = true;
  errorMessage.value = "";
  fieldErrors.value = {};

  try {
    const response = await api.get(
      `/api/problems/${route.params.id}`,
    );

    const problem =
      response.data.data.problem;

    Object.assign(form, {
      title: problem.title || "",
      platform:
        problem.platform || "LeetCode",
      platform_link:
        problem.platform_link || "",
      topic:
        problem.topic || "Array",
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
      solved_date:
        problem.solved_date || "",
      notes:
        problem.notes || "",
    });
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The coding problem could not be loaded.";

    fieldErrors.value = normalizeApiErrors(
      error.response?.data?.errors,
    );
  } finally {
    loadingProblem.value = false;
  }
}

async function submitProblem() {
  errorMessage.value = "";
  fieldErrors.value = {};

  if (!validateForm()) {
    return;
  }

  saving.value = true;

  try {
    const payload = buildPayload();

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
      query: {
        saved: isEditing.value
          ? "updated"
          : "created",
      },
    });
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The coding problem could not be saved.";

    fieldErrors.value = normalizeApiErrors(
      error.response?.data?.errors,
    );
  } finally {
    saving.value = false;
  }
}

watch(
  () => form.status,
  (status) => {
    clearFieldError("status");

    if (status !== "Solved") {
      form.solved_date = "";
      clearFieldError("solved_date");
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
          {{
            isEditing
              ? "Update record"
              : "New record"
          }}
        </span>

        <h1>{{ pageTitle }}</h1>

        <p>
          Add the problem source, classification, effort,
          completion details, and revision notes.
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
      role="alert"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="
        firstError('body') ||
        firstError('database')
      "
      class="alert alert--error"
      role="alert"
    >
      {{
        firstError("body") ||
        firstError("database")
      }}
    </div>

    <div
      v-if="loadingProblem"
      class="loading-panel"
    >
      Loading problem details...
    </div>

    <form
      v-else
      class="panel form problem-form"
      novalidate
      @submit.prevent="submitProblem"
    >
      <div class="form-section">
        <div class="form-section__header">
          <h2>Problem Information</h2>

          <p>
            Required fields are marked with an asterisk.
          </p>
        </div>

        <div class="form-grid">
          <div class="form-group form-group--full">
            <label for="problem-title">
              Title
              <span class="required-mark">*</span>
            </label>

            <input
              id="problem-title"
              v-model="form.title"
              type="text"
              placeholder="Example: Number of Islands"
              autocomplete="off"
              required
              :aria-invalid="hasError('title')"
              :class="{
                'form-control--error':
                  hasError('title'),
              }"
              @input="clearFieldError('title')"
            />

            <small
              v-if="hasError('title')"
              class="form-error"
            >
              {{ firstError("title") }}
            </small>
          </div>

          <div class="form-group">
            <label for="problem-platform">
              Platform
            </label>

            <select
              id="problem-platform"
              v-model="form.platform"
              :aria-invalid="hasError('platform')"
              :class="{
                'form-control--error':
                  hasError('platform'),
              }"
              @change="clearFieldError('platform')"
            >
              <option
                v-for="platform in platforms"
                :key="platform"
                :value="platform"
              >
                {{ platform }}
              </option>
            </select>

            <small
              v-if="hasError('platform')"
              class="form-error"
            >
              {{ firstError("platform") }}
            </small>
          </div>

          <div class="form-group">
            <label for="problem-topic">
              Topic
              <span class="required-mark">*</span>
            </label>

            <select
              id="problem-topic"
              v-model="form.topic"
              required
              :aria-invalid="hasError('topic')"
              :class="{
                'form-control--error':
                  hasError('topic'),
              }"
              @change="clearFieldError('topic')"
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
              v-if="hasError('topic')"
              class="form-error"
            >
              {{ firstError("topic") }}
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
              :aria-invalid="
                hasError('platform_link')
              "
              :class="{
                'form-control--error':
                  hasError('platform_link'),
              }"
              @input="
                clearFieldError('platform_link')
              "
            />

            <small
              v-if="hasError('platform_link')"
              class="form-error"
            >
              {{ firstError("platform_link") }}
            </small>

            <small
              v-else
              class="form-hint"
            >
              Optional direct URL to the problem.
            </small>
          </div>

          <div class="form-group">
            <label for="problem-difficulty">
              Difficulty
              <span class="required-mark">*</span>
            </label>

            <select
              id="problem-difficulty"
              v-model="form.difficulty"
              required
              :aria-invalid="
                hasError('difficulty')
              "
              :class="{
                'form-control--error':
                  hasError('difficulty'),
              }"
              @change="
                clearFieldError('difficulty')
              "
            >
              <option
                v-for="difficulty in difficulties"
                :key="difficulty"
                :value="difficulty"
              >
                {{ difficulty }}
              </option>
            </select>

            <small
              v-if="hasError('difficulty')"
              class="form-error"
            >
              {{ firstError("difficulty") }}
            </small>
          </div>

          <div class="form-group">
            <label for="problem-status">
              Status
              <span class="required-mark">*</span>
            </label>

            <select
              id="problem-status"
              v-model="form.status"
              required
              :aria-invalid="hasError('status')"
              :class="{
                'form-control--error':
                  hasError('status'),
              }"
            >
              <option
                v-for="status in statuses"
                :key="status"
                :value="status"
              >
                {{ status }}
              </option>
            </select>

            <small
              v-if="hasError('status')"
              class="form-error"
            >
              {{ firstError("status") }}
            </small>
          </div>
        </div>
      </div>

      <div class="form-section">
        <div class="form-section__header">
          <h2>Progress and Revision</h2>

          <p>
            Record attempts, time spent, completion, and
            revision progress.
          </p>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label for="attempts">
              Attempts
            </label>

            <input
              id="attempts"
              v-model.number="form.attempts"
              type="number"
              min="0"
              step="1"
              required
              :aria-invalid="
                hasError('attempts')
              "
              :class="{
                'form-control--error':
                  hasError('attempts'),
              }"
              @input="
                clearFieldError('attempts')
              "
            />

            <small
              v-if="hasError('attempts')"
              class="form-error"
            >
              {{ firstError("attempts") }}
            </small>

            <small
              v-else
              class="form-hint"
            >
              Defaults to 0.
            </small>
          </div>

          <div class="form-group">
            <label for="time-spent">
              Time Spent (minutes)
            </label>

            <input
              id="time-spent"
              v-model.number="
                form.time_spent_minutes
              "
              type="number"
              min="0"
              step="1"
              required
              :aria-invalid="
                hasError('time_spent_minutes')
              "
              :class="{
                'form-control--error':
                  hasError(
                    'time_spent_minutes',
                  ),
              }"
              @input="
                clearFieldError(
                  'time_spent_minutes',
                )
              "
            />

            <small
              v-if="
                hasError('time_spent_minutes')
              "
              class="form-error"
            >
              {{
                firstError(
                  "time_spent_minutes",
                )
              }}
            </small>

            <small
              v-else
              class="form-hint"
            >
              Defaults to 0.
            </small>
          </div>

          <div class="form-group">
            <label for="revision-status">
              Revision Status
            </label>

            <select
              id="revision-status"
              v-model="form.revision_status"
              :aria-invalid="
                hasError('revision_status')
              "
              :class="{
                'form-control--error':
                  hasError('revision_status'),
              }"
              @change="
                clearFieldError(
                  'revision_status',
                )
              "
            >
              <option
                v-for="
                  revisionStatus in
                  revisionStatuses
                "
                :key="revisionStatus"
                :value="revisionStatus"
              >
                {{ revisionStatus }}
              </option>
            </select>

            <small
              v-if="
                hasError('revision_status')
              "
              class="form-error"
            >
              {{
                firstError(
                  "revision_status",
                )
              }}
            </small>
          </div>

          <div
            v-if="form.status === 'Solved'"
            class="form-group"
          >
            <label for="solved-date">
              Solved Date
              <span class="required-mark">*</span>
            </label>

            <input
              id="solved-date"
              v-model="form.solved_date"
              type="date"
              required
              :aria-invalid="
                hasError('solved_date')
              "
              :class="{
                'form-control--error':
                  hasError('solved_date'),
              }"
              @input="
                clearFieldError('solved_date')
              "
            />

            <small
              v-if="hasError('solved_date')"
              class="form-error"
            >
              {{ firstError("solved_date") }}
            </small>

            <small
              v-else
              class="form-hint"
            >
              Required because the current status is
              Solved.
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
              placeholder="Approach, mistakes, edge cases, or revision notes..."
              :aria-invalid="hasError('notes')"
              :class="{
                'form-control--error':
                  hasError('notes'),
              }"
              @input="clearFieldError('notes')"
            ></textarea>

            <small
              v-if="hasError('notes')"
              class="form-error"
            >
              {{ firstError("notes") }}
            </small>
          </div>
        </div>
      </div>

      <div
        class="
          form-actions
          problem-form__actions
        "
      >
        <RouterLink
          :to="{ name: 'problems' }"
          class="button button--secondary"
        >
          Cancel
        </RouterLink>

        <button
          type="submit"
          class="button button--primary"
          :disabled="saving"
        >
          {{ submitLabel }}
        </button>
      </div>
    </form>
  </section>
</template>

<style scoped>
.required-mark {
  color: var(--danger);
}

.form-control--error {
  border-color: var(--danger) !important;

  box-shadow:
    0 0 0 3px
    rgba(181, 45, 58, 0.1) !important;
}

.problem-form__actions {
  padding-top: 2px;
}

@media (max-width: 760px) {
  .problem-form__actions {
    flex-direction: column-reverse;
  }

  .problem-form__actions .button {
    width: 100%;
  }
}
</style>