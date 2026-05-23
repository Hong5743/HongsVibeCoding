import { defineStore } from "pinia";

interface CompanyUser {
  id: number;
  email: string;
  is_verified: boolean;
  status: "pending" | "approved" | "rejected";
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: CompanyUser | null;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    accessToken: import.meta.client ? localStorage.getItem("access_token") : null,
    refreshToken: import.meta.client ? localStorage.getItem("refresh_token") : null,
    user: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },

  actions: {
    setTokens(accessToken: string, refreshToken: string) {
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      if (import.meta.client) {
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
      }
    },

    logout() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      if (import.meta.client) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
    },

    async login(email: string, password: string) {
      const config = useRuntimeConfig();
      const res = await $fetch<{ access_token: string; refresh_token: string }>(
        `${config.public.apiBase}/api/auth/login`,
        { method: "POST", body: { email, password } }
      );
      this.setTokens(res.access_token, res.refresh_token);
      await this.fetchMe();
    },

    async signup(email: string, password: string) {
      const config = useRuntimeConfig();
      return await $fetch(`${config.public.apiBase}/api/auth/signup`, {
        method: "POST",
        body: { email, password },
      });
    },

    async fetchMe() {
      if (!this.accessToken) return;
      const config = useRuntimeConfig();
      try {
        const res = await $fetch<{ success: boolean; data: CompanyUser }>(
          `${config.public.apiBase}/api/auth/me`,
          { headers: { Authorization: `Bearer ${this.accessToken}` } }
        );
        this.user = res.data;
      } catch {
        this.logout();
      }
    },

    async refreshAccessToken() {
      if (!this.refreshToken) return;
      const config = useRuntimeConfig();
      try {
        const res = await $fetch<{ success: boolean; data: { access_token: string } }>(
          `${config.public.apiBase}/api/auth/refresh`,
          { method: "POST", body: { refresh_token: this.refreshToken } }
        );
        this.accessToken = res.data.access_token;
        if (import.meta.client) {
          localStorage.setItem("access_token", res.data.access_token);
        }
      } catch {
        this.logout();
      }
    },
  },
});
