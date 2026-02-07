
export interface VcfBatch {
    id: string;
    file_name: string;
    contact_count: number;
    prefix: string;
    start_serial: number;
    status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'COMPLETED';
    agent_id?: string;
    agent_name?: string;
    assigned_at?: string;
    created_at: string;
}

export interface ProgressReportRequest {
    batch_id: string;
    session_type: 'morning' | 'evening';
    count: number;
    notes?: string;
}

export interface TodayProgress {
    date: string;
    morning_count: number;
    evening_count: number;
    total: number;
    goal: number;
    progress_percent: number;
}
