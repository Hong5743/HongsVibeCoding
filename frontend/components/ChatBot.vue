<template>
  <!-- 플로팅 버튼 -->
  <div class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
    <!-- 채팅창 -->
    <div
      v-if="isOpen"
      class="w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-gray-100 flex flex-col overflow-hidden"
      style="height: 480px;"
    >
      <!-- 헤더 -->
      <div class="bg-gray-900 text-white px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
          </svg>
          <span class="text-sm font-semibold">AI 기업 도우미</span>
        </div>
        <button @click="isOpen = false" class="text-gray-300 hover:text-white transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- 메시지 목록 -->
      <div ref="messagesEl" class="flex-1 overflow-y-auto p-4 space-y-3">
        <!-- 안내 메시지 -->
        <div v-if="messages.length === 0" class="text-center py-8 text-gray-400 text-sm">
          <p class="mb-1">궁금한 기업을 물어보세요!</p>
          <p class="text-xs text-gray-300">"서울 IT 스타트업 알려줘" 처럼 입력하세요.</p>
        </div>

        <template v-for="(msg, i) in messages" :key="i">
          <!-- 사용자 메시지 -->
          <div v-if="msg.role === 'user'" class="flex justify-end">
            <div class="max-w-[75%] bg-gray-900 text-white text-sm px-3 py-2 rounded-2xl rounded-tr-sm">
              {{ msg.content }}
            </div>
          </div>

          <!-- AI 메시지 -->
          <div v-else class="flex flex-col gap-1">
            <div class="max-w-[85%] bg-gray-50 border border-gray-100 text-gray-800 text-sm px-3 py-2 rounded-2xl rounded-tl-sm whitespace-pre-wrap">
              {{ msg.content }}
            </div>
            <!-- sources -->
            <div v-if="msg.sources && msg.sources.length > 0" class="flex flex-wrap gap-1 ml-1">
              <NuxtLink
                v-for="src in msg.sources"
                :key="src.id"
                :to="`/companies/${src.id}`"
                @click="isOpen = false"
                class="text-xs text-blue-600 hover:underline bg-blue-50 px-2 py-0.5 rounded-full"
              >
                {{ src.name }}
              </NuxtLink>
            </div>
          </div>
        </template>

        <!-- 로딩 -->
        <div v-if="loading" class="flex">
          <div class="bg-gray-50 border border-gray-100 px-3 py-2 rounded-2xl rounded-tl-sm">
            <span class="flex gap-1">
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:0ms"/>
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:150ms"/>
              <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay:300ms"/>
            </span>
          </div>
        </div>
      </div>

      <!-- 입력창 -->
      <div class="border-t border-gray-100 p-3 flex gap-2">
        <input
          v-model="input"
          @keydown.enter.prevent="submit"
          :disabled="loading"
          type="text"
          placeholder="질문을 입력하세요..."
          class="flex-1 text-sm px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 disabled:opacity-50"
        />
        <button
          @click="submit"
          :disabled="loading || !input.trim()"
          class="bg-gray-900 text-white px-3 py-2 rounded-lg hover:bg-gray-700 disabled:opacity-40 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 플로팅 버튼 -->
    <button
      @click="isOpen = !isOpen"
      class="w-12 h-12 bg-gray-900 text-white rounded-full shadow-lg hover:bg-gray-700 transition-colors flex items-center justify-center"
    >
      <svg v-if="!isOpen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
      </svg>
      <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useChat, type ChatMessage } from "~/composables/useChat";

const { sendMessage } = useChat();

const isOpen = ref(false);
const input = ref("");
const loading = ref(false);
const messages = ref<ChatMessage[]>([]);
const messagesEl = ref<HTMLElement | null>(null);

async function scrollToBottom() {
  await nextTick();
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight;
  }
}

async function submit() {
  const question = input.value.trim();
  if (!question || loading.value) return;

  messages.value.push({ role: "user", content: question });
  input.value = "";
  loading.value = true;
  await scrollToBottom();

  try {
    const result = await sendMessage(question);
    messages.value.push({
      role: "assistant",
      content: result.answer,
      sources: result.sources,
    });
  } catch {
    messages.value.push({
      role: "assistant",
      content: "AI 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
    });
  } finally {
    loading.value = false;
    await scrollToBottom();
  }
}
</script>
