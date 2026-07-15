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
  target_date: "",
});

const formattedTime = computed(() => {
  const totalMinutes = Number(
    summary.value.total_time_spent_minutes,
  ) || 0;

  if (totalMinutes < 60) {
    return `${totalMinutes} min`;
  }

  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;

  return minutes > 0
    ? `${hours}h ${minutes}m`
    : `${hours}h`;
});

const solvedPercentageValue = computed(() => {
  return `${formatPercentage(
    summary.value.solved_percentage,
  )}%`;
});

const todayCompletionValue = computed(() => {
  if (!dailyTarget.value.target_exists) {
    return "Not Set";
  }

  return `${formatPercentage(
    dailyTarget.value.completion_percentage,
  )}%`;
});

const revisionRows = computed(() => {
  const total = Number(
    summary.value.total_problems,
  ) || 0;

  return [
    {
      status: "Not Started",
      count:
        revisionCounts.value[
          "Not Started"
        ] || 0,
    },
    {
      status: "First Revision",
      count:
        revisionCounts.value[
          "First Revision"
        ] || 0,
    },
    {
      status: "Second Revision",
      count:
        revisionCounts.value[
          "Second Revision"
        ] || 0,
    },
    {
      status: "Mastered",
      count:
        revisionCounts.value.Mastered || 0,
    },
  ].map((item) => ({
    ...item,
    percentage: calculatePercentage(
      item.count,
      total,
    ),
  }));
});

function calculatePercentage(
  value,
  total,
) {
  const numericValue =
    Number(value) || 0;

  const numericTotal =
    Number(total) || 0;

  if (numericTotal <= 0) {
    return 0;
  }

  return Math.min(
    Math.round(
      (
        numericValue /
        numericTotal
      ) *
        10000,
    ) / 100,
    100,
  );
}

function formatPercentage(value) {
  const numericValue =
    Number(value) || 0;

  return Number.isInteger(numericValue)
    ? numericValue
    : numericValue.toFixed(2);
}

function formatTargetDate(value) {
  if (!value) {
    return "Today";
  }

  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    },
  ).format(
    new Date(`${value}T00:00:00`),
  );
}

