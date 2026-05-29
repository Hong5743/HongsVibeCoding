<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-6">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <h1 class="text-2xl font-bold text-gray-900">관리자 로그인</h1>
        <p class="text-gray-500 mt-1 text-sm">관리자 계정으로 로그인하세요.</p>
      </div>

      <form
        class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4"
        @submit.prevent="handleSubmit"
      >
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            이메일
          </label>
          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
            placeholder="admin@example.com"
            class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">
            비밀번호
          </label>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          />
        </div>

        <p v-if="errorMessage" class="text-sm text-red-500">
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="submitting"
          class="w-full bg-gray-900 text-white text-sm font-medium py-2.5 rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ submitting ? "로그인 중..." : "로그인" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useAdmin } from "~/composables/useAdmin";

const { adminLogin, getAdminToken } = useAdmin();
const router = useRouter();

const email = ref("");
const password = ref("");
const submitting = ref(false);
const errorMessage = ref("");

onMounted(() => {
  if (getAdminToken()) {
    router.replace("/admin");
  }
});

async function handleSubmit() {
  errorMessage.value = "";
  submitting.value = true;
  try {
    await adminLogin(email.value, password.value);
    await router.replace("/admin");
  } catch (err: unknown) {
    errorMessage.value = "이메일 또는 비밀번호가 올바르지 않습니다.";
  } finally {
    submitting.value = false;
  }
}
</script>
