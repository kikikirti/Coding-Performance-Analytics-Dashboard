<script setup>
import { computed } from "vue";

const props = defineProps({
  value: {
    type: Number,
    default: 0,
  },

  label: {
    type: String,
    default: "",
  },

  showValue: {
    type: Boolean,
    default: true,
  },
});

const safeValue = computed(() => {
  const numericValue = Number(props.value) || 0;

  return Math.min(
    Math.max(numericValue, 0),
    100,
  );
});

const formattedValue = computed(() => {
  return Number.isInteger(safeValue.value)
    ? safeValue.value
    : safeValue.value.toFixed(2);
});
</script>

<template>
  <div class="progress-block">
    <div
      v-if="label || showValue"
      class="progress-block__header"
    >
      <span>{{ label }}</span>

      <strong v-if="showValue">
        {{ formattedValue }}%
      </strong>
    </div>

    <div
      class="progress"
      role="progressbar"
      :aria-valuenow="safeValue"
      aria-valuemin="0"
      aria-valuemax="100"
    >
      <div
        class="progress__fill"
        :style="{ width: `${safeValue}%` }"
      ></div>
    </div>
  </div>
</template>