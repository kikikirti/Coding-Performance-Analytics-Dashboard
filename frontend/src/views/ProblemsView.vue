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
import ProblemTable from "../components/ProblemTable.vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const deletingId = ref(null);
const updatingId = ref(null);
const updatingAction = ref("");
const errorMessage = ref("");
const successMessage = ref("");
const problems = ref([]);

function queryValue(name) {
  return typeof route.query[name] === "string"
    ? route.query[name]
    : "";
}

const filters = reactive({
  search: queryValue("search"),
  topic: queryValue("topic"),
  difficulty: queryValue("difficulty"),
  status: queryValue("status"),
  revision_status:
    queryValue("revision_status"),
  platform: queryValue("platform"),
});

const defaultTopics = [
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

const defaultPlatforms = [
  "LeetCode",
  "HackerRank",
  "CodeChef",
  "GeeksforGeeks",
  "Other",
];

function mergeOptions(
  defaultValues,
  problemField,
) {
  return [
    ...new Set([
      ...defaultValues,
      ...problems.value
        .map(
          (problem) =>
            problem[problemField],
        )
        .filter(Boolean),
    ]),
  ].sort((first, second) =>
    first.localeCompare(second),
  );
}

const topics = computed(() =>
  mergeOptions(
    defaultTopics,
    "topic",
  ),
);

const platforms = computed(() =>
  mergeOptions(
    defaultPlatforms,
    "platform",
  ),
);

const filteredProblems = computed(() => {
  const searchTerm = filters.search
    .trim()
    .toLowerCase();

  return problems.value.filter(
    (problem) => {
      const matchesSearch =
        !searchTerm ||
        problem.title
          ?.toLowerCase()
          .includes(searchTerm);

      const matchesTopic =
        !filters.topic ||
        problem.topic === filters.topic;

      const matchesDifficulty =
        !filters.difficulty ||
        problem.difficulty ===
          filters.difficulty;

      const matchesStatus =
        !filters.status ||
        problem.status === filters.status;

      const matchesRevisionStatus =
        !filters.revision_status ||
        problem.revision_status ===
          filters.revision_status;

      const matchesPlatform =
        !filters.platform ||
        problem.platform ===
          filters.platform;

      return (
        matchesSearch &&
        matchesTopic &&
        matchesDifficulty &&
        matchesStatus &&
        matchesRevisionStatus &&
        matchesPlatform
      );
    },
  );
});

const hasActiveFilters = computed(() =>
  Object.values(filters).some(
    (value) => value.trim() !== "",
  ),
);

const resultSummary = computed(() => {
  const visibleCount =
    filteredProblems.value.length;

  const totalCount =
    problems.value.length;

  if (!hasActiveFilters.value) {
    return `${totalCount} problem${
      totalCount === 1 ? "" : "s"
    }`;
  }

  return `${visibleCount} of ${totalCount} problems`;
});

function buildQuery() {
  return Object.fromEntries(
    Object.entries(filters).filter(
      ([, value]) =>
        value.trim() !== "",
    ),
  );
}

function clearMessages() {
  errorMessage.value = "";
  successMessage.value = "";
}

function applySaveNotice() {
  const saved = queryValue("saved");

  if (saved === "created") {
    successMessage.value =
      "Coding problem created successfully.";
  } else if (saved === "updated") {
    successMessage.value =
      "Coding problem updated successfully.";
  } else {
    return;
  }

  const cleanedQuery = {
    ...route.query,
  };

  delete cleanedQuery.saved;

  router.replace({
    name: "problems",
    query: cleanedQuery,
  });
}

async function loadProblems() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get(
      "/api/problems",
    );

    problems.value =
      response.data.data.problems || [];
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Coding problems could not be loaded.";
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  Object.assign(filters, {
    search: "",
    topic: "",
    difficulty: "",
    status: "",
    revision_status: "",
    platform: "",
  });
}

function editProblem(problemId) {
  router.push({
    name: "problem-edit",
    params: {
      id: problemId,
    },
  });
}

function replaceProblem(updatedProblem) {
  const problemIndex =
    problems.value.findIndex(
      (problem) =>
        problem.id === updatedProblem.id,
    );

  if (problemIndex !== -1) {
    problems.value.splice(
      problemIndex,
      1,
      updatedProblem,
    );
  }
}

