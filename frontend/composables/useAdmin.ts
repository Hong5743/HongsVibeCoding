export type CompanyStatus = "pending" | "approved" | "rejected";

export interface AdminCompany {
  id: number;
  email: string | null;
  status: CompanyStatus;
  name: string | null;
  logo_url: string | null;
  description: string | null;
  industry: string | null;
  founded_year: number | null;
  employee_count: number | null;
  company_size: string | null;
  website: string | null;
  contact_email: string | null;
  phone: string | null;
  address: string | null;
  rejection_reason: string | null;
  created_at: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: string | null;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

const TOKEN_KEY = "admin_token";

export function useAdmin() {
  const config = useRuntimeConfig();
  const base = `${config.public.apiBase}/api/admin`;

  function getAdminToken(): string | null {
    if (import.meta.client) {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  }

  function setAdminToken(token: string): void {
    if (import.meta.client) {
      localStorage.setItem(TOKEN_KEY, token);
    }
  }

  function adminLogout(): void {
    if (import.meta.client) {
      localStorage.removeItem(TOKEN_KEY);
    }
  }

  function authHeaders(): Record<string, string> {
    const token = getAdminToken();
    if (!token) {
      throw new Error("관리자 인증이 필요합니다. 다시 로그인해주세요.");
    }
    return { Authorization: `Bearer ${token}` };
  }

  async function adminLogin(email: string, password: string): Promise<void> {
    const res = await $fetch<LoginResponse>(`${base}/login`, {
      method: "POST",
      body: { email, password },
    });
    setAdminToken(res.access_token);
  }

  async function listCompanies(status?: CompanyStatus): Promise<AdminCompany[]> {
    const query: Record<string, string> = {};
    if (status) query.status = status;

    const res = await $fetch<ApiResponse<AdminCompany[]>>(`${base}/companies`, {
      headers: authHeaders(),
      query,
    });
    return res.data;
  }

  async function getCompany(id: number): Promise<AdminCompany> {
    const res = await $fetch<ApiResponse<AdminCompany>>(
      `${base}/companies/${id}`,
      { headers: authHeaders() }
    );
    return res.data;
  }

  async function approveCompany(id: number): Promise<AdminCompany> {
    const res = await $fetch<ApiResponse<AdminCompany>>(
      `${base}/companies/${id}/approve`,
      { method: "PUT", headers: authHeaders() }
    );
    return res.data;
  }

  async function rejectCompany(
    id: number,
    reason: string
  ): Promise<AdminCompany> {
    const res = await $fetch<ApiResponse<AdminCompany>>(
      `${base}/companies/${id}/reject`,
      { method: "PUT", headers: authHeaders(), body: { reason } }
    );
    return res.data;
  }

  async function deleteCompany(id: number): Promise<void> {
    await $fetch<ApiResponse<null>>(`${base}/companies/${id}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
  }

  return {
    getAdminToken,
    adminLogin,
    adminLogout,
    listCompanies,
    getCompany,
    approveCompany,
    rejectCompany,
    deleteCompany,
  };
}
