<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-100">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
        <NuxtLink
          to="/"
          class="text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          ← 목록으로
        </NuxtLink>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-10">
      <div v-if="pending" class="animate-pulse space-y-6">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 bg-gray-200 rounded-2xl" />
          <div class="space-y-2">
            <div class="h-6 bg-gray-200 rounded w-48" />
            <div class="h-4 bg-gray-100 rounded w-24" />
          </div>
        </div>
        <div class="h-4 bg-gray-100 rounded w-full" />
        <div class="h-4 bg-gray-100 rounded w-4/5" />
      </div>

      <div v-else-if="error || !company" class="text-center py-20 text-gray-400">
        기업 정보를 찾을 수 없습니다.
      </div>

      <div v-else class="space-y-8">
        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
          <div class="flex items-start gap-6 mb-6">
            <img
              v-if="company.logo_url"
              :src="company.logo_url"
              :alt="company.name ?? ''"
              class="w-20 h-20 rounded-2xl object-cover flex-shrink-0"
            />
            <div
              v-else
              class="w-20 h-20 rounded-2xl bg-gray-100 flex items-center justify-center flex-shrink-0"
            >
              <span class="text-3xl font-bold text-gray-300">
                {{ (company.name ?? '?')[0].toUpperCase() }}
              </span>
            </div>

            <div class="min-w-0 flex-1">
              <h1 class="text-2xl font-bold text-gray-900">
                {{ company.name ?? '(이름 없음)' }}
              </h1>
              <p v-if="company.industry" class="text-gray-500 mt-1">
                {{ company.industry }}
              </p>
              <div class="flex flex-wrap gap-2 mt-3">
                <span
                  v-if="company.company_size"
                  class="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full"
                >
                  {{ company.company_size }}
                </span>
                <span
                  v-if="company.founded_year"
                  class="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full"
                >
                  {{ company.founded_year }}년 설립
                </span>
                <span
                  v-if="company.employee_count"
                  class="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full"
                >
                  직원 {{ company.employee_count }}명
                </span>
              </div>
            </div>
          </div>

          <p
            v-if="company.description"
            class="text-gray-600 leading-relaxed"
          >
            {{ company.description }}
          </p>
        </div>

        <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">연락처 정보</h2>
          <dl class="space-y-3">
            <div v-if="company.address" class="flex gap-3">
              <dt class="text-sm text-gray-400 w-20 flex-shrink-0">주소</dt>
              <dd class="text-sm text-gray-700">{{ company.address }}</dd>
            </div>
            <div v-if="company.contact_email" class="flex gap-3">
              <dt class="text-sm text-gray-400 w-20 flex-shrink-0">이메일</dt>
              <dd class="text-sm text-gray-700">{{ company.contact_email }}</dd>
            </div>
            <div v-if="company.phone" class="flex gap-3">
              <dt class="text-sm text-gray-400 w-20 flex-shrink-0">전화</dt>
              <dd class="text-sm text-gray-700">{{ company.phone }}</dd>
            </div>
            <div v-if="company.website" class="flex gap-3">
              <dt class="text-sm text-gray-400 w-20 flex-shrink-0">웹사이트</dt>
              <dd class="text-sm">
                <a
                  :href="company.website"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-blue-600 hover:underline"
                >
                  {{ company.website }}
                </a>
              </dd>
            </div>
          </dl>

          <div
            v-if="company.instagram_url || company.linkedin_url"
            class="flex gap-3 mt-5 pt-5 border-t border-gray-100"
          >
            <a
              v-if="company.instagram_url"
              :href="company.instagram_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              Instagram
            </a>
            <a
              v-if="company.linkedin_url"
              :href="company.linkedin_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              LinkedIn
            </a>
          </div>
        </div>

        <div
          v-if="company.image_urls && company.image_urls.length > 0"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-8"
        >
          <h2 class="text-lg font-semibold text-gray-900 mb-4">이미지</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <img
              v-for="(url, i) in company.image_urls"
              :key="i"
              :src="url"
              :alt="`${company.name} 이미지 ${i + 1}`"
              class="w-full aspect-video object-cover rounded-xl"
            />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useCompanies } from "~/composables/useCompanies";

const route = useRoute();
const { fetchCompany } = useCompanies();

const id = Number(route.params.id);

const { data: company, pending, error } = await useAsyncData(
  `company-${id}`,
  () => fetchCompany(id)
);

useHead({
  title: company.value?.name ?? "기업 상세",
});
</script>
