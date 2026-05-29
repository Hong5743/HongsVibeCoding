<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-100">
      <div class="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900">관리자 패널</h1>
        <NuxtLink
          to="/admin"
          class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          목록으로
        </NuxtLink>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-6 py-10">
      <!-- 로딩 -->
      <div
        v-if="pending"
        class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 animate-pulse"
      >
        <div class="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div class="h-4 bg-gray-100 rounded w-full mb-2" />
        <div class="h-4 bg-gray-100 rounded w-4/5" />
      </div>

      <div v-else-if="error || !company" class="text-center py-20 text-red-500">
        기업 정보를 불러오지 못했습니다.
      </div>

      <div v-else>
        <!-- 헤더 -->
        <div class="flex items-start gap-4 mb-6">
          <img
            v-if="company.logo_url"
            :src="company.logo_url"
            :alt="company.name ?? ''"
            class="w-16 h-16 rounded-xl object-cover flex-shrink-0"
          />
          <div
            v-else
            class="w-16 h-16 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0"
          >
            <span class="text-2xl font-bold text-gray-400">
              {{ (company.name ?? "?")[0].toUpperCase() }}
            </span>
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <h2 class="text-2xl font-bold text-gray-900">
                {{ company.name ?? "(이름 없음)" }}
              </h2>
              <span
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="STATUS_BADGE[company.status]"
              >
                {{ STATUS_LABEL[company.status] }}
              </span>
            </div>
            <p v-if="company.industry" class="text-sm text-gray-500 mt-1">
              {{ company.industry }}
            </p>
          </div>
        </div>

        <!-- 거절 사유 -->
        <div
          v-if="company.status === 'rejected' && company.rejection_reason"
          class="bg-red-50 border border-red-100 rounded-xl px-4 py-3 mb-6"
        >
          <p class="text-xs font-medium text-red-500 mb-1">거절 사유</p>
          <p class="text-sm text-red-700">{{ company.rejection_reason }}</p>
        </div>

        <!-- 상세 정보 -->
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
          <dl class="divide-y divide-gray-50">
            <DetailRow label="이메일" :value="company.email" />
            <DetailRow label="설명" :value="company.description" />
            <DetailRow label="업종" :value="company.industry" />
            <DetailRow
              label="설립연도"
              :value="company.founded_year ? String(company.founded_year) : null"
            />
            <DetailRow
              label="직원 수"
              :value="
                company.employee_count ? String(company.employee_count) : null
              "
            />
            <DetailRow label="회사 규모" :value="company.company_size" />
            <DetailRow label="웹사이트" :value="company.website" />
            <DetailRow label="문의 이메일" :value="company.contact_email" />
            <DetailRow label="전화번호" :value="company.phone" />
            <DetailRow label="주소" :value="company.address" />
          </dl>
        </div>

        <!-- 액션 버튼 -->
        <div class="flex flex-wrap gap-3">
          <button
            v-if="company.status !== 'approved'"
            :disabled="actionPending"
            class="px-5 py-2.5 text-sm font-medium bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            @click="handleApprove"
          >
            승인
          </button>
          <button
            v-if="company.status !== 'rejected'"
            :disabled="actionPending"
            class="px-5 py-2.5 text-sm font-medium bg-white text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
            @click="openRejectModal"
          >
            거절
          </button>
          <button
            v-if="company.status !== 'pending'"
            :disabled="actionPending"
            class="px-5 py-2.5 text-sm font-medium bg-white text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            @click="handleDelete"
          >
            삭제
          </button>
        </div>

        <p v-if="actionError" class="text-sm text-red-500 mt-4">
          {{ actionError }}
        </p>
      </div>
    </main>

    <!-- 거절 사유 모달 -->
    <div
      v-if="showRejectModal"
      class="fixed inset-0 bg-black/40 flex items-center justify-center px-6 z-50"
      @click.self="closeRejectModal"
    >
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-900 mb-1">거절 사유 입력</h3>
        <p class="text-sm text-gray-500 mb-4">
          기업에게 전달할 거절 사유를 작성하세요.
        </p>
        <textarea
          v-model="rejectReason"
          rows="4"
          placeholder="거절 사유를 입력하세요"
          class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent resize-none"
        />
        <div class="flex justify-end gap-3 mt-4">
          <button
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
            @click="closeRejectModal"
          >
            취소
          </button>
          <button
            :disabled="!rejectReason.trim() || actionPending"
            class="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            @click="handleReject"
          >
            거절 확정
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h } from "vue";
import {
  useAdmin,
  type CompanyStatus,
  type AdminCompany,
} from "~/composables/useAdmin";

definePageMeta({ middleware: "admin-auth" });

const { getCompany, approveCompany, rejectCompany, deleteCompany } = useAdmin();
const route = useRoute();
const router = useRouter();

const companyId = Number(route.params.id);

// 비정상 ID 접근 시 목록으로 이동
if (Number.isNaN(companyId)) {
  await navigateTo("/admin");
}

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

// 단순 라벨/값 표시 행 컴포넌트
const DetailRow = (props: { label: string; value: string | null }) =>
  h("div", { class: "py-3 flex gap-4" }, [
    h("dt", { class: "w-28 flex-shrink-0 text-sm text-gray-400" }, props.label),
    h(
      "dd",
      { class: "text-sm text-gray-900 break-words min-w-0" },
      props.value ?? "-"
    ),
  ]);

const { data: company, pending, error, refresh } = await useAsyncData<
  AdminCompany | null
>(`admin-company-${companyId}`, () => getCompany(companyId), {
  default: () => null,
  server: false,
});

const actionPending = ref(false);
const actionError = ref("");
const showRejectModal = ref(false);
const rejectReason = ref("");

async function handleApprove() {
  actionError.value = "";
  actionPending.value = true;
  try {
    await approveCompany(companyId);
    await refresh();
  } catch {
    actionError.value = "승인 처리에 실패했습니다.";
  } finally {
    actionPending.value = false;
  }
}

function openRejectModal() {
  rejectReason.value = "";
  showRejectModal.value = true;
}

function closeRejectModal() {
  showRejectModal.value = false;
}

async function handleReject() {
  if (!rejectReason.value.trim()) return;
  actionError.value = "";
  actionPending.value = true;
  try {
    await rejectCompany(companyId, rejectReason.value.trim());
    showRejectModal.value = false;
    await refresh();
  } catch {
    actionError.value = "거절 처리에 실패했습니다.";
  } finally {
    actionPending.value = false;
  }
}

async function handleDelete() {
  if (!window.confirm("정말 이 기업을 삭제하시겠습니까?")) return;
  actionError.value = "";
  actionPending.value = true;
  try {
    await deleteCompany(companyId);
    await router.replace("/admin");
  } catch {
    actionError.value = "삭제 처리에 실패했습니다.";
    actionPending.value = false;
  }
}
</script>
