export interface ChatSource {
  id: number;
  name: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

interface ChatApiResponse {
  success: boolean;
  data: {
    answer: string;
    sources: ChatSource[];
  };
  error: string | null;
}

export function useChat() {
  const config = useRuntimeConfig();
  const base = config.public.apiBase;

  async function sendMessage(question: string): Promise<{ answer: string; sources: ChatSource[] }> {
    const res = await $fetch<ChatApiResponse>(`${base}/api/chat`, {
      method: "POST",
      body: { question },
    });
    return res.data;
  }

  return { sendMessage };
}
