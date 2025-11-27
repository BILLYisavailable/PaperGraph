<template>
  <a-layout style="height: 100vh">
    <!-- 左侧筛选器 -->
    <a-layout-sider width="280" style="background: #fff">
      <div style="padding: 16px">
        <h3>筛选器</h3>
        <a-form layout="vertical">
          <a-form-item label="年份">
            <a-slider
              range
              :min="2000"
              :max="2025"
              v-model:value="filter.year"
            />
          </a-form-item>
          <a-form-item label="机构">
            <a-select
              v-model:value="filter.orgs"
              mode="multiple"
              placeholder="选择机构"
              :options="orgOptions"
            />
          </a-form-item>
          <a-form-item label="作者">
            <a-input v-model:value="filter.author" placeholder="模糊搜索" />
          </a-form-item>
          <a-form-item>
            <a-button type="primary" block @click="onFilter">应用筛选</a-button>
          </a-form-item>
        </a-form>
      </div>
    </a-layout-sider>

    <!-- 中间图谱 -->
    <a-layout-content style="background: #fafafa; position: relative">
      <div ref="chartDom" style="width: 100%; height: 100%"></div>
    </a-layout-content>

    <!-- 右侧详情 -->
    <a-layout-sider width="320" style="background: #fff">
      <div style="padding: 16px">
        <h3>详细信息</h3>
        <div v-if="!selected">请单击节点/边</div>
        <a-form v-else layout="vertical" size="small">
          <a-form-item label="名称">
            <a-input :value="selected.label" readonly />
          </a-form-item>
          <a-form-item label="类型">
            <a-tag :color="tagColor(selected.type)">{{ selected.type }}</a-tag>
          </a-form-item>
          <!-- Paper 字段 -->
          <template v-if="selected.type === 'Paper'">
            <a-form-item label="标题"
              ><a-input :value="selected.title" readonly
            /></a-form-item>
            <a-form-item label="年份"
              ><a-input :value="selected.year" readonly
            /></a-form-item>
            <a-form-item label="发表地"
              ><a-input :value="selected.venue" readonly
            /></a-form-item>
            <a-form-item label="DOI"
              ><a-input :value="selected.doi" readonly
            /></a-form-item>
          </template>
          <!-- Author 字段 -->
          <template v-if="selected.type === 'Author'">
            <a-form-item label="h-index"
              ><a-input :value="selected.hIndex" readonly
            /></a-form-item>
            <a-form-item label="ORCID"
              ><a-input :value="selected.orcid" readonly
            /></a-form-item>
          </template>
          <!-- Organization 字段 -->
          <template v-if="selected.type === 'Organization'">
            <a-form-item label="国家"
              ><a-input :value="selected.country" readonly
            /></a-form-item>
            <a-form-item label="排名"
              ><a-input :value="selected.rank" readonly
            /></a-form-item>
          </template>
        </a-form>
      </div>
    </a-layout-sider>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import * as echarts from "echarts";
import type { GraphDTO, Node, Link } from "@/types/node.ts";
import { message } from "ant-design-vue";
/* 筛选状态 */
const filter = ref({
  year: [2020, 2025],
  orgs: [] as string[],
  author: "",
});
const orgOptions = ref([
  { label: "Tsinghua", value: "Tsinghua" },
  { label: "PKU", value: "PKU" },
]);

/* 选中项 */
const selected = ref<Node | null>(null);

/* 图谱实例 */
const chartDom = ref<HTMLDivElement>();
let ins: echarts.ECharts;
const lineStyleMap: Record<string, any> = {
  AUTHORED: { width: 1.5, color: "#67c23a", type: "solid" },
  AFFILIATED_WITH: { width: 1.5, color: "#909399", type: "dashed" },
  CITES: { width: 2, color: "#f56c6c", type: "dotted" }, // 红色点线 = 引用
};
import { get } from "@/api/http";

async function onFilter() {
  /* 1. 构造参数 */
  const params = {
    yearStart: filter.value.year[0],
    yearEnd: filter.value.year[1],
    orgs: filter.value.orgs,
    author: filter.value.author,
  };
  /* 2. 调接口 */
  const dto: GraphDTO = await get("/graph/root", params);
  /* 3. 画 */
  draw(dto);
}

/* 画/重画 */
function draw(dto: GraphDTO) {
  /*防御：DOM 不存在直接返回 */
  if (!chartDom.value) return;
  if (!ins) ins = echarts.init(chartDom.value);
  const color: Record<string, string> = {
    Paper: "#409eff",
    Author: "#f2d545",
    Organization: "#67c23a",
  };
  const option: echarts.EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === "edge") {
          const rel = params.data.relation;
          const cit = rel === "CITES" ? "（引用）" : "";
          return `${params.data.source} → ${params.data.target}<br/>关系：${rel}${cit}`;
        }
        return params.data.name;
      },
    },
    animationDurationUpdate: 500,
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        draggable: true,
        data: dto.nodes.map((n) => ({
          id: n.id,
          name: n.label,
          value: n.type === "Paper" ? 30 : 20,
          category: n.type,
          symbolSize: n.type === "Paper" ? 30 : 20,
          itemStyle: { color: color[n.type] },
        })),
        edges: dto.links.map((l) => ({
          source: l.source as string,
          target: l.target as string,
          lineStyle: lineStyleMap[l.relation],
          // 悬浮提示
          emphasis: { lineStyle: { width: 4 } },
        })),
        categories: Object.keys(color).map((name) => ({ name })),
        force: { repulsion: 800, edgeLength: 120, gravity: 0.05 },
        emphasis: { focus: "adjacency", lineStyle: { width: 3 } },
      },
    ],
  };
  ins.setOption(option);

  /* 单击节点 → 右侧详情 & 展开子图 */
  ins.off("click");
  ins.on("click", (params) => {
    if (params.dataType === "node") {
      /* 立即展开子图（异步） */
      get<GraphDTO>(`/graph/children/${params.data.id}`)
        .then((sub) => {
          draw({ nodes: sub.nodes, links: sub.edges });
        })
        .catch((e) => message.error("加载子节点失败：" + e));

      /* 同步设置右侧详情（本地已有数据） */
      selected.value = dto.nodes.find((n) => n.id === params.data.id) ?? null;
    }
  });
}

/* 标签颜色 */
function tagColor(type: string) {
  return type === "Paper" ? "blue" : type === "Author" ? "orange" : "green";
}

onMounted(() => {
  onFilter(); // 首次加载
  window.addEventListener("resize", () => ins.resize());
});
</script>
