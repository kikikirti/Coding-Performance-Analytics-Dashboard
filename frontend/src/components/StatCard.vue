<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },

  value: {
    type: [String, Number],
    default: 0,
  },

  subtitle: {
    type: String,
    default: "",
  },

  icon: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <article class="stat-card">
    <div class="stat-card__header">
      <span class="stat-card__title">
        {{ title }}
      </span>

      <span
        v-if="icon"
        class="stat-card__icon"
      >
        {{ icon }}
      </span>
    </div>

    <strong class="stat-card__value">
      {{ value }}
    </strong>

    <p
      v-if="subtitle"
      class="stat-card__subtitle"
    >
      {{ subtitle }}
    </p>
  </article>
</template>