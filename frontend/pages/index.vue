<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white border-b border-gray-100">
      <div class="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900">기업 소개 플랫폼</h1>
        <div class="flex gap-3">
          <NuxtLink
            to="/login"
            class="text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            로그인
          </NuxtLink>
          <NuxtLink
            to="/signup"
            class="text-sm bg-gray-900 text-white px-4 py-1.5 rounded-lg hover:bg-gray-700 transition-colors"
          >
            기업 등록
          </NuxtLink>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-10">
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900">승인된 기업 목록</h2>
        <p class="text-gray-500 mt-1 text-sm">검증된 기업들을 탐색해보세요.</p>
      </div>

      <div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="i in 6"
          :key="i"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 animate-pulse"
        >
          <div class="w-12 h-12 bg-gray-200 rounded-xl mb-4" />
          <div class="h-4 bg-gray-200 rounded w-2/3 mb-2" />
          <div class="h-3 bg-gray-100 rounded w-full mb-1" />
          <div class="h-3 bg-gray-100 rounded w-4/5" />
        </div>
      </div>

      <div v-else-if="error" class="text-center py-20 text-red-500">
        기업 목록을 불러오지 못했습니다.
      </div>

      <div
        v-else-if="companies && companies.length === 0"
        class="text-center py-20 text-gray-400"
      >
        등록된 기업이 없습니다.
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="company in companies"
          :key="company.id"
          :to="`/companies/${company.id}`"
          class="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 hover:shadow-md hover:border-gray-200 transition-all group"
        >
          <div class="flex items-start gap-4 mb-4">
            <img
              v-if="company.logo_url"
              :src="company.logo_url"
              :alt="company.name ?? ''"
              class="w-12 h-12 rounded-xl object-cover flex-shrink-0"
            />
            <div
              v-else
              class="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0"
            >
              <span class="text-lg font-bold text-gray-400">
                {{ (company.name ?? '?')[0].toUpperCase() }}
              </span>
            </div>
            <div class="min-w-0">
              <h3 class="font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                {{ company.name ?? '(이름 없음)' }}
              </h3>
              <p v-if="company.industry" class="text-xs text-gray-400 mt-0.5">
                {{ company.industry }}
              </p>
            </div>
          </div>

          <p
            v-if="company.description"
            class="text-sm text-gray-500 line-clamp-2 mb-4"
          >
            {{ company.description }}
          </p>

          <div class="flex flex-wrap gap-2">
            <span
              v-if="company.company_size"
              class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full"
            >
              {{ company.company_size }}
            </span>
            <span
              v-if="company.address"
              class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full truncate max-w-[140px]"
            >
              {{ company.address }}
            </span>
          </div>
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useCompanies } from "~/composables/useCompanies";

const { fetchCompanies } = useCompanies();

const { data: companies, pending, error } = await useAsyncData(
  "companies",
  () => fetchCompanies()
);
</script>
