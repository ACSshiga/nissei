const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  token?: string;
}

export async function apiFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// 型定義
export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface Project {
  id: string;
  management_no: string;
  series?: string;
  generation?: string;
  tonnage?: string;
  spec_tags?: string;
  machine_no?: string;
  commission_content?: string;
  inquiry_type?: string;
  work_category?: string;
  estimated_hours?: number;
  actual_hours: number;
  status: string;
  start_date?: string;
  completion_date?: string;
  drawing_deadline?: string;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkLog {
  id: string;
  project_id: string;
  user_id: string;
  work_date: string;
  start_time?: string;
  end_time?: string;
  duration_minutes: number;
  work_content?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkLogSummary {
  project_id: string;
  management_no: string;
  estimated_hours: number;
  actual_hours: number;
  by_user: Array<{
    username: string;
    total_minutes: number;
    entry_count: number;
  }>;
  by_date: Array<{
    work_date: string;
    total_minutes: number;
    entry_count: number;
  }>;
}

// マスタデータ型定義
export interface MasterShinchoku {
  id: string;
  status_name: string;
  background_color?: string;
  completion_trigger: boolean;
  start_date_trigger: boolean;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MasterSagyouKubun {
  id: string;
  kubun_name: string;
  background_color?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MasterToiawase {
  id: string;
  status_name: string;
  background_color?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MachineSeriesMaster {
  id: string;
  series_name: string;
  display_name: string;
  description?: string;
  category?: string;
  checklist_template_category?: string;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const api = {
  // 認証
  auth: {
    register: (data: { email: string; username: string; password: string }) =>
      apiFetch('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    login: (data: { email: string; password: string }) =>
      apiFetch<{ access_token: string; token_type: string }>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    getMe: (token: string) =>
      apiFetch<User>('/api/auth/me', {
        token,
      }),
  },

  // 案件管理
  projects: {
    list: (token: string, params?: { page?: number; per_page?: number; status?: string; machine_no?: string }) => {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.status) queryParams.append('status', params.status);
      if (params?.machine_no) queryParams.append('machine_no', params.machine_no);

      return apiFetch<{
        projects: Project[];
        total: number;
        page: number;
        per_page: number;
      }>(`/api/projects?${queryParams}`, { token });
    },

    get: (token: string, projectId: string) =>
      apiFetch<Project>(`/api/projects/${projectId}`, { token }),

    create: (token: string, data: Partial<Project>) =>
      apiFetch<Project>('/api/projects', {
        method: 'POST',
        body: JSON.stringify(data),
        token,
      }),

    update: (token: string, projectId: string, data: Partial<Project>) =>
      apiFetch<Project>(`/api/projects/${projectId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
        token,
      }),

    delete: (token: string, projectId: string) =>
      apiFetch<void>(`/api/projects/${projectId}`, {
        method: 'DELETE',
        token,
      }),
  },

  // 工数入力
  worklogs: {
    list: (token: string, params?: { page?: number; per_page?: number; project_id?: string; work_date?: string; user_id?: string }) => {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.per_page) queryParams.append('per_page', params.per_page.toString());
      if (params?.project_id) queryParams.append('project_id', params.project_id);
      if (params?.work_date) queryParams.append('work_date', params.work_date);
      if (params?.user_id) queryParams.append('user_id', params.user_id);

      return apiFetch<{
        worklogs: WorkLog[];
        total: number;
        page: number;
        per_page: number;
      }>(`/api/worklogs?${queryParams}`, { token });
    },

    get: (token: string, worklogId: string) =>
      apiFetch<WorkLog>(`/api/worklogs/${worklogId}`, { token }),

    create: (token: string, data: Partial<WorkLog>) =>
      apiFetch<WorkLog>('/api/worklogs', {
        method: 'POST',
        body: JSON.stringify(data),
        token,
      }),

    update: (token: string, worklogId: string, data: Partial<WorkLog>) =>
      apiFetch<WorkLog>(`/api/worklogs/${worklogId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
        token,
      }),

    delete: (token: string, worklogId: string) =>
      apiFetch<void>(`/api/worklogs/${worklogId}`, {
        method: 'DELETE',
        token,
      }),

    getSummary: (token: string, projectId: string) =>
      apiFetch<WorkLogSummary>(`/api/worklogs/summary/${projectId}`, { token }),
  },

  // マスタ管理
  masters: {
    // 進捗マスタ
    shinchoku: {
      list: (token: string, includeInactive?: boolean) => {
        const params = includeInactive ? '?include_inactive=true' : '';
        return apiFetch<MasterShinchoku[]>(`/api/masters/shinchoku${params}`, { token });
      },

      get: (token: string, id: string) =>
        apiFetch<MasterShinchoku>(`/api/masters/shinchoku/${id}`, { token }),

      create: (token: string, data: Omit<MasterShinchoku, 'id' | 'created_at' | 'updated_at'>) =>
        apiFetch<MasterShinchoku>('/api/masters/shinchoku', {
          method: 'POST',
          body: JSON.stringify(data),
          token,
        }),

      update: (token: string, id: string, data: Partial<Omit<MasterShinchoku, 'id' | 'created_at' | 'updated_at'>>) =>
        apiFetch<MasterShinchoku>(`/api/masters/shinchoku/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data),
          token,
        }),

      delete: (token: string, id: string) =>
        apiFetch<void>(`/api/masters/shinchoku/${id}`, {
          method: 'DELETE',
          token,
        }),
    },

    // 作業区分マスタ
    sagyouKubun: {
      list: (token: string, includeInactive?: boolean) => {
        const params = includeInactive ? '?include_inactive=true' : '';
        return apiFetch<MasterSagyouKubun[]>(`/api/masters/sagyou-kubun${params}`, { token });
      },

      get: (token: string, id: string) =>
        apiFetch<MasterSagyouKubun>(`/api/masters/sagyou-kubun/${id}`, { token }),

      create: (token: string, data: Omit<MasterSagyouKubun, 'id' | 'created_at' | 'updated_at'>) =>
        apiFetch<MasterSagyouKubun>('/api/masters/sagyou-kubun', {
          method: 'POST',
          body: JSON.stringify(data),
          token,
        }),

      update: (token: string, id: string, data: Partial<Omit<MasterSagyouKubun, 'id' | 'created_at' | 'updated_at'>>) =>
        apiFetch<MasterSagyouKubun>(`/api/masters/sagyou-kubun/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data),
          token,
        }),

      delete: (token: string, id: string) =>
        apiFetch<void>(`/api/masters/sagyou-kubun/${id}`, {
          method: 'DELETE',
          token,
        }),
    },

    // 問い合わせマスタ
    toiawase: {
      list: (token: string, includeInactive?: boolean) => {
        const params = includeInactive ? '?include_inactive=true' : '';
        return apiFetch<MasterToiawase[]>(`/api/masters/toiawase${params}`, { token });
      },

      get: (token: string, id: string) =>
        apiFetch<MasterToiawase>(`/api/masters/toiawase/${id}`, { token }),

      create: (token: string, data: Omit<MasterToiawase, 'id' | 'created_at' | 'updated_at'>) =>
        apiFetch<MasterToiawase>('/api/masters/toiawase', {
          method: 'POST',
          body: JSON.stringify(data),
          token,
        }),

      update: (token: string, id: string, data: Partial<Omit<MasterToiawase, 'id' | 'created_at' | 'updated_at'>>) =>
        apiFetch<MasterToiawase>(`/api/masters/toiawase/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data),
          token,
        }),

      delete: (token: string, id: string) =>
        apiFetch<void>(`/api/masters/toiawase/${id}`, {
          method: 'DELETE',
          token,
        }),
    },

    // 機種シリーズマスタ
    machineSeries: {
      list: (token: string, includeInactive?: boolean) => {
        const params = includeInactive ? '?include_inactive=true' : '';
        return apiFetch<MachineSeriesMaster[]>(`/api/masters/machine-series${params}`, { token });
      },

      get: (token: string, id: string) =>
        apiFetch<MachineSeriesMaster>(`/api/masters/machine-series/${id}`, { token }),

      create: (token: string, data: Omit<MachineSeriesMaster, 'id' | 'created_at' | 'updated_at'>) =>
        apiFetch<MachineSeriesMaster>('/api/masters/machine-series', {
          method: 'POST',
          body: JSON.stringify(data),
          token,
        }),

      update: (token: string, id: string, data: Partial<Omit<MachineSeriesMaster, 'id' | 'created_at' | 'updated_at'>>) =>
        apiFetch<MachineSeriesMaster>(`/api/masters/machine-series/${id}`, {
          method: 'PUT',
          body: JSON.stringify(data),
          token,
        }),

      delete: (token: string, id: string) =>
        apiFetch<void>(`/api/masters/machine-series/${id}`, {
          method: 'DELETE',
          token,
        }),
    },
  },
};