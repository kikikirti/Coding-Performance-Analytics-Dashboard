<script setup>
import {
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
const criteria = ref({});

async function loadWeakTopics() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get(
      "/api/dashboard/weak-topics",
    );

    weakTopics.value =
      response.data.data.weak_topics;

    criteria.value =
      response.data.data.criteria;
  } catch (error) {
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
        <span class="eyebrow">Priority analysis</span>
        <h1>Weak Topics</h1>

        <p>
          Focus preparation on topics with low solved rates,
          repeated attempts or high revision requirements.
        </p>
      </div>

      <button
        type="button"
        class="button button--secondary"
        :disabled="loading"
        @click="loadWeakTopics"
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

    <article class="panel criteria-panel">
      <div>
        <span class="eyebrow">Detection criteria</span>
        <h2>How Weak Topics Are Identified</h2>
      </div>

      <div class="criteria-grid">
        <div>
          <strong>Below 60%</strong>
          <span>Solved percentage</span>
        </div>

        <div>
          <strong>
            {{
              criteria.high_revision_needed_count || 2
            }}+
          </strong>

          <span>Revision-needed problems</span>
        </div>

        <div>
          <strong>
            Above
            {{
              criteria.maximum_average_attempts || 2
            }}
          </strong>

          <span>Average attempts</span>
        </div>
      </div>
    </article>

    <div
      v-if="loading"
      class="loading-panel"
    >
      Loading weak-topic analytics...
    </div>

    <div
      v-else-if="weakTopics.length"
      class="weak-topic-grid"
    >
      <WeakTopicCard
        v-for="topic in weakTopics"
        :key="topic.topic"
        :topic="topic"
        @view-problems="viewTopicProblems"
      />
    </div>

    <div
      v-else
      class="empty-state"
    >
      <h2>No Weak Topics Detected</h2>

      <p>
        Your current records do not meet the weak-topic
        criteria, or more problem data is required.
      </p>

      <RouterLink
        :to="{ name: 'problem-create' }"
        class="button button--primary"
      >
        Add Coding Problem
      </RouterLink>
    </div>
  </section>
</template>