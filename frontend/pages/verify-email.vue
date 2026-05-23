<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
      <div v-if="loading">
        <p class="text-gray-500 text-sm">이메일 인증 중...</p>
      </div>

      <div v-else-if="success">
        <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 class="text-xl font-bold text-gray-900 mb-2">이메일 인증 완료</h1>
        <p class="text-gray-500 text-sm mb-6">인증이 완료되었습니다. 로그인해 주세요.</p>
        <NuxtLink to="/login" class="inline-block bg-primary-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
          로그인하기
        </NuxtLink>
      </div>

      <div v-else>
        <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 class="text-xl font-bold text-gray-900 mb-2">인증 실패</h1>
        <p class="text-gray-500 text-sm mb-6">{{ error }}</p>
        <NuxtLink to="/signup" class="inline-block text-primary-600 text-sm font-medium hover:underline">
          다시 가입하기
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: [] });

const route = useRoute();
const config = useRuntimeConfig();
const loading = ref(true);
const success = ref(false);
const error = ref("");

onMounted(async () => {
  const token = route.query.token as string;
  if (!token) {
    error.value = "유효하지 않은 링크입니다.";
    loading.value = false;
    return;
  }

  try {
    await $fetch(`${config.public.apiBase}/api/auth/verify-email`, {
      params: { token },
    });
    success.value = true;
  } catch (e: unknown) {
    const err = e as { data?: { detail?: { error?: string } } };
    error.value = err.data?.detail?.error ?? "인증에 실패했습니다.";
  } finally {
    loading.value = false;
  }
});
</script>