function todayAsIsoDate() {
  const today = new Date();
  const year = today.getFullYear();

  const month = String(
    today.getMonth() + 1,
  ).padStart(2, "0");

  const day = String(
    today.getDate(),
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

async function updateProblemStatus(
  problem,
  nextStatus,
) {
  if (problem.status === nextStatus) {
    return;
  }

  updatingId.value = problem.id;
  updatingAction.value = nextStatus;
  clearMessages();

  const payload = {
    status: nextStatus,
  };

  if (nextStatus === "Solved") {
    payload.solved_date =
      todayAsIsoDate();
  }

  try {
    const response = await api.put(
      `/api/problems/${problem.id}`,
      payload,
    );

    replaceProblem(
      response.data.data.problem,
    );

    successMessage.value =
      nextStatus === "Solved"
        ? `"${problem.title}" was marked as solved.`
        : `"${problem.title}" was marked as revision needed.`;
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The problem status could not be updated.";
  } finally {
    updatingId.value = null;
    updatingAction.value = "";
  }
}

async function deleteProblem(problem) {
  const confirmed = window.confirm(
    `Delete "${problem.title}"? This action cannot be undone.`,
  );

  if (!confirmed) {
    return;
  }

  deletingId.value = problem.id;
  clearMessages();

  try {
    await api.delete(
      `/api/problems/${problem.id}`,
    );

    problems.value =
      problems.value.filter(
        (item) =>
          item.id !== problem.id,
      );

    successMessage.value =
      `"${problem.title}" was deleted successfully.`;
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The problem could not be deleted.";
  } finally {
    deletingId.value = null;
  }
}

watch(
  filters,
  () => {
    router.replace({
      name: "problems",
      query: buildQuery(),
    });
  },
  {
    deep: true,
  },
);

onMounted(() => {
  applySaveNotice();
  loadProblems();
});
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">
          Problem tracker
        </span>

        <h1>Coding Problems</h1>

        <p>
          Search, filter, update, and manage every
          coding problem in your preparation tracker.
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

    <div
      v-if="successMessage"
      class="alert alert--success"
    >
      {{ successMessage }}
    </div>

    <article class="panel filter-panel">
      <div
        class="
          filter-grid
          filter-grid--problems
        "
      >
        <div
          class="
            form-group
            form-group--search
          "
        >
          <label for="problem-search">
            Search by title
          </label>

          <input
            id="problem-search"
            v-model="filters.search"
            type="search"
            placeholder="Search coding problems..."
            autocomplete="off"
          />
        </div>

        <div class="form-group">
          <label for="topic-filter">
            Topic
          </label>

          <select
            id="topic-filter"
            v-model="filters.topic"
          >
            <option value="">
              All topics
            </option>

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
            <option value="">
              All difficulties
            </option>

            <option
              v-for="
                difficulty in difficulties
              "
              :key="difficulty"
              :value="difficulty"
            >
              {{ difficulty }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label for="status-filter">
            Status
          </label>

          <select
            id="status-filter"
            v-model="filters.status"
          >
            <option value="">
              All statuses
            </option>

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
            v-model="
              filters.revision_status
            "
          >
            <option value="">
              All revision stages
            </option>

            <option
              v-for="
                status in revisionStatuses
              "
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
            <option value="">
              All platforms
            </option>

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
          class="button button--secondary"
          :disabled="!hasActiveFilters"
          @click="resetFilters"
        >
          Clear Filters
        </button>
      </div>
    </article>

    <article class="panel">
      <div class="panel__header">
        <div>
          <h2>Problem Records</h2>

          <p>
            {{ resultSummary }} displayed
          </p>
        </div>
      </div>

      <div
        v-if="loading"
        class="loading-panel"
      >
        Loading coding problems...
      </div>

      <div
        v-else-if="problems.length === 0"
        class="
          empty-state
          empty-state--compact
        "
      >
        <h3>No coding problems added yet</h3>

        <p>
          Add your first problem to start tracking
          solving, attempts, and revision progress.
        </p>

        <RouterLink
          :to="{ name: 'problem-create' }"
          class="button button--primary"
        >
          Add Problem
        </RouterLink>
      </div>

      <div
        v-else-if="
          filteredProblems.length === 0
        "
        class="
          empty-state
          empty-state--compact
        "
      >
        <h3>
          No problems match the filters
        </h3>

        <p>
          Change the search text or clear one or more
          filters to see additional problem records.
        </p>

        <button
          type="button"
          class="button button--secondary"
          @click="resetFilters"
        >
          Clear Filters
        </button>
      </div>

      <ProblemTable
        v-else
        :problems="filteredProblems"
        :busy-id="
          deletingId || updatingId
        "
        :busy-action="
          deletingId
            ? 'delete'
            : updatingAction
        "
        @edit="editProblem"
        @delete="deleteProblem"
        @mark-solved="
          updateProblemStatus(
            $event,
            'Solved',
          )
        "
        @mark-revision="
          updateProblemStatus(
            $event,
            'Revision Needed',
          )
        "
      />
    </article>
  </section>
</template>

<style scoped>
.filter-grid--problems {
  grid-template-columns:
    minmax(260px, 1.6fr)
    repeat(
      5,
      minmax(150px, 1fr)
    );
}

.form-group--search input {
  width: 100%;
}

.empty-state--compact .button {
  margin-top: 16px;
}

@media (max-width: 1250px) {
  .filter-grid--problems {
    grid-template-columns:
      repeat(
        3,
        minmax(0, 1fr)
      );
  }

  .form-group--search {
    grid-column: span 2;
  }
}

@media (max-width: 760px) {
  .filter-grid--problems {
    grid-template-columns: 1fr;
  }

  .form-group--search {
    grid-column: auto;
  }
}
</style>