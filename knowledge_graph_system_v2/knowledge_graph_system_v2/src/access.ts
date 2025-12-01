import router from "@/router";
import { message } from "ant-design-vue";

/**
 * 全局权限校验
 */
router.beforeEach(async (to, from, next) => {
  // 简单的路由校验，不涉及用户权限
  next();
});
