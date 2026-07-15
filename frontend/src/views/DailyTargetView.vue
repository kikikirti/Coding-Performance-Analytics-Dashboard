<script setup>
import {
  computed,
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

function dateFromLocalString(value) {
  return new Date(`${value}T00:00:00`);
}

const todayDate = localDateString();

const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const fieldErrors = ref({});

const targets = ref([]);
const todayTarget = ref(null);

const form = reactive({
  target_date: todayDate,
  target_count: 3,
});

const todayRemaining = computed(() => {
  if (!todayTarget.value) {
    return 0;
  }

  return Math.max(
    Number(todayTarget.value.target_count) -
      Number(todayTarget.value.solved_count),
    0,
  );
});

const lastSevenDays = computed(() => {
  const targetsByDate = new Map(
    targets.value.map((target) => [
      target.target_date,
      target,
    ]),
  );

  return Array.from(
    {
      length: 7,
    },
    (_, index) => {
      const dateValue = new Date();

      dateValue.setHours(0, 0, 0, 0);

      dateValue.setDate(
        dateValue.getDate() - (6 - index),
      );

      const dateKey =
        localDateString(dateValue);

      const target =
        targetsByDate.get(dateKey);

      if (!target) {
        return {
          id: `empty-${dateKey}`,
          target_date: dateKey,
          target_count: 0,
          solved_count: 0,
          completion_percentage: 0,
          remaining_count: 0,
          is_completed: false,
          target_exists: false,
        };
      }

      return {
        ...target,

        remaining_count: Math.max(
          Number(target.target_count) -
            Number(target.solved_count),
          0,
        ),

        target_exists: true,
      };
    },
  );
});

const sevenDaySummary = computed(() => {
  const targetDays =
    lastSevenDays.value.filter(
      (day) => day.target_exists,
    );

  return {
    target_days: targetDays.length,

    completed_days: targetDays.filter(
      (day) => day.is_completed,
    ).length,

    total_target: targetDays.reduce(
      (total, day) =>
        total +
        Number(day.target_count || 0),
      0,
    ),

    total_solved: targetDays.reduce(
      (total, day) =>
        total +
        Number(day.solved_count || 0),
      0,
    ),
  };
});

function firstError(fieldName) {
  const error =
    fieldErrors.value[fieldName];

  if (Array.isArray(error)) {
    return error[0] || "";
  }

  return typeof error === "string"
    ? error
    : "";
}

function clearFieldError(fieldName) {
  if (!fieldErrors.value[fieldName]) {
    return;
  }

  const nextErrors = {
    ...fieldErrors.value,
  };

  delete nextErrors[fieldName];

  fieldErrors.value = nextErrors;
}

function normalizeApiErrors(errors) {
  if (
    !errors ||
    typeof errors !== "object"
  ) {
    return {};
  }

  return Object.fromEntries(
    Object.entries(errors).map(
      ([fieldName, messages]) => [
        fieldName,

        Array.isArray(messages)
          ? messages
          : [String(messages)],
      ],
    ),
  );
}

function formatDate(value) {
  return new Intl.DateTimeFormat(
    "en-IN",
    {
      weekday: "short",
      day: "2-digit",
      month: "short",
      year: "numeric",
    },
  ).format(
    dateFromLocalString(value),
  );
}

function formatShortDate(value) {
  return new Intl.DateTimeFormat(
    "en-IN",
    {
      weekday: "short",
      day: "2-digit",
      month: "short",
    },
  ).format(
    dateFromLocalString(value),
  );
}

function formatPercentage(value) {
  const numericValue =
    Number(value) || 0;

  return Number.isInteger(numericValue)
    ? numericValue
    : numericValue.toFixed(2);
}

function validateForm() {
  const errors = {};

  if (!form.target_date) {
    errors.target_date = [
      "Target date is required.",
    ];
  }

  const targetCount =
    Number(form.target_count);

  if (
    !Number.isInteger(targetCount) ||
    targetCount <= 0
  ) {
    errors.target_count = [
      "Target count must be a whole number greater than 0.",
    ];
  }

  fieldErrors.value = errors;

  if (
    Object.keys(errors).length > 0
  ) {
    errorMessage.value =
      "Please correct the highlighted fields.";

    return false;
  }

  return true;
}

async function loadTodayTarget() {
  try {
    const response = await api.get(
      "/api/daily-targets/today",
    );

    todayTarget.value =
      response.data.data.daily_target;

    form.target_date =
      todayTarget.value.target_date;

    form.target_count =
      todayTarget.value.target_count;
  } catch (error) {
    if (
      error.response?.status === 404
    ) {
      todayTarget.value = null;
      form.target_date = todayDate;
      form.target_count = 3;

      return;
    }

    throw error;
  }
}

async function loadDailyTargets() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const [targetsResponse] =
      await Promise.all([
        api.get(
          "/api/daily-targets",
        ),

        loadTodayTarget(),
      ]);

    targets.value =
      targetsResponse.data.data
        .daily_targets || [];
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Daily-target information could not be loaded.";
  } finally {
    loading.value = false;
  }
}

