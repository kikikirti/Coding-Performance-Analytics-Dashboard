<script setup>
import ProgressBar from "./ProgressBar.vue";

defineProps({
  difficulties: {
    type: Array,
    default: () => [],
  },
});

function pendingCount(item) {
  const total =
    Number(item.total_count) || 0;

  const solved =
    Number(item.solved_count) || 0;

  return Math.max(
    total - solved,
    0,
  );
}
</script>

<template>
  <div class="table-container">
    <table
      class="
        data-table
        difficulty-progress-table
      "
    >
      <thead>
        <tr>
          <th>Difficulty</th>

          <th>
            Total Problems
          </th>

          <th>
            Solved Count
          </th>

          <th>
            Pending Count
          </th>

          <th>
            Solved Percentage
          </th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="
            item in difficulties
          "
          :key="item.difficulty"
        >
          <td>
            <span
              class="badge"
              :class="
                `badge--${item.difficulty.toLowerCase()}`
              "
            >
              {{ item.difficulty }}
            </span>
          </td>

          <td>
            {{ item.total_count }}
          </td>

          <td>
            {{ item.solved_count }}
          </td>

          <td>
            {{
              pendingCount(item)
            }}
          </td>

          <td
            class="
              table-progress-cell
            "
          >
            <ProgressBar
              :value="
                item.solved_percentage
              "
              :label="
                `${item.solved_percentage}% solved`
              "
              :show-value="false"
            />
          </td>
        </tr>

        <tr
          v-if="
            difficulties.length === 0
          "
        >
          <td
            colspan="5"
            class="empty-table-cell"
          >
            No difficulty progress is
            available yet.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.difficulty-progress-table {
  min-width: 820px;
}
</style>