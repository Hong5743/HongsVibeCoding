export interface CompanyCard {
  id: number;
  name: string | null;
  logo_url: string | null;
  description: string | null;
  industry: string | null;
  company_size: string | null;
  address: string | null;
}

export interface CompanyDetail {
  id: number;
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
  image_urls: string[] | null;
  instagram_url: string | null;
  linkedin_url: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: string | null;
}

export function useCompanies() {
  const config = useRuntimeConfig();
  const base = config.public.apiBase;

  async function fetchCompanies(): Promise<CompanyCard[]> {
    const res = await $fetch<ApiResponse<CompanyCard[]>>(
      `${base}/api/public/companies`
    );
    return res.data;
  }

  async function fetchCompany(id: number): Promise<CompanyDetail> {
    const res = await $fetch<ApiResponse<CompanyDetail>>(
      `${base}/api/public/companies/${id}`
    );
    return res.data;
  }

  return { fetchCompanies, fetchCompany };
}
