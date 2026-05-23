import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore();
  const protectedRoutes = ["/dashboard"];

  if (protectedRoutes.some((r) => to.path.startsWith(r)) && !auth.isLoggedIn) {
    return navigateTo("/login");
  }
});
