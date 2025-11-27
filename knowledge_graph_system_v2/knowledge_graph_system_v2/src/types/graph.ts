// src/types/graph.ts

export interface Node {
  id: string;
  label: string;
  type: "Paper" | "Author" | "Organization";
  // 根据不同类型可能有其他字段
  title?: string;
  year?: number;
  venue?: string;
  doi?: string;
  hIndex?: number;
  orcid?: string;
  country?: string;
  rank?: number;
}

export interface Edge {
  source: string;
  target: string;
  relation: "AUTHORED" | "AFFILIATED_WITH" | "CITES";
}

export interface GraphDTO {
  nodes: Node[];
  edges: Edge[];
}
