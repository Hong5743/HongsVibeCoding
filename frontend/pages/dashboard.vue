<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-2xl mx-auto">
      <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">대시보드</h1>
        <p class="text-gray-500 text-sm">{{ auth.user?.email }}</p>

        <div class="mt-6">
          <span
            class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium"
            :class="statusClass"
          >
            {{ statusLabel }}
          </span>
        </div>

        <div class="mt-8 pt-6 border-t border-gray-100">
          <button
            @click="auth.logout(); navigateTo('/login')"
            class="text-sm text-gray-500 hover:text-red-600 transition-colors"
          >
            로그아웃
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

definePageMeta({ middleware: ["auth"] });

const auth = useAuthStore();

onMounted(() => auth.fetchMe());

const statusClass = computed(() => ({
  "bg-yellow-100 text-yellow-700": auth.user?.status === "pending",
  "bg-green-100 text-green-700": auth.user?.status === "approved",
  "bg-red-100 text-red-700": auth.user?.status === "rejected",
}));

const statusLabel = computed(() => ({
  pending: "승인 대기 중",
  approved: "승인됨",
  rejected: "거절됨",
}[auth.user?.status ?? "pending"]));
</script>
