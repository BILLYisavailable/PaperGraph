<template>
  <a-layout style="height: calc(100vh - 120px); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);">
    <!-- 左侧筛选器 -->
    <a-layout-sider width="280" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
      <div style="padding: 20px">
        <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 12px;">筛选器</h3>
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
            <a-button type="primary" block @click="onFilter" size="large" style="height: 40px; border-radius: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none;">
              应用筛选
            </a-button>
          </a-form-item>
        </a-form>
      </div>
    </a-layout-sider>

    <!-- 中间图谱 -->
    <a-layout-content style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); position: relative">
      <div ref="chartDom" style="width: 100%; height: 100%"></div>
    </a-layout-content>

    <!-- 右侧详情 -->
    <a-layout-sider width="320" style="background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);">
      <div style="padding: 20px">
        <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 12px;">详细信息</h3>
        <div v-if="!selected">请单击节点/边</div>
        <a-form v-else layout="vertical" size="small">
          <a-form-item label="名称">
            <a-input :value="selected.label" readonly />
          </a-form-item>
          <a-form-item label="类型">
            <a-tag :color="tagColor(selected.type)">
              {{ selected.type }}
            </a-tag>
          </a-form-item>
          <!-- Paper 字段 -->
          <template v-if="selected.type === 'Paper'">
            <a-form-item label="标题">
              <a-input :value="selected.title" readonly />
            </a-form-item>
            <a-form-item label="年份">
              <a-input :value="selected.year" readonly />
            </a-form-item>
            <a-form-item label="发表地">
              <a-input :value="selected.venue" readonly />
            </a-form-item>
            <a-form-item label="DOI">
              <a-input :value="selected.doi" readonly />
            </a-form-item>
          </template>
          <!-- Author 字段 -->
          <template v-if="selected.type === 'Author'">
            <a-form-item label="h-index">
              <a-input :value="selected.hIndex" readonly />
            </a-form-item>
            <a-form-item label="ORCID">
              <a-input :value="selected.orcid" readonly />
            </a-form-item>
          </template>
          <!-- Organization 字段 -->
          <template v-if="selected.type === 'Organization'">
            <a-form-item label="国家">
              <a-input :value="selected.country" readonly />
            </a-form-item>
            <a-form-item label="排名">
              <a-input :value="selected.rank" readonly />
            </a-form-item>
          </template>
        </a-form>
      </div>
    </a-layout-sider>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import * as echarts from "echarts";
import type { GraphDTO, Node, Edge } from "@/types/graph";
import { message } from "ant-design-vue";
import { get } from "@/api/http";
import { post } from "@/api/http";
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
  CITES: { width: 2, color: "#f56c6c", type: "dotted" },
};

/**
 * 应用筛选并加载数据
 */
// 在 script setup 顶部添加类型接口
interface GraphResponse {
  nodes: any[];
  edges: any[];
}
async function onFilter() {
  try {
    const params = {
      yearStart: filter.value.year[0],
      yearEnd: filter.value.year[1],
      orgs: filter.value.orgs,
      author: filter.value.author,
    };

    // 提取接口类型
    interface GraphResponse {
      nodes: any[];
      edges: any[];
    }

    const rawData = await get<GraphResponse>("/graph/root", params);

    console.log("原始节点:", rawData.nodes);
    console.log("原始边:", rawData.edges);

    const processedNodes: Node[] = rawData.nodes.map((node) => ({
      id: node.id,
      type: node.label as "Paper" | "Author" | "Organization",
      label: node.properties?.name || node.properties?.title || node.label,
      ...node.properties,
    }));

    const edgeMap = new Map<string, Edge>();
    rawData.edges.forEach((edge) => {
      const key = `${edge.source}-${edge.target}`;
      if (!edgeMap.has(key)) {
        edgeMap.set(key, {
          source: edge.source,
          target: edge.target,
          relation: edge.type,
          ...edge.properties,
        });
      }
    });
    const processedEdges = Array.from(edgeMap.values());

    const dto: GraphDTO = {
      nodes: processedNodes,
      edges: processedEdges,
    };

    draw(dto);
  } catch (error) {
    console.error("筛选失败:", error);
    // 关键修复：模板字符串表达式需要换行
    message.error(
      `加载图谱失败: ${error instanceof Error ? error.message : "未知错误"}`
    );
  }
}

/**
 * 绘制/重绘图谱
 */
