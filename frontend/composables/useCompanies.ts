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

export interface CompanySearchParams {
  q?: string;
  industry?: string;
  region?: string;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: string | null;
}

export function useCompanies() {
  const config = useRuntimeConfig();
  const base = config.public.apiBase;

  async function fetchCompanies(params?: CompanySearchParams): Promise<CompanyCard[]> {
    const query: Record<string, string> = {};
    if (params?.q) query.q = params.q;
    if (params?.industry) query.industry = params.industry;
    if (params?.region) query.region = params.region;

    const res = await $fetch<ApiResponse<CompanyCard[]>>(
      `${base}/api/public/companies`,
      { query }
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
