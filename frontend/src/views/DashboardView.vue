<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue";

import { useRouter } from "vue-router";

import api from "../api/axios";

import DifficultyProgressTable from "../components/DifficultyProgressTable.vue";
import ProgressBar from "../components/ProgressBar.vue";
import StatCard from "../components/StatCard.vue";
import TopicProgressTable from "../components/TopicProgressTable.vue";
import WeakTopicCard from "../components/WeakTopicCard.vue";

const router = useRouter();

const loading = ref(true);
const errorMessage = ref("");

const summary = ref({
  total_problems: 0,
  solved_problems: 0,
  unsolved_problems: 0,
  revision_needed_problems: 0,
  total_attempts: 0,
  total_time_spent_minutes: 0,
  average_attempts_per_problem: 0,
  solved_percentage: 0,
});

const topics = ref([]);
const difficulties = ref([]);
const weakTopics = ref([]);

const revisionCounts = ref({
  "Not Started": 0,
  "First Revision": 0,
  "Second Revision": 0,
  Mastered: 0,
});

const dailyTarget = ref({
  today_target: 0,
  today_solved: 0,
  completion_percentage: 0,
  remaining_today: 0,
  last_7_days_solved_count: 0,
  target_exists: false,
});

const topWeakTopics = computed(() => {
  return weakTopics.value.slice(0, 3);
});

const formattedTime = computed(() => {
  const minutes =
    summary.value.total_time_spent_minutes || 0;

  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  return `${hours}h ${remainingMinutes}m`;
});

async function loadDashboard() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const [
      summaryResponse,
      topicResponse,
      difficultyResponse,
      weakResponse,
      revisionResponse,
      targetResponse,
    ] = await Promise.all([
      api.get("/api/dashboard/summary"),
      api.get("/api/dashboard/topic-progress"),
      api.get("/api/dashboard/difficulty-progress"),
      api.get("/api/dashboard/weak-topics"),
      api.get("/api/dashboard/revision-summary"),
      api.get("/api/dashboard/daily-target-summary"),
    ]);

    summary.value =
      summaryResponse.data.data;

    topics.value =
      topicResponse.data.data.topics;

    difficulties.value =
      difficultyResponse.data.data.difficulties;

    weakTopics.value =
      weakResponse.data.data.weak_topics;

    revisionCounts.value =
      revisionResponse.data.data.revision_status_counts;

    dailyTarget.value =
      targetResponse.data.data;
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Dashboard analytics could not be loaded.";
  } finally {
    loading.value = false;
  }
}

function viewTopicProblems(topic) {
  router.push({
    name: "problems",
    query: {
      topic,
    },
  });
}

