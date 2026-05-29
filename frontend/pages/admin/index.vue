<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-100">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900">관리자 패널</h1>
        <button
          class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          @click="handleLogout"
        >
          로그아웃
        </button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-10">
      <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900">기업 관리</h2>
        <p class="text-gray-500 mt-1 text-sm">
          등록된 기업을 검토하고 승인/거절하세요.
        </p>
      </div>

      <!-- 상태 필터 탭 -->
      <div class="flex gap-2 mb-8 border-b border-gray-100">
        <button
          v-for="tab in STATUS_TABS"
          :key="tab.value ?? 'all'"
          class="px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors"
          :class="
            activeStatus === tab.value
              ? 'border-gray-900 text-gray-900'
              : 'border-transparent text-gray-400 hover:text-gray-600'
          "
          @click="activeStatus = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- 로딩 스켈레톤 -->
      <div
        v-if="pending"
        class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <div
          v-for="i in 5"
          :key="i"
          class="flex items-center gap-4 px-6 py-4 border-b border-gray-50 animate-pulse"
        >
          <div class="h-4 bg-gray-200 rounded w-1/4" />
          <div class="h-4 bg-gray-100 rounded w-1/5" />
          <div class="h-4 bg-gray-100 rounded w-16" />
        </div>
      </div>

      <div v-else-if="error" class="text-center py-20 text-red-500">
        기업 목록을 불러오지 못했습니다.
      </div>

      <div
        v-else-if="companies && companies.length === 0"
        class="text-center py-20 text-gray-400"
      >
        해당 상태의 기업이 없습니다.
      </div>

      <div
        v-else
        class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden"
      >
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-gray-400 border-b border-gray-100">
              <th class="px-6 py-3 font-medium">회사명</th>
              <th class="px-6 py-3 font-medium">업종</th>
              <th class="px-6 py-3 font-medium">상태</th>
              <th class="px-6 py-3 font-medium">등록일</th>
              <th class="px-6 py-3 font-medium text-right">관리</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="company in companies"
              :key="company.id"
              class="border-b border-gray-50 last:border-0 hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4 font-medium text-gray-900">
                {{ company.name ?? "(이름 없음)" }}
              </td>
              <td class="px-6 py-4 text-gray-500">
                {{ company.industry ?? "-" }}
              </td>
              <td class="px-6 py-4">
                <span
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="STATUS_BADGE[company.status]"
                >
                  {{ STATUS_LABEL[company.status] }}
                </span>
              </td>
              <td class="px-6 py-4 text-gray-500">
                {{ formatDate(company.created_at) }}
              </td>
              <td class="px-6 py-4 text-right">
                <NuxtLink
                  :to="`/admin/companies/${company.id}`"
                  class="text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  상세보기
                </NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import {
  useAdmin,
  type CompanyStatus,
  type AdminCompany,
} from "~/composables/useAdmin";

definePageMeta({ middleware: "admin-auth" });

const { listCompanies, adminLogout } = useAdmin();
const router = useRouter();

const STATUS_TABS: { label: string; value: CompanyStatus | undefined }[] = [
  { label: "전체", value: undefined },
  { label: "대기중", value: "pending" },
  { label: "승인", value: "approved" },
  { label: "거절", value: "rejected" },
];

const STATUS_LABEL: Record<CompanyStatus, string> = {
  pending: "대기중",
  approved: "승인",
  rejected: "거절",
};

const STATUS_BADGE: Record<CompanyStatus, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
};

const activeStatus = ref<CompanyStatus | undefined>(undefined);

function formatDate(value: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return date.toLocaleDateString("ko-KR");
}

const { data: companies, pending, error, refresh } = await useAsyncData<
  AdminCompany[]
>("admin-companies", () => listCompanies(activeStatus.value), {
  default: () => [],
  server: false,
});

watch(activeStatus, () => refresh());

function handleLogout() {
  adminLogout();
  router.replace("/admin/login");
}
</script>
