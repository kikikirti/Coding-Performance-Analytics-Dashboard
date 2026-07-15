<script setup>
const props = defineProps({
  problems: {
    type: Array,
    default: () => [],
  },

  showActions: {
    type: Boolean,
    default: true,
  },

  busyId: {
    type: [Number, String],
    default: null,
  },

  busyAction: {
    type: String,
    default: "",
  },
});

defineEmits([
  "edit",
  "delete",
  "mark-solved",
  "mark-revision",
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

function isBusy(problemId) {
  return props.busyId === problemId;
}

function actionLabel(
  problemId,
  action,
  label,
) {
  if (
    isBusy(problemId) &&
    props.busyAction === action
  ) {
    return action === "delete"
      ? "Deleting..."
      : "Updating...";
  }

  return label;
}
</script>

<template>
  <div class="table-container">
    <table class="data-table problem-table">
      <thead>
        <tr>
          <th>Title</th>
          <th>Topic</th>
          <th>Difficulty</th>
          <th>Platform</th>
          <th>Status</th>
          <th>Attempts</th>
          <th>Revision Status</th>
          <th>Solved Date</th>
          <th v-if="showActions">
            Actions
          </th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="problem in problems"
          :key="problem.id"
        >
          <td>
            <div class="problem-title-cell">
              <strong>
                {{ problem.title }}
              </strong>

              <a
                v-if="problem.platform_link"
                :href="problem.platform_link"
                target="_blank"
                rel="noopener noreferrer"
              >
                Open problem
              </a>
            </div>
          </td>

          <td>
            {{ problem.topic }}
          </td>

          <td>
            <span
              class="badge"
              :class="badgeClass(
                problem.difficulty,
              )"
            >
              {{ problem.difficulty }}
            </span>
          </td>

          <td>
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
          </td>

          <td>
            <span
              class="badge"
              :class="badgeClass(
                problem.status,
              )"
            >
              {{ problem.status }}
            </span>
          </td>

          <td>
            {{ problem.attempts }}
          </td>

          <td>
            <span
              class="badge"
              :class="badgeClass(
                problem.revision_status,
              )"
            >
              {{ problem.revision_status }}
            </span>
          </td>

          <td>
            {{ formatDate(problem.solved_date) }}
          </td>

          <td v-if="showActions">
            <div class="table-actions problem-actions">
              <button
                type="button"
                class="
                  button
                  button--small
                  button--secondary
                "
                :disabled="isBusy(problem.id)"
                @click="$emit('edit', problem.id)"
              >
                Edit
              </button>

              <button
                type="button"
                class="
                  button
                  button--small
                  button--success-outline
                "
                :disabled="
                  isBusy(problem.id) ||
                  problem.status === 'Solved'
                "
                @click="
                  $emit('mark-solved', problem)
                "
              >
                {{
                  actionLabel(
                    problem.id,
                    "Solved",
                    "Mark as Solved",
                  )
                }}
              </button>

              <button
                type="button"
                class="
                  button
                  button--small
                  button--warning-outline
                "
                :disabled="
                  isBusy(problem.id) ||
                  problem.status ===
                    'Revision Needed'
                "
                @click="
                  $emit('mark-revision', problem)
                "
              >
                {{
                  actionLabel(
                    problem.id,
                    "Revision Needed",
                    "Mark as Revision Needed",
                  )
                }}
              </button>

              <button
                type="button"
                class="
                  button
                  button--small
                  button--danger-outline
                "
                :disabled="isBusy(problem.id)"
                @click="$emit('delete', problem)"
              >
                {{
                  actionLabel(
                    problem.id,
                    "delete",
                    "Delete",
                  )
                }}
              </button>
            </div>
          </td>
        </tr>

        <tr v-if="problems.length === 0">
          <td
            :colspan="showActions ? 9 : 8"
            class="empty-table-cell"
          >
            No coding problems are available.
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.button--success-outline {
  color: var(--success);
  background: transparent;
  border-color: #9ed5bc;
}

.button--success-outline:hover:not(:disabled) {
  color: #ffffff;
  background: var(--success);
  border-color: var(--success);
}

.button--warning-outline {
  color: var(--warning);
  background: transparent;
  border-color: #e5c875;
}

.button--warning-outline:hover:not(:disabled) {
  color: #ffffff;
  background: var(--warning);
  border-color: var(--warning);
}

.problem-actions {
  flex-wrap: wrap;
  min-width: 420px;
}
</style>