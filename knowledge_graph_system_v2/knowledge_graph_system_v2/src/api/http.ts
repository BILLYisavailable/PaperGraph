import axios from "axios";
import { message } from "ant-design-vue";

// 1. 取地址（Webpack 版）
const baseURL = process.env.VUE_APP_API_BASE;
if (!baseURL) {
  throw new Error(
    "VUE_APP_API_BASE 未定义，请在项目根目录新建 .env 文件并写入 VUE_APP_API_BASE=http://localhost:8000/api/v1"
  );
}

// 2. 创建实例
const http = axios.create({
  baseURL,
  timeout: 10000,
});

// 3. 拦截器不变
http.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || "网络异常";
    message.error(msg);
    return Promise.reject(err);
  }
);

export const get = <T = any>(url: string, params?: object) =>
  http.get<T>(url, { params }).then((r) => r.data);

export const post = <T = any>(url: string, data?: object) =>
  http.post<T>(url, data).then((r) => r.data);
