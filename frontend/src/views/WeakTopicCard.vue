<script setup>
import { computed } from "vue";

import ProgressBar from "./ProgressBar.vue";

const props = defineProps({
  topic: {
    type: Object,
    required: true,
  },
});

defineEmits([
  "view-problems",
]);

const weaknessReasons = computed(() => {
  if (
    Array.isArray(
      props.topic.weakness_reasons,
    ) &&
    props.topic.weakness_reasons.length > 0
  ) {
    return props.topic.weakness_reasons;
  }

  const reasons = [];

  const solvedPercentage =
    Number(
      props.topic.solved_percentage,
    ) || 0;

  const revisionNeededCount =
    Number(
      props.topic.revision_needed_count,
    ) || 0;

  const averageAttempts =
    Number(
      props.topic.average_attempts,
    ) || 0;

  if (solvedPercentage < 60) {
    reasons.push(
      "Low solved percentage",
    );
  }

  if (revisionNeededCount >= 2) {
    reasons.push(
      "Too many revision-needed problems",
    );
  }

  if (averageAttempts > 2) {
    reasons.push(
      "High average attempts",
    );
  }

  return reasons;
});

const recommendations = computed(() => {
  if (
    Array.isArray(
      props.topic.recommendations,
    ) &&
    props.topic.recommendations.length > 0
  ) {
    return props.topic.recommendations;
  }

  const messages = [];

  const solvedPercentage =
    Number(
      props.topic.solved_percentage,
    ) || 0;

  const revisionNeededCount =
    Number(
      props.topic.revision_needed_count,
    ) || 0;

  const averageAttempts =
    Number(
      props.topic.average_attempts,
    ) || 0;

  if (solvedPercentage < 60) {
    messages.push(
      "Practice more basic and medium-level problems in this topic.",
    );
  }

  if (averageAttempts > 2) {
    messages.push(
      "Revise core concepts and solve similar problems again.",
    );
  }

  if (revisionNeededCount >= 2) {
    messages.push(
      "Schedule revision for previously solved problems.",
    );
  }

  return messages;
});

function reasonClass(reason) {
  if (
    reason ===
    "Low solved percentage"
  ) {
    return "reason-badge--percentage";
  }

  if (
    reason ===
    "Too many revision-needed problems"
  ) {
    return "reason-badge--revision";
  }

  return "reason-badge--attempts";
}
</script>

<template>
  <article class="weak-topic-card">
    <div class="weak-topic-card__header">
      <div>
        <span class="eyebrow">
          Weak topic
        </span>

        <h3>
          {{ topic.topic }}
        </h3>
      </div>

      <div class="weak-topic-card__score">
        <strong>
          {{ topic.solved_percentage }}%
        </strong>

        <span>
          Solved
        </span>
      </div>
    </div>

    <ProgressBar
      :value="
        topic.solved_percentage
      "
      :label="
        `${topic.solved_count} of ${topic.total_count} problems solved`
      "
    />

    <div class="weak-topic-card__metrics">
      <div>
        <span>
          Total Problems
        </span>

        <strong>
          {{ topic.total_count }}
        </strong>
      </div>

      <div>
        <span>
          Solved Problems
        </span>

        <strong>
          {{ topic.solved_count }}
        </strong>
      </div>

      <div>
        <span>
          Revision Needed
        </span>

        <strong>
          {{
            topic.revision_needed_count
          }}
        </strong>
      </div>

      <div>
        <span>
          Average Attempts
        </span>

        <strong>
          {{ topic.average_attempts }}
        </strong>
      </div>
    </div>

    <section class="weak-topic-card__section">
      <h4>
        Why This Topic Is Weak
      </h4>

      <div class="weak-topic-card__reason-list">
        <span
          v-for="reason in weaknessReasons"
          :key="reason"
          class="reason-badge"
          :class="reasonClass(reason)"
        >
          {{ reason }}
        </span>
      </div>
    </section>

    <section
      class="
        weak-topic-card__section
        recommendation-box
      "
    >
      <h4>
        Rule-based Recommendation
      </h4>

      <ul
        v-if="
          recommendations.length > 0
        "
      >
        <li
          v-for="
            recommendation in
            recommendations
          "
          :key="recommendation"
        >
          {{ recommendation }}
        </li>
      </ul>

      <p v-else>
        Continue practising this topic and review
        performance after adding more problem
        records.
      </p>
    </section>

    <button
      type="button"
      class="
        button
        button--secondary
        button--full
      "
      @click="
        $emit(
          'view-problems',
          topic.topic,
        )
      "
    >
      View {{ topic.topic }} Problems
    </button>
  </article>
</template>

<style scoped>
.weak-topic-card {
  min-width: 0;
}

.weak-topic-card__score {
  min-width: 82px;
  text-align: right;
}

.weak-topic-card__score strong,
.weak-topic-card__score span {
  display: block;
}

.weak-topic-card__score strong {
  color: var(--danger);
  font-size: 1.5rem;
}

.weak-topic-card__score span {
  margin-top: 2px;

  color: var(--text-muted);

  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
}

.weak-topic-card__section {
  padding-top: 16px;

  border-top:
    1px solid var(--border);
}

.weak-topic-card__section h4 {
  margin: 0 0 11px;
  font-size: 0.84rem;
}

.weak-topic-card__reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reason-badge {
  display: inline-flex;
  align-items: center;

  min-height: 28px;
  padding: 6px 9px;

  border-radius: 999px;

  font-size: 0.72rem;
  font-weight: 750;
  line-height: 1.25;
}

.reason-badge--percentage {
  color: var(--danger);
  background: var(--danger-soft);
}

.reason-badge--revision {
  color: var(--warning);
  background: var(--warning-soft);
}

.reason-badge--attempts {
  color: #5942a8;
  background: #f1edff;
}

.recommendation-box {
  flex: 1;

  padding: 15px;

  background:
    var(--primary-soft);

  border:
    1px solid #d8e0ff;

  border-radius:
    var(--radius-small);
}

.recommendation-box h4 {
  color: var(--primary-dark);
}

.recommendation-box ul {
  margin: 0;
  padding-left: 19px;

  color: var(--text-secondary);

  font-size: 0.82rem;
}

.recommendation-box li {
  margin-bottom: 7px;
  line-height: 1.5;
}

.recommendation-box li:last-child {
  margin-bottom: 0;
}

.recommendation-box p {
  margin: 0;

  color: var(--text-secondary);

  font-size: 0.82rem;
  line-height: 1.5;
}
</style>