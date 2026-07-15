import {
  createRouter,
  createWebHistory,
} from "vue-router";

import DailyTargetView from "../views/DailyTargetView.vue";
import DashboardView from "../views/DashboardView.vue";
import LoginView from "../views/LoginView.vue";
import ProblemFormView from "../views/ProblemFormView.vue";
import ProblemsView from "../views/ProblemsView.vue";
import RegisterView from "../views/RegisterView.vue";
import RevisionView from "../views/RevisionView.vue";
import WeakTopicsView from "../views/WeakTopicsView.vue";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
    meta: {
      guestOnly: true,
    },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/problems",
    name: "problems",
    component: ProblemsView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/problems/new",
    name: "problem-create",
    component: ProblemFormView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/problems/:id/edit",
    name: "problem-edit",
    component: ProblemFormView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/daily-targets",
    name: "daily-targets",
    component: DailyTargetView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/revision",
    name: "revision",
    component: RevisionView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/weak-topics",
    name: "weak-topics",
    component: WeakTopicsView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,

  scrollBehavior() {
    return {
      top: 0,
      behavior: "smooth",
    };
  },
});

router.beforeEach((to) => {
  const token = localStorage.getItem("authToken");

  if (to.meta.requiresAuth && !token) {
    return {
      name: "login",
      query: {
        redirect: to.fullPath,
      },
    };
  }

  if (to.meta.guestOnly && token) {
    return {
      name: "dashboard",
    };
  }

  return true;
});

export default router;