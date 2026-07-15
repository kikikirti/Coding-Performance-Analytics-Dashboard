<script setup>
defineProps({
  topics: {
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
          <th>Topic</th>
          <th>Total</th>
          <th>Solved</th>
          <th>Unsolved</th>
          <th>Revision Needed</th>
          <th>Progress</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="topic in topics"
          :key="topic.topic"
        >
          <td>
            <strong>{{ topic.topic }}</strong>
          </td>

          <td>{{ topic.total_count }}</td>
          <td>{{ topic.solved_count }}</td>
          <td>{{ topic.unsolved_count }}</td>
          <td>{{ topic.revision_needed_count }}</td>

          <td class="table-progress-cell">
            <ProgressBar
              :value="topic.solved_percentage"
              :label="`${topic.solved_percentage}% solved`"
              :show-value="false"
            />
          </td>
        </tr>

        <tr v-if="topics.length === 0">
          <td
            colspan="6"
            class="empty-table-cell"
          >
            No topic data is available.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>