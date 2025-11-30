import { ref } from "vue";
import { get } from "@/api/http";

export const totalPaperCount = ref<number>(0);

export async function loadTotalPaperCount() {
  try {
    const res: any = await get("/graph/root", { limit: 200 });
    const allPapers = (res.nodes || [])
      .filter((n: any) => n.label === "Paper" || n.type === "Paper")
      .map((n: any) => n.properties);
    totalPaperCount.value = allPapers.length;
    console.log("Total paper count loaded:", totalPaperCount.value);
  } catch (e) {
    // 不阻塞启动，仅记录错误
    console.error("loadTotalPaperCount failed:", e);
  }
}
