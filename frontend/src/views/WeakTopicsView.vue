<script setup>
import {
  computed,
  onMounted,
  ref,
} from "vue";

import { useRouter } from "vue-router";

import api from "../api/axios";
import WeakTopicCard from "../components/WeakTopicCard.vue";

const router = useRouter();

const loading = ref(false);
const errorMessage = ref("");
const weakTopics = ref([]);

const criteria = ref({
  maximum_strong_solved_percentage: 60,
  high_revision_needed_count: 2,
  maximum_average_attempts: 2,
});

const weakTopicCount = computed(
  () => weakTopics.value.length,
);

const lowestSolvedPercentage = computed(() => {
  if (weakTopics.value.length === 0) {
    return 0;
  }

  return Math.min(
    ...weakTopics.value.map(
      (topic) =>
        Number(topic.solved_percentage) || 0,
    ),
  );
});

const totalRevisionNeeded = computed(() => {
  return weakTopics.value.reduce(
    (total, topic) =>
      total +
      (
        Number(
          topic.revision_needed_count,
        ) || 0
      ),
    0,
  );
});

const highestAverageAttempts = computed(() => {
  if (weakTopics.value.length === 0) {
    return 0;
  }

  return Math.max(
    ...weakTopics.value.map(
      (topic) =>
        Number(topic.average_attempts) || 0,
    ),
  );
});

function normalizedCriteria() {
  return {
    solvedPercentage:
      Number(
        criteria.value
          .maximum_strong_solved_percentage,
      ) || 60,

    revisionNeeded:
      Number(
        criteria.value
          .high_revision_needed_count,
      ) || 2,

    averageAttempts:
      Number(
        criteria.value
          .maximum_average_attempts,
      ) || 2,
  };
}

function buildReasons(topic) {
  const thresholds = normalizedCriteria();
  const reasons = [];

  if (
    Number(topic.solved_percentage) <
    thresholds.solvedPercentage
  ) {
    reasons.push(
      "Low solved percentage",
    );
  }

  if (
    Number(
      topic.revision_needed_count,
    ) >= thresholds.revisionNeeded
  ) {
    reasons.push(
      "Too many revision-needed problems",
    );
  }

  if (
    Number(topic.average_attempts) >
    thresholds.averageAttempts
  ) {
    reasons.push(
      "High average attempts",
    );
  }

  return reasons;
}

function buildRecommendations(topic) {
  const thresholds = normalizedCriteria();
  const recommendations = [];

  if (
    Number(topic.solved_percentage) <
    thresholds.solvedPercentage
  ) {
    recommendations.push(
      "Practice more basic and medium-level problems in this topic.",
    );
  }

  if (
    Number(topic.average_attempts) >
    thresholds.averageAttempts
  ) {
    recommendations.push(
      "Revise core concepts and solve similar problems again.",
    );
  }

  if (
    Number(
      topic.revision_needed_count,
    ) >= thresholds.revisionNeeded
  ) {
    recommendations.push(
      "Schedule revision for previously solved problems.",
    );
  }

  return recommendations;
}

function enhanceTopic(topic) {
  return {
    ...topic,

    weakness_reasons:
      buildReasons(topic),

    recommendations:
      buildRecommendations(topic),
  };
}