function weaknessSummary(topic) {
  if (
    Array.isArray(
      topic.weakness_reasons,
    ) &&
    topic.weakness_reasons.length > 0
  ) {
    return topic.weakness_reasons.join(
      " ",
    );
  }

  return "This topic needs additional practice.";
}

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
      api.get(
        "/api/dashboard/summary",
      ),
      api.get(
        "/api/dashboard/topic-progress",
      ),
      api.get(
        "/api/dashboard/difficulty-progress",
      ),
      api.get(
        "/api/dashboard/weak-topics",
      ),
      api.get(
        "/api/dashboard/revision-summary",
      ),
      api.get(
        "/api/dashboard/daily-target-summary",
      ),
    ]);

    summary.value =
      summaryResponse.data.data;

    topics.value =
      topicResponse.data.data.topics ||
      [];

    difficulties.value =
      difficultyResponse.data.data
        .difficulties || [];

    weakTopics.value =
      weakResponse.data.data
        .weak_topics || [];

    revisionCounts.value =
      revisionResponse.data.data
        .revision_status_counts ||
      revisionCounts.value;

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
        <span class="eyebrow">
          Performance overview
        </span>

        <h1>
          Coding Performance Dashboard
        </h1>

        <p>
          Review overall progress, topic
          performance, weak areas, revision
          stages, and today's coding target.
        </p>
      </div>

      <div class="page-header__actions">
        <RouterLink
          :to="{
            name: 'problem-create',
          }"
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
          {{
            loading
              ? "Refreshing..."
              : "Refresh"
          }}
        </button>
      </div>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
      role="alert"
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
      <div class="dashboard-stat-grid">
        <StatCard
          title="Total Problems"
          :value="
            summary.total_problems
          "
          subtitle="All problems in the tracker"
          icon="Σ"
        />

        <StatCard
          title="Solved Problems"
          :value="
            summary.solved_problems
          "
          subtitle="Problems completed successfully"
          icon="✓"
        />

        <StatCard
          title="Unsolved Problems"
          :value="
            summary.unsolved_problems
          "
          subtitle="Problems still pending"
          icon="U"
        />

        <StatCard
          title="Revision Needed"
          :value="
            summary.revision_needed_problems
          "
          subtitle="Problems requiring another attempt"
          icon="R"
        />

        <StatCard
          title="Solved Percentage"
          :value="
            solvedPercentageValue
          "
          subtitle="Solved problems divided by total problems"
          icon="%"
        />

        <StatCard
          title="Total Attempts"
          :value="
            summary.total_attempts
          "
          :subtitle="
            `${summary.average_attempts_per_problem} average attempts per problem`
          "
          icon="A"
        />

        <StatCard
          title="Total Time Spent"
          :value="formattedTime"
          subtitle="Recorded problem-solving time"
          icon="T"
        />

        <StatCard
          title="Today's Target Completion"
          :value="
            todayCompletionValue
          "
          :subtitle="
            dailyTarget.target_exists
              ? `${dailyTarget.today_solved} of ${dailyTarget.today_target} solved today`
              : 'Create a daily target to track completion'
          "
          icon="D"
        />
      </div>

      <!-- Section 1 -->
      <article
        class="
          panel
          dashboard-section
        "
      >
        <div class="panel__header">
          <div>
            <span class="eyebrow">
              Section 1
            </span>

            <h2>
              Topic-wise Progress
            </h2>

            <p>
              Compare total, solved, pending,
              and completion percentage for
              every coding topic.
            </p>
          </div>

          <RouterLink
            :to="{ name: 'problems' }"
            class="text-link"
          >
            View all problems
          </RouterLink>
        </div>

        <TopicProgressTable
          :topics="topics"
        />
      </article>

      <!-- Section 2 -->
      <article
        class="
          panel
          dashboard-section
        "
      >
        <div class="panel__header">
          <div>
            <span class="eyebrow">
              Section 2
            </span>

            <h2>
              Difficulty-wise Progress
            </h2>

            <p>
              Review Easy, Medium, and Hard
              problem counts with their solved
              percentage.
            </p>
          </div>
        </div>

        <DifficultyProgressTable
          :difficulties="
            difficulties
          "
        />
      </article>

      <!-- Section 3 -->
      <article
        class="
          panel
          dashboard-section
        "
      >
        <div class="panel__header">
          <div>
            <span class="eyebrow">
              Section 3
            </span>

            <h2>Weak Topics</h2>

            <p>
              Topics appear here when solved
              percentage is low, revision need
              is high, or average attempts are
              greater than two.
            </p>
          </div>

          <RouterLink
            :to="{
              name: 'weak-topics',
            }"
            class="text-link"
          >
            Open detailed analysis
          </RouterLink>
        </div>

        <div
          v-if="
            weakTopics.length > 0
          "
          class="table-container"
        >
          <table
            class="
              data-table
              weak-topics-table
            "
          >
            <thead>
              <tr>
                <th>Topic</th>

                <th>
                  Solved Progress
                </th>

                <th>
                  Average Attempts
                </th>

                <th>
                  Revision Needed
                </th>

                <th>Reason</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="
                  topic in weakTopics
                "
                :key="topic.topic"
              >
                <td>
                  <strong>
                    {{ topic.topic }}
                  </strong>
                </td>

                <td
                  class="
                    table-progress-cell
                  "
                >
                  <ProgressBar
                    :value="
                      topic.solved_percentage
                    "
                    :label="
                      `${topic.solved_count} of ${topic.total_count} solved`
                    "
                  />
                </td>

                <td>
                  {{
                    topic.average_attempts
                  }}
                </td>

                <td>
                  {{
                    topic.revision_needed_count
                  }}
                </td>

                <td
                  class="
                    weak-reason-cell
                  "
                >
                  {{
                    weaknessSummary(
                      topic,
                    )
                  }}
                </td>

                <td>
                  <button
                    type="button"
                    class="
                      button
                      button--small
                      button--secondary
                    "
                    @click="
                      viewTopicProblems(
                        topic.topic,
                      )
                    "
                  >
                    View Problems
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-else
          class="
            empty-state
            empty-state--compact
          "
        >
          <h3>
            No weak topics detected
          </h3>

          <p>
            Add more problems or continue
            solving to generate meaningful
            weak-topic analysis.
          </p>
        </div>
      </article>

      <div
        class="
          dashboard-two-column-grid
        "
      >
        <!-- Section 4 -->
        <article
          class="
            panel
            dashboard-section
          "
        >
          <div class="panel__header">
            <div>
              <span class="eyebrow">
                Section 4
              </span>

              <h2>
                Revision Summary
              </h2>

              <p>
                Distribution of problems
                across each revision stage.
              </p>
            </div>

            <RouterLink
              :to="{
                name: 'revision',
              }"
              class="text-link"
            >
              Manage revision
            </RouterLink>
          </div>

          <div class="table-container">
            <table
              class="
                data-table
                summary-table
              "
            >
              <thead>
                <tr>
                  <th>
                    Revision Status
                  </th>

                  <th>Count</th>

                  <th>
                    Share of Problems
                  </th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="
                    item in revisionRows
                  "
                  :key="item.status"
                >
                  <td>
                    <span
                      class="badge"
                      :class="
                        `badge--${item.status
                          .toLowerCase()
                          .replaceAll(
                            ' ',
                            '-',
                          )}`
                      "
                    >
                      {{ item.status }}
                    </span>
                  </td>

                  <td>
                    {{ item.count }}
                  </td>

                  <td
                    class="
                      table-progress-cell
                    "
                  >
                    <ProgressBar
                      :value="
                        item.percentage
                      "
                      :label="
                        `${item.count} of ${summary.total_problems}`
                      "
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <!-- Section 5 -->
        <article
          class="
            panel
            dashboard-section
          "
        >
          <div class="panel__header">
            <div>
              <span class="eyebrow">
                Section 5
              </span>

              <h2>
                Daily Target Summary
              </h2>

              <p>
                Today's target status and
                completion progress.
              </p>
            </div>

            <RouterLink
              :to="{
                name: 'daily-targets',
              }"
              class="text-link"
            >
              Manage target
            </RouterLink>
          </div>

          <template
            v-if="
              dailyTarget.target_exists
            "
          >
            <div
              class="
                daily-target-date
              "
            >
              Target date:

              <strong>
                {{
                  formatTargetDate(
                    dailyTarget.target_date,
                  )
                }}
              </strong>
            </div>

            <div
              class="table-container"
            >
              <table
                class="
                  data-table
                  summary-table
                "
              >
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Value</th>
                  </tr>
                </thead>

                <tbody>
                  <tr>
                    <td>
                      Today's Target
                    </td>

                    <td>
                      {{
                        dailyTarget.today_target
                      }}
                    </td>
                  </tr>

                  <tr>
                    <td>
                      Today's Solved Count
                    </td>

                    <td>
                      {{
                        dailyTarget.today_solved
                      }}
                    </td>
                  </tr>

                  <tr>
                    <td>
                      Remaining Count
                    </td>

                    <td>
                      {{
                        dailyTarget.remaining_today
                      }}
                    </td>
                  </tr>

                  <tr>
                    <td>
                      Completion Percentage
                    </td>

                    <td>
                      {{
                        formatPercentage(
                          dailyTarget.completion_percentage,
                        )
                      }}%
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div
              class="
                daily-target-progress
              "
            >
              <ProgressBar
                :value="
                  dailyTarget.completion_percentage
                "
                :label="
                  `${dailyTarget.today_solved} of ${dailyTarget.today_target} completed`
                "
              />
            </div>

            <p
              class="
                dashboard-note
              "
            >
              Problems solved during the
              last seven days:

              <strong>
                {{
                  dailyTarget.last_7_days_solved_count
                }}
              </strong>
            </p>
          </template>

          <div
            v-else
            class="
              empty-state
              empty-state--compact
            "
          >
            <h3>
              No target created for today
            </h3>

            <p>
              Create today's target to
              calculate remaining work and
              completion percentage.
            </p>

            <RouterLink
              :to="{
                name: 'daily-targets',
              }"
              class="
                button
                button--primary
              "
            >
              Create Today's Target
            </RouterLink>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.dashboard-stat-grid {
  display: grid;

  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );

  gap: 16px;
  margin-bottom: 24px;
}