onMounted(loadDashboard);
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">Performance overview</span>
        <h1>Dashboard</h1>

        <p>
          Monitor coding progress, topic strength,
          revision status and daily consistency.
        </p>
      </div>

      <div class="page-header__actions">
        <RouterLink
          :to="{ name: 'problem-create' }"
          class="button button--primary"
        >
          Add Coding Problem
        </RouterLink>

        <button
          type="button"
          class="button button--secondary"
          :disabled="loading"
          @click="loadDashboard"
        >
          Refresh
        </button>
      </div>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-panel"
    >
      Loading dashboard analytics...
    </div>

    <template v-else>
      <div class="stats-grid">
        <StatCard
          title="Total Problems"
          :value="summary.total_problems"
          subtitle="Problems added to your tracker"
          icon="Σ"
        />

        <StatCard
          title="Solved Problems"
          :value="summary.solved_problems"
          :subtitle="`${summary.solved_percentage}% completion rate`"
          icon="✓"
        />

        <StatCard
          title="Unsolved Problems"
          :value="summary.unsolved_problems"
          subtitle="Problems waiting to be solved"
          icon="—"
        />

        <StatCard
          title="Revision Needed"
          :value="summary.revision_needed_problems"
          subtitle="Problems requiring another attempt"
          icon="R"
        />

        <StatCard
          title="Total Attempts"
          :value="summary.total_attempts"
          :subtitle="`${summary.average_attempts_per_problem} average per problem`"
          icon="A"
        />

        <StatCard
          title="Practice Time"
          :value="formattedTime"
          subtitle="Total tracked problem-solving time"
          icon="T"
        />
      </div>

      <div class="dashboard-grid dashboard-grid--primary">
        <article class="panel">
          <div class="panel__header">
            <div>
              <span class="eyebrow">Today's plan</span>
              <h2>Daily Target</h2>
            </div>

            <RouterLink
              :to="{ name: 'daily-targets' }"
              class="text-link"
            >
              Manage target
            </RouterLink>
          </div>

          <div
            v-if="dailyTarget.target_exists"
            class="daily-target-summary"
          >
            <div class="daily-target-summary__numbers">
              <div>
                <span>Target</span>
                <strong>{{ dailyTarget.today_target }}</strong>
              </div>

              <div>
                <span>Solved</span>
                <strong>{{ dailyTarget.today_solved }}</strong>
              </div>

              <div>
                <span>Remaining</span>
                <strong>{{ dailyTarget.remaining_today }}</strong>
              </div>
            </div>

            <ProgressBar
              :value="dailyTarget.completion_percentage"
              label="Today's completion"
            />

            <p class="muted-text">
              You solved
              <strong>
                {{ dailyTarget.last_7_days_solved_count }}
              </strong>
              problems during the last seven days.
            </p>
          </div>

          <div
            v-else
            class="empty-state empty-state--compact"
          >
            <h3>No target created for today</h3>

            <p>
              Create a daily target to measure your
              completion rate.
            </p>

            <RouterLink
              :to="{ name: 'daily-targets' }"
              class="button button--primary"
            >
              Create Today's Target
            </RouterLink>
          </div>
        </article>

        <article class="panel">
          <div class="panel__header">
            <div>
              <span class="eyebrow">Revision pipeline</span>
              <h2>Revision Summary</h2>
            </div>

            <RouterLink
              :to="{ name: 'revision' }"
              class="text-link"
            >
              Open revision page
            </RouterLink>
          </div>

          <div class="revision-summary-grid">
            <div>
              <span>Not Started</span>
              <strong>
                {{ revisionCounts["Not Started"] }}
              </strong>
            </div>

            <div>
              <span>First Revision</span>
              <strong>
                {{ revisionCounts["First Revision"] }}
              </strong>
            </div>

            <div>
              <span>Second Revision</span>
              <strong>
                {{ revisionCounts["Second Revision"] }}
              </strong>
            </div>

            <div>
              <span>Mastered</span>
              <strong>
                {{ revisionCounts.Mastered }}
              </strong>
            </div>
          </div>
        </article>
      </div>

      <article class="panel">
        <div class="panel__header">
          <div>
            <span class="eyebrow">Topic analysis</span>
            <h2>Topic-Wise Progress</h2>
          </div>
        </div>

        <TopicProgressTable :topics="topics" />
      </article>

      <article class="panel">
        <div class="panel__header">
          <div>
            <span class="eyebrow">Difficulty analysis</span>
            <h2>Difficulty-Wise Progress</h2>
          </div>
        </div>

        <DifficultyProgressTable
          :difficulties="difficulties"
        />
      </article>

      <article class="panel">
        <div class="panel__header">
          <div>
            <span class="eyebrow">Priority areas</span>
            <h2>Weak Topics</h2>
          </div>

          <RouterLink
            :to="{ name: 'weak-topics' }"
            class="text-link"
          >
            View full analysis
          </RouterLink>
        </div>

        <div
          v-if="topWeakTopics.length"
          class="weak-topic-grid"
        >
          <WeakTopicCard
            v-for="topic in topWeakTopics"
            :key="topic.topic"
            :topic="topic"
            @view-problems="viewTopicProblems"
          />
        </div>

        <div
          v-else
          class="empty-state empty-state--compact"
        >
          <h3>No weak topics detected</h3>

          <p>
            Add more coding problems to generate meaningful
            topic analytics.
          </p>
        </div>
      </article>
    </template>
  </section>
</template>