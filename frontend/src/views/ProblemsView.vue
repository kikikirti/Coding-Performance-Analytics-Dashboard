<script setup>
import {
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
import ProblemTable from "../components/ProblemTable.vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const deletingId = ref(null);
const errorMessage = ref("");
const problems = ref([]);

const filters = reactive({
  topic:
    typeof route.query.topic === "string"
      ? route.query.topic
      : "",

  difficulty:
    typeof route.query.difficulty === "string"
      ? route.query.difficulty
      : "",

  status:
    typeof route.query.status === "string"
      ? route.query.status
      : "",

  revision_status:
    typeof route.query.revision_status === "string"
      ? route.query.revision_status
      : "",

  platform:
    typeof route.query.platform === "string"
      ? route.query.platform
      : "",
});

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

const platforms = [
  "LeetCode",
  "HackerRank",
  "CodeChef",
  "GeeksforGeeks",
];

function buildParameters() {
  return Object.fromEntries(
    Object.entries(filters).filter(
      ([, value]) =>
        value !== null &&
        value !== undefined &&
        value !== "",
    ),
  );
}

async function loadProblems() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const params = buildParameters();

    const response = await api.get(
      "/api/problems",
      {
        params,
      },
    );

    problems.value =
      response.data.data.problems;

    await router.replace({
      name: "problems",
      query: params,
    });
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Coding problems could not be loaded.";
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  Object.assign(
    filters,
    {
      topic: "",
      difficulty: "",
      status: "",
      revision_status: "",
      platform: "",
    },
  );

  loadProblems();
}

function editProblem(problemId) {
  router.push({
    name: "problem-edit",
    params: {
      id: problemId,
    },
  });
}

async function deleteProblem(problem) {
  const confirmed = window.confirm(
    `Delete "${problem.title}"? This action cannot be undone.`,
  );

  if (!confirmed) {
    return;
  }

  deletingId.value = problem.id;
  errorMessage.value = "";

  try {
    await api.delete(
      `/api/problems/${problem.id}`,
    );

    await loadProblems();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The problem could not be deleted.";
  } finally {
    deletingId.value = null;
  }
}

watch(
  () => route.query,
  (query) => {
    if (query.topic !== undefined) {
      filters.topic =
        typeof query.topic === "string"
          ? query.topic
          : "";
    }
  },
);

onMounted(loadProblems);
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">Problem tracker</span>
        <h1>Coding Problems</h1>

        <p>
          Store problems from different platforms and track
          solving and revision progress.
        </p>
      </div>

      <RouterLink
        :to="{ name: 'problem-create' }"
        class="button button--primary"
      >
        Add Problem
      </RouterLink>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
    >
      {{ errorMessage }}
    </div>

    <article class="panel filter-panel">
      <div class="filter-grid">
        <div class="form-group">
          <label for="topic-filter">Topic</label>

          <select
            id="topic-filter"
            v-model="filters.topic"
          >
            <option value="">All topics</option>

            <option
              v-for="topic in topics"
              :key="topic"
              :value="topic"
            >
              {{ topic }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="difficulty-filter">
            Difficulty
          </label>

          <select
            id="difficulty-filter"
            v-model="filters.difficulty"
          >
            <option value="">All difficulties</option>

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
          <label for="status-filter">Status</label>

          <select
            id="status-filter"
            v-model="filters.status"
          >
            <option value="">All statuses</option>

            <option
              v-for="status in statuses"
              :key="status"
              :value="status"
            >
              {{ status }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="revision-filter">
            Revision Status
          </label>

          <select
            id="revision-filter"
            v-model="filters.revision_status"
          >
            <option value="">All revision stages</option>

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
          <label for="platform-filter">
            Platform
          </label>

          <select
            id="platform-filter"
            v-model="filters.platform"
          >
            <option value="">All platforms</option>

            <option
              v-for="platform in platforms"
              :key="platform"
              :value="platform"
            >
              {{ platform }}
            </option>
          </select>
        </div>
      </div>

      <div class="filter-actions">
        <button
          type="button"
          class="button button--primary"
          :disabled="loading"
          @click="loadProblems"
        >
          Apply Filters
        </button>

        <button
          type="button"
          class="button button--secondary"
          :disabled="loading"
          @click="resetFilters"
        >
          Reset
        </button>
      </div>
    </article>

    <article class="panel">
      <div class="panel__header">
        <div>
          <h2>Problem Records</h2>

          <p>
            {{ problems.length }}
            problem{{ problems.length === 1 ? "" : "s" }}
            found
          </p>
        </div>
      </div>

      <div
        v-if="loading"
        class="loading-panel"
      >
        Loading coding problems...
      </div>

      <ProblemTable
        v-else
        :problems="problems"
        @edit="editProblem"
        @delete="deleteProblem"
      />

      <p
        v-if="deletingId"
        class="muted-text"
      >
        Deleting problem...
      </p>
    </article>
  </section>
</template>