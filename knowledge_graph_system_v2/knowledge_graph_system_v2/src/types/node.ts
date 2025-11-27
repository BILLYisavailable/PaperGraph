export type NodeType = "Paper" | "Author" | "Organization";

export interface Node {
  id: string;
  label: string;
  type: NodeType;
  year?: number;
  title?: string;
  venue?: string;
  doi?: string;
  hIndex?: number;
  orcid?: string;
  country?: string;
  rank?: number;
  [key: string]: any; // 允许扩展
}

export interface Link {
  source: string | Node;
  target: string | Node;
  relation: "AUTHORED" | "AFFILIATED_WITH" | "CITES";
}

export interface GraphDTO {
  nodes: Node[];
  links: Link[];
}
