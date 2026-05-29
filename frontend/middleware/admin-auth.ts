import { useAdmin } from "~/composables/useAdmin";

// /admin 하위 경로 인증 가드.
// 토큰은 localStorage에만 존재하므로 SSR에서는 검사하지 않고
// client-side에서만 토큰 유무를 확인한다.
export default defineNuxtRouteMiddleware(() => {
  if (!import.meta.client) return;

  const { getAdminToken } = useAdmin();
  if (!getAdminToken()) {
    return navigateTo("/admin/login");
  }
});
