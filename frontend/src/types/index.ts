// api types - all interfaces for backend responses

export interface User {
    id: number;
    email: string;
    full_name: string;
    is_active: boolean;
    created_at: string | null;
}

export interface Project {
    id: number;
    name: string;
    description: string;
    owner_id: number;
    role?: string;
    created_at: string | null;
    updated_at: string | null;
    stages?: Stage[];
}

export interface Stage {
    id: number;
    name: string;
    position: number;
    project_id: number;
}

export interface Task {
    id: number;
    title: string;
    description: string;
    position: number;
    project_id: number;
    stage_id: number;
    assignee_id: number | null;
    assignee: User | null;
    created_by: number;
    created_at: string | null;
    updated_at: string | null;
}

export interface Comment {
    id: number;
    content: string;
    task_id: number;
    author_id: number;
    author: User | null;
    created_at: string | null;
    updated_at: string | null;
}

export interface ProjectMember {
    id: number;
    project_id: number;
    user_id: number;
    role: string;
    status: string;
    user: User | null;
    project_name?: string;
    created_at: string | null;
}

export interface ApiResponse<T> {
    status: "success" | "error";
    request_id: string;
    data: T;
    message: string | null;
    errors?: Record<string, string[]>;
}
