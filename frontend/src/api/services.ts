import api from "./client";
import type { ApiResponse, User, Project, Task, Comment, ProjectMember } from "../types";

// auth
export const authApi = {
    register: (data: { email: string; full_name: string; password: string }) =>
        api.post<ApiResponse<User>>("/auth/register", data),

    login: (data: { email: string; password: string }) =>
        api.post<ApiResponse<null>>("/auth/login", data),

    logout: () => api.post<ApiResponse<null>>("/auth/logout"),

    me: () => api.get<ApiResponse<User>>("/auth/me"),

    listUsers: () => api.get<ApiResponse<User[]>>("/auth/users"),
};

// projects
export const projectApi = {
    create: (data: { name: string; description?: string }) =>
        api.post<ApiResponse<Project>>("/projects", data),

    list: () => api.get<ApiResponse<Project[]>>("/projects"),

    get: (id: number) => api.get<ApiResponse<Project>>(`/projects/${id}`),

    update: (id: number, data: { name?: string; description?: string }) =>
        api.put<ApiResponse<Project>>(`/projects/${id}`, data),

    delete: (id: number) => api.delete<ApiResponse<null>>(`/projects/${id}`),
};

// tasks
export const taskApi = {
    create: (projectId: number, data: { title: string; description?: string; stage_id: number; assignee_id?: number }) =>
        api.post<ApiResponse<Task>>(`/tasks?project_id=${projectId}`, data),

    list: (projectId: number) =>
        api.get<ApiResponse<Task[]>>(`/tasks?project_id=${projectId}`),

    get: (id: number) => api.get<ApiResponse<Task>>(`/tasks/${id}`),

    update: (id: number, data: { title?: string; description?: string; assignee_id?: number | null }) =>
        api.put<ApiResponse<Task>>(`/tasks/${id}`, data),

    move: (id: number, data: { stage_id: number; position: number }) =>
        api.put<ApiResponse<Task>>(`/tasks/${id}/move`, data),

    delete: (id: number) => api.delete<ApiResponse<null>>(`/tasks/${id}`),
};

// comments
export const commentApi = {
    create: (taskId: number, data: { content: string }) =>
        api.post<ApiResponse<Comment>>(`/comments?task_id=${taskId}`, data),

    list: (taskId: number) =>
        api.get<ApiResponse<Comment[]>>(`/comments?task_id=${taskId}`),

    delete: (id: number) => api.delete<ApiResponse<null>>(`/comments/${id}`),
};

// members
export const memberApi = {
    add: (projectId: number, data: { email: string; role: string }) =>
        api.post<ApiResponse<ProjectMember>>(`/members/add?project_id=${projectId}`, data),

    list: (projectId: number) =>
        api.get<ApiResponse<ProjectMember[]>>(`/members?project_id=${projectId}`),

    remove: (projectId: number, userId: number) =>
        api.delete<ApiResponse<null>>(`/members/${userId}?project_id=${projectId}`),
};