.dashboard-section {
  scroll-margin-top: 24px;
}

.dashboard-section
  .panel__header
  p {
  max-width: 760px;
  margin: 6px 0 0;
}

.dashboard-two-column-grid {
  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );

  gap: 24px;
}

.dashboard-two-column-grid
  > .panel {
  min-width: 0;
}

.weak-topics-table {
  min-width: 1050px;
}

.weak-reason-cell {
  min-width: 290px;
  max-width: 420px;
  line-height: 1.5;
}

.summary-table {
  min-width: 520px;
}

.daily-target-date {
  margin-bottom: 16px;

  color: var(--text-secondary);
  font-size: 0.88rem;
}

.daily-target-progress {
  margin-top: 22px;
}

.dashboard-note {
  margin: 18px 0 0;
  padding: 13px 15px;

  background:
    var(--surface-muted);

  border:
    1px solid var(--border);

  border-radius:
    var(--radius-small);

  font-size: 0.86rem;
}

.empty-state--compact
  .button {
  margin-top: 14px;
}

@media (
  max-width: 1180px
) {
  .dashboard-stat-grid {
    grid-template-columns:
      repeat(
        2,
        minmax(0, 1fr)
      );
  }

  .dashboard-two-column-grid {
    grid-template-columns:
      1fr;
  }
}

@media (
  max-width: 700px
) {
  .dashboard-stat-grid {
    grid-template-columns:
      1fr;
  }

  .dashboard-stat-grid
    :deep(.stat-card) {
    min-height: auto;
  }
}
</style>