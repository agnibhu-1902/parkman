import { createRouter, createWebHistory } from "vue-router";
import AdminHome from "../views/admin/Home.vue";
import AdminUsers from "../views/admin/Users.vue";
import AdminSummary from "../views/admin/Summary.vue";
import Home from "../views/user/Home.vue";
import Summary from "../views/user/Summary.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import axios from "../config/api";

const routes = [
  // User routes
  {
    path: "/",
    name: "Home",
    component: Home,
    meta: { requiresAuth: true, userOnly: true },
  },
  {
    path: "/summary",
    name: "Summary",
    component: Summary,
    meta: { requiresAuth: true, userOnly: true },
  },

  // Admin routes
  {
    path: "/admin/",
    name: "AdminHome",
    component: AdminHome,
    meta: { requiresAuth: true, adminOnly: true },
  },
  {
    path: "/admin/users",
    name: "AdminUsers",
    component: AdminUsers,
    meta: { requiresAuth: true, adminOnly: true },
  },
  {
    path: "/admin/summary",
    name: "AdminSummary",
    component: AdminSummary,
    meta: { requiresAuth: true, adminOnly: true },
  },

  // Auth routes
  { path: "/login", name: "Login", component: Login },
  { path: "/register", name: "Register", component: Register },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const response = await axios.get("/api/check-auth");
      const data = response.data;

      if (!data.logged_in) return next("/login");

      if (to.meta.adminOnly && !data.user.is_admin) return next("/");
      if (to.meta.userOnly && data.user.is_admin) return next("/admin/");

      next();
    } catch (err) {
      next("/login");
    }
  } else next();
});

export default router;
