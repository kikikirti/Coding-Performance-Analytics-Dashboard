<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue";

import api from "../api/axios";

import ProblemTable from "../components/ProblemTable.vue";
import StatCard from "../components/StatCard.vue";

const loading = ref(false);
const errorMessage = ref("");
const problems = ref([]);

const revisionCounts = ref({
  "Not Started": 0,
  "First Revision": 0,
  "Second Revision": 0,
  Mastered: 0,
});

const selectedRevisionStatus = ref("");

const revisionStatuses = [
  "Not Started",
  "First Revision",
  "Second Revision",
  "Mastered",
];

const revisionProblems = computed(() => {
  let result = problems.value.filter(
    (problem) =>
      problem.status === "Revision Needed" ||
      problem.revision_status !== "Mastered",
  );

  if (selectedRevisionStatus.value) {
    result = result.filter(
      (problem) =>
        problem.revision_status ===
        selectedRevisionStatus.value,
    );
  }

  return result;
});

async function loadRevisionData() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const [
      summaryResponse,
      problemsResponse,
    ] = await Promise.all([
      api.get("/api/dashboard/revision-summary"),
      api.get("/api/problems"),
    ]);

    revisionCounts.value =
      summaryResponse.data.data.revision_status_counts;

    problems.value =
      problemsResponse.data.data.problems;
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Revision information could not be loaded.";
  } finally {
    loading.value = false;
  }
}

onMounted(loadRevisionData);
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">Revision management</span>
        <h1>Revision Tracker</h1>

        <p>
          Review pending problems and move important
          concepts toward mastery.
        </p>
      </div>

      <button
        type="button"
        class="button button--secondary"
        :disabled="loading"
        @click="loadRevisionData"
      >
        Refresh
      </button>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
    >
      {{ errorMessage }}
    </div>

    <div class="stats-grid stats-grid--four">
      <StatCard
        title="Not Started"
        :value="revisionCounts['Not Started']"
        subtitle="Problems awaiting first revision"
        icon="0"
      />

      <StatCard
        title="First Revision"
        :value="revisionCounts['First Revision']"
        subtitle="Problems revised once"
        icon="1"
      />

      <StatCard
        title="Second Revision"
        :value="revisionCounts['Second Revision']"
        subtitle="Problems revised twice"
        icon="2"
      />

      <StatCard
        title="Mastered"
        :value="revisionCounts.Mastered"
        subtitle="Problems marked as mastered"
        icon="M"
      />
    </div>

    <article class="panel">
      <div class="panel__header panel__header--responsive">
        <div>
          <span class="eyebrow">Revision queue</span>
          <h2>Problems Requiring Attention</h2>

          <p>
            {{ revisionProblems.length }}
            problem{{
              revisionProblems.length === 1 ? "" : "s"
            }}
            currently displayed
          </p>
        </div>

        <div class="form-group form-group--inline">
          <label for="revision-page-filter">
            Revision stage
          </label>

          <select
            id="revision-page-filter"
            v-model="selectedRevisionStatus"
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
      </div>

      <div
        v-if="loading"
        class="loading-panel"
      >
        Loading revision information...
      </div>

      <ProblemTable
        v-else
        :problems="revisionProblems"
        :show-actions="false"
      />
    </article>
  </section>
</template>