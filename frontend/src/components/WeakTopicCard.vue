<script setup>
defineProps({
  topic: {
    type: Object,
    required: true,
  },
});

defineEmits(["view-problems"]);
</script>

<template>
  <article class="weak-topic-card">
    <div class="weak-topic-card__header">
      <div>
        <span class="eyebrow">Weak topic</span>
        <h3>{{ topic.topic }}</h3>
      </div>

      <strong class="weak-topic-card__percentage">
        {{ topic.solved_percentage }}%
      </strong>
    </div>

    <ProgressBar
      :value="topic.solved_percentage"
      label="Solved progress"
    />

    <div class="weak-topic-card__metrics">
      <div>
        <span>Total</span>
        <strong>{{ topic.total_count }}</strong>
      </div>

      <div>
        <span>Solved</span>
        <strong>{{ topic.solved_count }}</strong>
      </div>

      <div>
        <span>Needs revision</span>
        <strong>{{ topic.revision_needed_count }}</strong>
      </div>

      <div>
        <span>Average attempts</span>
        <strong>{{ topic.average_attempts }}</strong>
      </div>
    </div>

    <div class="weak-topic-card__reasons">
      <strong>Why this topic needs attention</strong>

      <ul>
        <li
          v-for="reason in topic.weakness_reasons"
          :key="reason"
        >
          {{ reason }}
        </li>
      </ul>
    </div>

    <button
      type="button"
      class="button button--secondary button--full"
      @click="$emit('view-problems', topic.topic)"
    >
      View {{ topic.topic }} Problems
    </button>
  </article>
</template>