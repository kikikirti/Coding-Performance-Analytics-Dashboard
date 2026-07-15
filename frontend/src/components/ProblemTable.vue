<script setup>
defineProps({
  problems: {
    type: Array,
    default: () => [],
  },

  showActions: {
    type: Boolean,
    default: true,
  },
});

defineEmits([
  "edit",
  "delete",
]);

function badgeClass(value) {
  if (!value) {
    return "";
  }

  return `badge--${value
    .toLowerCase()
    .replaceAll(" ", "-")}`;
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    },
  ).format(
    new Date(`${value}T00:00:00`),
  );
}
</script>

<template>
  <div class="table-container">
    <table class="data-table problem-table">
      <thead>
        <tr>
          <th>Problem</th>
          <th>Topic</th>
          <th>Difficulty</th>
          <th>Status</th>
          <th>Attempts</th>
          <th>Time</th>
          <th>Revision</th>
          <th>Solved Date</th>
          <th v-if="showActions">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="problem in problems"
          :key="problem.id"
        >
          <td>
            <div class="problem-title-cell">
              <strong>{{ problem.title }}</strong>

              <a
                v-if="problem.platform_link"
                :href="problem.platform_link"
                target="_blank"
                rel="noopener noreferrer"
              >
                {{ problem.platform }}
              </a>

              <span v-else>
                {{ problem.platform }}
              </span>
            </div>
          </td>

          <td>{{ problem.topic }}</td>

          <td>
            <span
              class="badge"
              :class="badgeClass(problem.difficulty)"
            >
              {{ problem.difficulty }}
            </span>
          </td>

          <td>
            <span
              class="badge"
              :class="badgeClass(problem.status)"
            >
              {{ problem.status }}
            </span>
          </td>

          <td>{{ problem.attempts }}</td>

          <td>
            {{ problem.time_spent_minutes }} min
          </td>

          <td>
            <span
              class="badge"
              :class="badgeClass(problem.revision_status)"
            >
              {{ problem.revision_status }}
            </span>
          </td>

          <td>{{ formatDate(problem.solved_date) }}</td>

          <td v-if="showActions">
            <div class="table-actions">
              <button
                type="button"
                class="button button--small button--secondary"
                @click="$emit('edit', problem.id)"
              >
                Edit
              </button>

              <button
                type="button"
                class="button button--small button--danger-outline"
                @click="$emit('delete', problem)"
              >
                Delete
              </button>
            </div>
          </td>
        </tr>

        <tr v-if="problems.length === 0">
          <td
            :colspan="showActions ? 9 : 8"
            class="empty-table-cell"
          >
            No coding problems match the selected criteria.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>