async function saveTodayTarget() {
  errorMessage.value = "";
  successMessage.value = "";
  fieldErrors.value = {};

  if (!validateForm()) {
    return;
  }

  saving.value = true;

  const payload = {
    target_date: form.target_date,

    target_count: Number(
      form.target_count,
    ),
  };

  try {
    if (todayTarget.value) {
      await api.put(
        `/api/daily-targets/${todayTarget.value.id}`,
        payload,
      );

      successMessage.value =
        "Today's target updated successfully.";
    } else {
      await api.post(
        "/api/daily-targets",
        payload,
      );

      successMessage.value =
        "Today's target created successfully.";
    }

    await loadDailyTargets();
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      "Today's target could not be saved.";

    fieldErrors.value =
      normalizeApiErrors(
        error.response?.data?.errors,
      );
  } finally {
    saving.value = false;
  }
}

onMounted(loadDailyTargets);
</script>

<template>
  <section class="page">
    <div class="page-header">
      <div>
        <span class="eyebrow">
          Consistency tracker
        </span>

        <h1>Daily Target</h1>

        <p>
          Set today's coding goal and compare it
          with problems whose solved date matches
          the target date.
        </p>
      </div>

      <button
        type="button"
        class="button button--secondary"
        :disabled="loading"
        @click="loadDailyTargets"
      >
        {{
          loading
            ? "Refreshing..."
            : "Refresh"
        }}
      </button>
    </div>

    <div
      v-if="errorMessage"
      class="alert alert--error"
      role="alert"
    >
      {{ errorMessage }}
    </div>

    <div
      v-if="successMessage"
      class="alert alert--success"
      role="status"
    >
      {{ successMessage }}
    </div>

    <div
      v-if="loading"
      class="loading-panel"
    >
      Loading daily-target performance...
    </div>

    <template v-else>
      <div class="daily-target-layout">
        <article
          class="
            panel
            today-target-panel
          "
        >
          <div class="panel__header">
            <div>
              <span class="eyebrow">
                Today's progress
              </span>

              <h2>
                {{
                  todayTarget
                    ? "Current Target"
                    : "No Target Set"
                }}
              </h2>

              <p>
                {{ formatDate(todayDate) }}
              </p>
            </div>

            <span
              v-if="todayTarget"
              class="badge"
              :class="
                todayTarget.is_completed
                  ? 'badge--solved'
                  : 'badge--unsolved'
              "
            >
              {{
                todayTarget.is_completed
                  ? "Completed"
                  : "In Progress"
              }}
            </span>
          </div>

          <div
            v-if="todayTarget"
            class="today-target-content"
          >
            <div class="today-target-metrics">
              <div>
                <span>
                  Today's Target
                </span>

                <strong>
                  {{
                    todayTarget.target_count
                  }}
                </strong>
              </div>

              <div>
                <span>
                  Solved Today
                </span>

                <strong>
                  {{
                    todayTarget.solved_count
                  }}
                </strong>
              </div>

              <div>
                <span>
                  Remaining
                </span>

                <strong>
                  {{ todayRemaining }}
                </strong>
              </div>

              <div>
                <span>
                  Completion
                </span>

                <strong>
                  {{
                    formatPercentage(
                      todayTarget
                        .completion_percentage,
                    )
                  }}%
                </strong>
              </div>
            </div>

            <ProgressBar
              :value="
                todayTarget
                  .completion_percentage
              "
              :label="
                `${todayTarget.solved_count} of ${todayTarget.target_count} problems completed`
              "
            />

            <p class="daily-target-note">
              Completion is calculated
              automatically from solved problems
              where <code>solved_date</code> equals
              <code>
                {{ todayTarget.target_date }}
              </code>.
            </p>
          </div>

          <div
            v-else
            class="
              empty-state
              empty-state--compact
            "
          >
            <h3>
              Set a target for today
            </h3>

            <p>
              No target exists for today. Use
              the form to define how many coding
              problems you plan to solve.
            </p>
          </div>
        </article>

        <article
          class="
            panel
            target-form-panel
          "
        >
          <div class="panel__header">
            <div>
              <span class="eyebrow">
                {{
                  todayTarget
                    ? "Update goal"
                    : "Set goal"
                }}
              </span>

              <h2>
                {{
                  todayTarget
                    ? "Update Today's Target"
                    : "Set Today's Target"
                }}
              </h2>

              <p>
                Only one target can exist for
                each user and date.
              </p>
            </div>
          </div>

          <form
            class="form"
            novalidate
            @submit.prevent="
              saveTodayTarget
            "
          >
            <div
              class="
                form-grid
                target-form-grid
              "
            >
              <div class="form-group">
                <label for="target-date">
                  Target Date
                </label>

                <input
                  id="target-date"
                  v-model="
                    form.target_date
                  "
                  type="date"
                  readonly
                  required
                  :aria-invalid="
                    Boolean(
                      firstError(
                        'target_date',
                      ),
                    )
                  "
                  :class="{
                    'target-input--error':
                      firstError(
                        'target_date',
                      ),
                  }"
                />

                <small class="form-hint">
                  This page manages today's
                  target.
                </small>

                <small
                  v-if="
                    firstError(
                      'target_date',
                    )
                  "
                  class="form-error"
                >
                  {{
                    firstError(
                      "target_date",
                    )
                  }}
                </small>
              </div>

              <div class="form-group">
                <label for="target-count">
                  Target Count
                </label>

                <input
                  id="target-count"
                  v-model.number="
                    form.target_count
                  "
                  type="number"
                  min="1"
                  step="1"
                  required
                  :aria-invalid="
                    Boolean(
                      firstError(
                        'target_count',
                      ),
                    )
                  "
                  :class="{
                    'target-input--error':
                      firstError(
                        'target_count',
                      ),
                  }"
                  @input="
                    clearFieldError(
                      'target_count',
                    )
                  "
                />

                <small class="form-hint">
                  Enter a whole number greater
                  than 0.
                </small>

                <small
                  v-if="
                    firstError(
                      'target_count',
                    )
                  "
                  class="form-error"
                >
                  {{
                    firstError(
                      "target_count",
                    )
                  }}
                </small>
              </div>
            </div>

            <div class="form-actions">
              <button
                type="submit"
                class="
                  button
                  button--primary
                "
                :disabled="saving"
              >
                {{
                  saving
                    ? "Saving..."
                    : todayTarget
                      ? "Update Today's Target"
                      : "Set Today's Target"
                }}
              </button>
            </div>
          </form>
        </article>
      </div>

      <article
        class="
          panel
          seven-day-panel
        "
      >
        <div class="panel__header">
          <div>
            <span class="eyebrow">
              Recent consistency
            </span>

            <h2>
              Last 7 Days Target Performance
            </h2>

            <p>
              Calendar-day performance including
              dates where no target was created.
            </p>
          </div>
        </div>

        <div class="seven-day-summary">
          <div>
            <span>
              Days with Targets
            </span>

            <strong>
              {{
                sevenDaySummary.target_days
              }}
              / 7
            </strong>
          </div>

          <div>
            <span>
              Completed Target Days
            </span>

            <strong>
              {{
                sevenDaySummary.completed_days
              }}
            </strong>
          </div>

          <div>
            <span>
              Total Target
            </span>

            <strong>
              {{
                sevenDaySummary.total_target
              }}
            </strong>
          </div>

          <div>
            <span>
              Total Solved
            </span>

            <strong>
              {{
                sevenDaySummary.total_solved
              }}
            </strong>
          </div>
        </div>

        <div class="table-container">
          <table
            class="
              data-table
              seven-day-table
            "
          >
            <thead>
              <tr>
                <th>Date</th>
                <th>Target</th>
                <th>Solved</th>
                <th>Remaining</th>
                <th>Completion</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="
                  day in lastSevenDays
                "
                :key="day.id"
              >
                <td>
                  <strong>
                    {{
                      formatShortDate(
                        day.target_date,
                      )
                    }}
                  </strong>

                  <small
                    v-if="
                      day.target_date ===
                      todayDate
                    "
                    class="today-label"
                  >
                    Today
                  </small>
                </td>

                <td>
                  {{
                    day.target_exists
                      ? day.target_count
                      : "—"
                  }}
                </td>

                <td>
                  {{
                    day.target_exists
                      ? day.solved_count
                      : "—"
                  }}
                </td>

                <td>
                  {{
                    day.target_exists
                      ? day.remaining_count
                      : "—"
                  }}
                </td>

                <td
                  class="
                    table-progress-cell
                  "
                >
                  <ProgressBar
                    v-if="
                      day.target_exists
                    "
                    :value="
                      day
                        .completion_percentage
                    "
                    :label="
                      `${formatPercentage(day.completion_percentage)}%`
                    "
                    :show-value="false"
                  />

                  <span
                    v-else
                    class="muted-text"
                  >
                    No target
                  </span>
                </td>

                <td>
                  <span
                    v-if="
                      day.target_exists
                    "
                    class="badge"
                    :class="
                      day.is_completed
                        ? 'badge--solved'
                        : 'badge--unsolved'
                    "
                  >
                    {{
                      day.is_completed
                        ? "Completed"
                        : "In Progress"
                    }}
                  </span>

                  <span
                    v-else
                    class="
                      badge
                      badge--not-started
                    "
                  >
                    No Target
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </template>
  </section>
