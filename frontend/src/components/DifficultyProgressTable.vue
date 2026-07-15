<script setup>
defineProps({
  difficulties: {
    type: Array,
    default: () => [],
  },
});
</script>

<template>
  <div class="table-container">
    <table class="data-table">
      <thead>
        <tr>
          <th>Difficulty</th>
          <th>Total Problems</th>
          <th>Solved Problems</th>
          <th>Solved Percentage</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="item in difficulties"
          :key="item.difficulty"
        >
          <td>
            <span
              class="badge"
              :class="`badge--${item.difficulty.toLowerCase()}`"
            >
              {{ item.difficulty }}
            </span>
          </td>

          <td>{{ item.total_count }}</td>
          <td>{{ item.solved_count }}</td>

          <td class="table-progress-cell">
            <ProgressBar
              :value="item.solved_percentage"
              :label="`${item.solved_percentage}% solved`"
              :show-value="false"
            />
          </td>
        </tr>

        <tr v-if="difficulties.length === 0">
          <td
            colspan="4"
            class="empty-table-cell"
          >
            No difficulty data is available.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>