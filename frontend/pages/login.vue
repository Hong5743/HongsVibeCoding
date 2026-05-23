<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">로그인</h1>
        <p class="text-gray-500 mt-1 text-sm">기업 담당자 전용 로그인</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="company@example.com"
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div class="flex justify-end">
          <NuxtLink to="/forgot-password" class="text-sm text-primary-600 hover:underline">
            비밀번호를 잊으셨나요?
          </NuxtLink>
        </div>

        <div v-if="error" class="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-primary-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
        >
          {{ loading ? "로그인 중..." : "로그인" }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-gray-500">
        계정이 없으신가요?
        <NuxtLink to="/signup" class="text-primary-600 font-medium hover:underline">회원가입</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

definePageMeta({ middleware: [] });

const auth = useAuthStore();
const router = useRouter();
const form = reactive({ email: "", password: "" });
const loading = ref(false);
const error = ref("");

async function handleLogin() {
  loading.value = true;
  error.value = "";
  try {
    await auth.login(form.email, form.password);
    await router.push("/dashboard");
  } catch (e: unknown) {
    const err = e as { data?: { detail?: { error?: string } } };
    error.value = err.data?.detail?.error ?? "로그인에 실패했습니다.";
  } finally {
    loading.value = false;
  }
}
</script>