</template>

<style scoped>
.daily-target-layout {
  display: grid;

  grid-template-columns:
    minmax(0, 1.35fr)
    minmax(320px, 0.65fr);

  gap: 24px;
  margin-bottom: 24px;
}

.today-target-panel,
.target-form-panel {
  min-width: 0;
}

.today-target-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.today-target-metrics,
.seven-day-summary {
  display: grid;

  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );

  gap: 12px;
}

.today-target-metrics > div,
.seven-day-summary > div {
  padding: 16px;

  background:
    var(--surface-muted);

  border:
    1px solid var(--border);

  border-radius:
    var(--radius-small);
}

.today-target-metrics span,
.seven-day-summary span {
  display: block;
  margin-bottom: 8px;

  color: var(--text-muted);

  font-size: 0.72rem;
  font-weight: 750;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.today-target-metrics strong,
.seven-day-summary strong {
  display: block;
  font-size: 1.35rem;
}

.daily-target-note {
  margin: 0;
  padding: 13px 15px;

  color: var(--text-secondary);

  background:
    var(--surface-muted);

  border:
    1px solid var(--border);

  border-radius:
    var(--radius-small);

  font-size: 0.84rem;
  line-height: 1.55;
}

.daily-target-note code {
  color: var(--primary-dark);
  font-weight: 700;
}

.target-form-grid {
  grid-template-columns: 1fr;
}

.target-form-panel input[readonly] {
  cursor: not-allowed;

  background:
    var(--surface-muted);
}

.target-input--error {
  border-color:
    var(--danger) !important;

  box-shadow:
    0 0 0 3px
    rgba(181, 45, 58, 0.1) !important;
}

.seven-day-summary {
  margin-bottom: 22px;
}

.seven-day-table {
  min-width: 900px;
}

.today-label {
  display: block;
  margin-top: 3px;

  color: var(--primary);

  font-size: 0.68rem;
  font-weight: 750;
  text-transform: uppercase;
}

@media (max-width: 1120px) {
  .daily-target-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .today-target-metrics,
  .seven-day-summary {
    grid-template-columns:
      repeat(
        2,
        minmax(0, 1fr)
      );
  }
}

@media (max-width: 520px) {
  .today-target-metrics,
  .seven-day-summary {
    grid-template-columns: 1fr;
  }
}
</style>