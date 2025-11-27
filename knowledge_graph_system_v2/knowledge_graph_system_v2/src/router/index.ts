import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import HomePage from "@/pages/HomePage.vue";
import UserLoginPage from "@/pages/user/UserLoginPage.vue";
import UserRegisterPage from "@/pages/user/UserRegisterPage.vue";
import UserManagePage from "@/pages/admin/UserManagePage.vue";
import KnowledgeGraph from "@/pages/KnowledgeGraph.vue";
import PaperList from "@/pages/PaperList.vue";
import DataStats from "@/pages/DataStats.vue";
const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "home",
    component: HomePage,
  },
  {
    path: "/user/login",
    name: "userLogin",
    component: UserLoginPage,
  },
  {
    path: "/user/register",
    name: "userRegister",
    component: UserRegisterPage,
  },
  {
    path: "/admin/userManage",
    name: "adminUserManage",
    component: UserManagePage,
  },
  {
    path: "/data-stats",
    name: "DataStats",
    component: DataStats,
  },
  {
    path: "/kg",
    name: "KnowledgeGraph",
    component: KnowledgeGraph,
  },
  {
    path: "/papers",
    name: "PaperList",
    component: PaperList,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
