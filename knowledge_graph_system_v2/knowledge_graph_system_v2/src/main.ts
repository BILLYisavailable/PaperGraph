import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { createPinia } from "pinia";
import "./access";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";
import { loadTotalPaperCount } from "@/stores/totalPaperCount";

const pinia = createPinia();

// 在应用启动时加载一次文献数量统计（不阻塞渲染）
loadTotalPaperCount();

createApp(App).use(pinia).use(Antd).use(router).mount("#app");