function draw(dto: GraphDTO) {
  if (!chartDom.value) return;
  if (!ins) ins = echarts.init(chartDom.value);

  const color: Record<string, string> = {
    Paper: "#409eff",
    Author: "#f2d545",
    Organization: "#67c23a",
  };
  console.log("【边数据】links 长度:", dto.edges.length, dto.edges);
  console.log(
    "【节点类型检查】",
    dto.nodes.map((n) => ({ id: n.id, label: n.label, type: n.type }))
  );
  const option: echarts.EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === "edge") {
          const rel = params.data.relation;
          const cit = rel === "CITES" ? "（引用）" : "";
          return `${params.data.source} → ${params.data.target}<br/>关系：${rel}${cit}`;
        }
        return params.data.label || params.data.name || params.data.title;
      },
    },
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        draggable: true,
        data: dto.nodes.map((n) => ({
          id: n.id,
          name: n.label,
          symbolSize:
            n.type === "Organization" ? 28 : n.type === "Paper" ? 30 : 20,
          itemStyle: {
            color: n.type === "Organization" ? "#e60000" : color[n.type],
          },
          ...n,
        })),
        links: dto.edges.map((e) => ({
          source: e.source,
          target: e.target,
          relation: e.relation,
          lineStyle: lineStyleMap[e.relation] || { width: 1.5, color: "#999" },
        })),
        categories: Object.keys(color).map((name) => ({ name })),
        force: { repulsion: 800, edgeLength: 120, gravity: 0.05 },
        emphasis: { focus: "adjacency", lineStyle: { width: 3 } },
      },
    ],
  };

  ins.setOption(option);

  ins.off("click");
  ins.on("click", (params) => {
    if (params.dataType === "node") {
      loadAndMergeSubgraph(params.data.id);
      selected.value = params.data as Node;
    }
  });
  ins.off("graphdragend"); // 防止重复绑定
  ins.on("graphdragend", (params) => {
    // params.data 是被拖动的节点
    const updateList = ins.getOption().series[0].data.map((n: any) => ({
      node_id: n.id,
      x: n.x ?? 0, // 拖拽后 ECharts 会给每个节点加上 x/y
      y: n.y ?? 0,
    }));

    // 可选：批量保存
    post("/graph/layout/persist", { positions: updateList })
      .then(() => message.success("位置已保存"))
      .catch(() => message.error("保存失败"));
  });
  console.log("【节点 id 集合】", new Set(dto.nodes.map((n) => n.id)));
  console.log(
    "【link 源-目标】",
    dto.edges.map((l) => `${l.source}->${l.target}`)
  );
  console.log(
    "【最终】option.series[0].links",
    JSON.stringify(option.series[0].links)
  );
}

/**
 * 加载子图并合并到当前图谱
 */
async function loadAndMergeSubgraph(nodeId: string) {
  try {
    // 🔧 提取数字部分，去掉前缀
    const numericId = nodeId.replace(/^\D+/, ""); // "paper_003" → "003"
    // 如果前端已经拿到纯数字，直接传
    const cleanId = nodeId.replace(/^\D+/, "").replace(/^0+/, "") || nodeId;

    console.log("【调试】请求子图，原始 ID:", nodeId, "提取后 ID:", cleanId);

    const sub = await get<GraphResponse>(`/graph/children/${cleanId}`);

    // 同样需要转换数据格式
    const processedSubNodes: Node[] = sub.nodes.map((node) => ({
      id: node.id,
      type: node.label as "Paper" | "Author" | "Organization",
      label: node.properties?.name || node.properties?.title || node.label,
      ...node.properties,
    }));

    const edgeMap = new Map<string, Edge>();
    sub.edges.forEach((edge) => {
      const key = `${edge.source}-${edge.target}`;
      if (!edgeMap.has(key)) {
        edgeMap.set(key, {
          source: edge.source,
          target: edge.target,
          relation: edge.type,
          ...edge.properties,
        });
      }
    });
    const processedSubEdges = Array.from(edgeMap.values());

    // 合并逻辑...
    const currentOption = ins.getOption() as any;
    const currentNodes = currentOption.series[0].data || [];
    const currentLinks = currentOption.series[0].links || []; // ✅ links 不是 edges

    const newNodes = processedSubNodes.filter(
      (n) => !currentNodes.some((cn: any) => cn.id === n.id)
    );
    const newLinks = processedSubEdges.filter(
      (e) =>
        !currentLinks.some(
          (ce: any) => ce.source === e.source && ce.target === e.target
        )
    );

    ins.setOption({
      series: [
        {
          data: [...currentNodes, ...newNodes],
          links: [...currentLinks, ...newLinks], // ✅ 用 links
        },
      ],
    });
  } catch (error) {
    console.error("加载子图失败:", error);
    message.error(
      `加载子节点失败: ${error instanceof Error ? error.message : "未知错误"}`
    );
  }
}

function tagColor(type: string) {
  return type === "Paper" ? "blue" : type === "Author" ? "orange" : "green";
}

onMounted(() => {
  onFilter();
  window.addEventListener("resize", () => ins?.resize());
});
</script>
