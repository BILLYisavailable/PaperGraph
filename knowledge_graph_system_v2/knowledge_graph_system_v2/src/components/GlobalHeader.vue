<template>
  <div id="globalHeader">
    <a-row :wrap="false">
      <a-col flex="200px">
        <div class="title-bar">
          <img class="logo" src="../assets/logo.png" alt="logo" />
          <div class="title">文献知识图谱</div>
        </div>
      </a-col>
      <a-col flex="auto">
        <a-menu
          v-model:selectedKeys="current"
          mode="horizontal"
          :items="items"
          @click="doMenuClick"
        />
      </a-col>
      <a-col flex="80px">
        <div class="user-login-status">
          <div v-if="loginUserStore.loginUser.id">
            {{ loginUserStore.loginUser.username ?? "无名" }}
          </div>
          <div v-else>
            <a-button type="primary" href="/user/login">登录</a-button>
          </div>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script lang="ts" setup>
import { h, ref } from "vue";
import { CrownOutlined, HomeOutlined } from "@ant-design/icons-vue";
import { MenuProps } from "ant-design-vue";
import { useRouter } from "vue-router";
import { useLoginUserStore } from "@/store/useLoginUserStore";

const loginUserStore = useLoginUserStore();

const router = useRouter();
// 点击菜单后的路由跳转事件
const doMenuClick = ({ key }: { key: string }) => {
  router.push({
    path: key,
  });
};

const current = ref<string[]>(["mail"]);
// 监听路由变化，更新当前菜单选中状态
router.afterEach((to, from, failure) => {
  current.value = [to.path];
});

const items = ref<MenuProps["items"]>([
  {
    key: "/",
    icon: () => h(HomeOutlined),
    label: "主页",
    title: "主页",
  },
  {
    key: "/kg",
    label: "知识图谱",
    title: "知识图谱",
  },
  {
    key: "/papers",
    label: "文献列表",
    title: "文献列表",
  },
  {
    key: "/data-stats",
    label: "数据统计",
    title: "数据统计",
  },
  {
    key: "/admin/userManage",
    icon: () => h(CrownOutlined),
    label: "用户管理",
    title: "用户管理",
  },
]);
</script>

<style scoped>
#globalHeader {
  height: 64px;
  display: flex;
  align-items: center;
}

.title-bar {
  display: flex;
  align-items: center;
  transition: transform 0.3s ease;
}

.title-bar:hover {
  transform: translateX(4px);
}

.title {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 20px;
  font-weight: 600;
  margin-left: 16px;
  letter-spacing: 0.5px;
}

.logo {
  height: 40px;
  width: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.1) rotate(5deg);
}

.user-login-status {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

:deep(.ant-menu) {
  background: transparent;
  border-bottom: none;
  line-height: 62px;
}

:deep(.ant-menu-item) {
  margin: 0 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.ant-menu-item:hover) {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

:deep(.ant-menu-item-selected) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: none;
}

:deep(.ant-menu-item-selected::after) {
  display: none;
}
</style>