async function loadWeakTopics() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get(
      "/api/dashboard/weak-topics",
    );

    const responseData =
      response.data?.data || {};

    criteria.value = {
      ...criteria.value,
      ...(responseData.criteria || {}),
    };

    weakTopics.value = (
      responseData.weak_topics || []
    ).map(enhanceTopic);
  } catch (error) {
    weakTopics.value = [];

    errorMessage.value =
      error.response?.data?.message ||
      "Weak-topic analytics could not be loaded.";
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

onMounted(loadWeakTopics);
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">
          Priority analysis
        </span>

        <h1>Weak Topics</h1>

        <p>
          Identify topics that need additional
          practice, concept revision, or scheduled
          reattempts using fixed performance rules.
        </p>
      </div>

      <div class="page-header__actions">
        <RouterLink
          :to="{ name: 'problems' }"
          class="button button--secondary"
        >
          View Problems
        </RouterLink>

        <button
          type="button"
          class="button button--primary"
          :disabled="loading"
          @click="loadWeakTopics"
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

    <article class="panel criteria-panel">
      <div>
        <span class="eyebrow">
          Rule-based detection
        </span>

        <h2>
          How a Topic Is Marked Weak
        </h2>

        <p>
          A topic is included when it meets at
          least one of these transparent rules.
          Recommendations are selected from fixed
          rules and are not AI-generated.
        </p>
      </div>

      <div class="criteria-grid">
        <div>
          <strong>
            Below
            {{
              criteria
                .maximum_strong_solved_percentage
            }}%
          </strong>

          <span>
            Low solved percentage
          </span>
        </div>

        <div>
          <strong>
            {{
              criteria
                .high_revision_needed_count
            }}+
          </strong>

          <span>
            Revision-needed problems
          </span>
        </div>

        <div>
          <strong>
            Above
            {{
              criteria
                .maximum_average_attempts
            }}
          </strong>

          <span>
            Average attempts
          </span>
        </div>
      </div>
    </article>

    <div
      v-if="loading"
      class="loading-panel"
    >
      Loading weak-topic analytics...
    </div>

    <template
      v-else-if="
        weakTopics.length > 0
      "
    >
      <div class="weak-topic-summary-grid">
        <article class="weak-summary-card">
          <span>Weak Topics</span>

          <strong>
            {{ weakTopicCount }}
          </strong>

          <small>
            Topics requiring attention
          </small>
        </article>

        <article class="weak-summary-card">
          <span>Lowest Solved Rate</span>

          <strong>
            {{ lowestSolvedPercentage }}%
          </strong>

          <small>
            Lowest completion among weak topics
          </small>
        </article>

        <article class="weak-summary-card">
          <span>Revision Needed</span>

          <strong>
            {{ totalRevisionNeeded }}
          </strong>

          <small>
            Problems awaiting revision
          </small>
        </article>

        <article class="weak-summary-card">
          <span>
            Highest Average Attempts
          </span>

          <strong>
            {{ highestAverageAttempts }}
          </strong>

          <small>
            Maximum topic-level average
          </small>
        </article>
      </div>

      <div class="weak-topic-grid">
        <WeakTopicCard
          v-for="topic in weakTopics"
          :key="topic.topic"
          :topic="topic"
          @view-problems="
            viewTopicProblems
          "
        />
      </div>
    </template>

    <div
      v-else
      class="empty-state"
    >
      <h2>
        No Weak Topics Detected
      </h2>

      <p>
        None of the available topics currently
        meet the low-solved-rate,
        revision-needed, or high-attempt rules.
        More problem records may be needed for
        meaningful analysis.
      </p>

      <RouterLink
        :to="{
          name: 'problem-create',
        }"
        class="button button--primary"
      >
        Add Coding Problem
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.criteria-panel p {
  margin: 8px 0 0;
}

.weak-topic-summary-grid {
  display: grid;

  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );

  gap: 14px;
  margin: 22px 0;
}

.weak-summary-card {
  padding: 18px;

  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);

  box-shadow: var(--shadow-small);
}

.weak-summary-card span,
.weak-summary-card small {
  display: block;
  color: var(--text-muted);
}

.weak-summary-card span {
  margin-bottom: 8px;

  font-size: 0.75rem;
  font-weight: 750;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.weak-summary-card strong {
  display: block;

  margin-bottom: 6px;

  font-size: 1.7rem;
}

.weak-summary-card small {
  line-height: 1.45;
}

@media (max-width: 1050px) {
  .weak-topic-summary-grid {
    grid-template-columns:
      repeat(
        2,
        minmax(0, 1fr)
      );
  }
}

@media (max-width: 620px) {
  .weak-topic-summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>