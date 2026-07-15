<script setup>
import ProgressBar from "./ProgressBar.vue";

defineProps({
  topics: {
    type: Array,
    default: () => [],
  },
});

function pendingCount(topic) {
  const total =
    Number(topic.total_count) || 0;

  const solved =
    Number(topic.solved_count) || 0;

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
        topic-progress-table
      "
    >
      <thead>
        <tr>
          <th>Topic</th>

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
          v-for="topic in topics"
          :key="topic.topic"
        >
          <td>
            <strong>
              {{ topic.topic }}
            </strong>
          </td>

          <td>
            {{ topic.total_count }}
          </td>

          <td>
            {{ topic.solved_count }}
          </td>

          <td>
            {{
              pendingCount(topic)
            }}
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
                `${topic.solved_percentage}% solved`
              "
              :show-value="false"
            />
          </td>
        </tr>

        <tr
          v-if="
            topics.length === 0
          "
        >
          <td
            colspan="5"
            class="empty-table-cell"
          >
            No topic progress is
            available yet.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.topic-progress-table {
  min-width: 820px;
}
</style>