<script setup>
import {
  onMounted,
  reactive,
  ref,
} from "vue";

import api from "../api/axios";
import ProgressBar from "../components/ProgressBar.vue";

function localDateString(dateValue = new Date()) {
  const timezoneOffset =
    dateValue.getTimezoneOffset() * 60000;

  return new Date(
    dateValue.getTime() - timezoneOffset,
  )
    .toISOString()
    .slice(0, 10);
}

const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

const targets = ref([]);
const todayTarget = ref(null);
const editingTargetId = ref(null);

const form = reactive({
  target_date: localDateString(),
  target_count: 3,
});

function resetForm() {
  editingTargetId.value = null;
  form.target_date = localDateString();
  form.target_count = 3;
}

function formatDate(value) {
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

async function loadTodayTarget() {
  try {
    const response = await api.get(
      "/api/daily-targets/today",
    );

    todayTarget.value =
      response.data.data.daily_target;
  } catch (error) {
    if (error.response?.status === 404) {
      todayTarget.value = null;
      return;
    }

    throw error;
  }
}

async function loadTargets() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get(
      "/api/daily-targets",
    );

    targets.value =
      response.data.data.daily_targets;

    await loadTodayTarget();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Daily targets could not be loaded.";
  } finally {
    loading.value = false;
  }
}

async function saveTarget() {
  saving.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  const payload = {
    target_date: form.target_date,
    target_count: Number(form.target_count),
  };

  try {
    if (editingTargetId.value) {
      await api.put(
        `/api/daily-targets/${editingTargetId.value}`,
        payload,
      );

      successMessage.value =
        "Daily target updated successfully.";
    } else {
      await api.post(
        "/api/daily-targets",
        payload,
      );

      successMessage.value =
        "Daily target created successfully.";
    }

    resetForm();
    await loadTargets();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The daily target could not be saved.";
  } finally {
    saving.value = false;
  }
}

function editTarget(target) {
  editingTargetId.value = target.id;
  form.target_date = target.target_date;
  form.target_count = target.target_count;

  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

async function deleteTarget(target) {
  const confirmed = window.confirm(
    `Delete the target for ${formatDate(target.target_date)}?`,
  );

  if (!confirmed) {
    return;
  }

  errorMessage.value = "";
  successMessage.value = "";

  try {
    await api.delete(
      `/api/daily-targets/${target.id}`,
    );

    successMessage.value =
      "Daily target deleted successfully.";

    if (editingTargetId.value === target.id) {
      resetForm();
    }

    await loadTargets();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "The target could not be deleted.";
  }
}

onMounted(loadTargets);
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">Consistency tracker</span>
        <h1>Daily Targets</h1>

        <p>
          Plan daily coding goals and automatically measure
          completion using solved problem dates.
        </p>
      </div>

      <button
        type="button"
        class="button button--secondary"
        :disabled="loading"
        @click="loadTargets"
      >
        Refresh
      </button>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="alert alert--success"
    >
      {{ successMessage }}
    </div>

    <div class="dashboard-grid dashboard-grid--primary">
      <article class="panel">
        <div class="panel__header">
          <div>
            <span class="eyebrow">
              {{
                editingTargetId
                  ? "Update target"
                  : "Create target"
              }}
            </span>

            <h2>
              {{
                editingTargetId
                  ? "Edit Daily Target"
                  : "New Daily Target"
              }}
            </h2>
          </div>
        </div>

        <form
          class="form"
          @submit.prevent="saveTarget"
        >
          <div class="form-grid">
            <div class="form-group">
              <label for="target-date">
                Target Date
              </label>

              <input
                id="target-date"
                v-model="form.target_date"
                type="date"
                required
              />
            </div>

            <div class="form-group">
              <label for="target-count">
                Problem Target
              </label>

              <input
                id="target-count"
                v-model.number="form.target_count"
                type="number"
                min="1"
                step="1"
                required
              />
            </div>
          </div>

          <div class="form-actions">
            <button
              v-if="editingTargetId"
              type="button"
              class="button button--secondary"
              @click="resetForm"
            >
              Cancel Edit
            </button>

            <button
              type="submit"
              class="button button--primary"
              :disabled="saving"
            >
              {{
                saving
                  ? "Saving..."
                  : editingTargetId
                    ? "Update Target"
                    : "Create Target"
              }}
            </button>
          </div>
        </form>
      </article>

      <article class="panel">
        <div class="panel__header">
          <div>
            <span class="eyebrow">Today's progress</span>
            <h2>Current Target</h2>
          </div>
        </div>

        <div
          v-if="todayTarget"
          class="daily-target-summary"
        >
          <div class="daily-target-summary__numbers">
            <div>
              <span>Target</span>
              <strong>{{ todayTarget.target_count }}</strong>
            </div>

            <div>
              <span>Solved</span>
              <strong>{{ todayTarget.solved_count }}</strong>
            </div>

            <div>
              <span>Status</span>
              <strong>
                {{
                  todayTarget.is_completed
                    ? "Completed"
                    : "In progress"
                }}
              </strong>
            </div>
          </div>

          <ProgressBar
            :value="todayTarget.completion_percentage"
            label="Today's completion"
          />

          <p class="muted-text">
            Solved count is calculated automatically from
            problems solved today.
          </p>
        </div>

        <div
          v-else
          class="empty-state empty-state--compact"
        >
          <h3>No target for today</h3>

          <p>
            Use the form to create a target for the current
            date.
          </p>
        </div>
      </article>
    </div>

    <article class="panel">
      <div class="panel__header">
        <div>
          <span class="eyebrow">Target history</span>
          <h2>Daily Target Records</h2>
        </div>
      </div>

      <div
        v-if="loading"
        class="loading-panel"
      >
        Loading daily targets...
      </div>

      <div
        v-else
        class="table-container"
      >
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Target</th>
              <th>Solved</th>
              <th>Completion</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="target in targets"
              :key="target.id"
            >
              <td>
                <strong>
                  {{ formatDate(target.target_date) }}
                </strong>
              </td>

              <td>{{ target.target_count }}</td>
              <td>{{ target.solved_count }}</td>

              <td class="table-progress-cell">
                <ProgressBar
                  :value="target.completion_percentage"
                  :label="`${target.completion_percentage}%`"
                  :show-value="false"
                />
              </td>

              <td>
                <span
                  class="badge"
                  :class="
                    target.is_completed
                      ? 'badge--solved'
                      : 'badge--unsolved'
                  "
                >
                  {{
                    target.is_completed
                      ? "Completed"
                      : "In Progress"
                  }}
                </span>
              </td>

              <td>
                <div class="table-actions">
                  <button
                    type="button"
                    class="button button--small button--secondary"
                    @click="editTarget(target)"
                  >
                    Edit
                  </button>

                  <button
                    type="button"
                    class="button button--small button--danger-outline"
                    @click="deleteTarget(target)"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="targets.length === 0">
              <td
                colspan="6"
                class="empty-table-cell"
              >
                No daily targets have been created.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
  </section>
</template>