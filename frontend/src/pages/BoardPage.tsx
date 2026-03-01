import { useState, useEffect, type FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { DragDropContext, Droppable, Draggable, type DropResult } from "@hello-pangea/dnd";
import { useAuth } from "../context/AuthContext";
import { projectApi, taskApi, memberApi, authApi } from "../api/services";
import type { Project, Task, ProjectMember, User } from "../types";

export default function BoardPage() {
    const { projectId } = useParams<{ projectId: string }>();
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const pid = Number(projectId);

    const [project, setProject] = useState<Project | null>(null);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [members, setMembers] = useState<ProjectMember[]>([]);
    const [allUsers, setAllUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // filtering
    const [filterMyTasks, setFilterMyTasks] = useState(false);

    // create task form
    const [showAddTask, setShowAddTask] = useState<number | null>(null);
    const [newTaskTitle, setNewTaskTitle] = useState("");
    const [newTaskAssignee, setNewTaskAssignee] = useState<number | undefined>();

    // invite modal
    const [showInvite, setShowInvite] = useState(false);
    const [inviteRole, setInviteRole] = useState("member");
    const [userSearch, setUserSearch] = useState("");

    useEffect(() => {
        fetchBoard();
    }, [pid]);

    const fetchBoard = async () => {
        setLoading(true);
        try {
            const [projRes, taskRes, memRes] = await Promise.all([
                projectApi.get(pid),
                taskApi.list(pid),
                memberApi.list(pid),
            ]);
            if (projRes.data.status === "success" && projRes.data.data) setProject(projRes.data.data);
            if (taskRes.data.status === "success") setTasks(taskRes.data.data || []);
            if (memRes.data.status === "success") setMembers(memRes.data.data || []);
        } catch {
            setError("failed to load board");
        } finally {
            setLoading(false);
        }
    };

    const fetchUsers = async () => {
        try {
            const res = await authApi.listUsers();
            if (res.data.status === "success") {
                setAllUsers(res.data.data || []);
            }
        } catch {
            setError("failed to load users");
        }
    };

    useEffect(() => {
        if (showInvite) fetchUsers();
    }, [showInvite]);

    const getTasksForStage = (stageId: number) => {
        let filtered = tasks.filter((t) => t.stage_id === stageId);
        if (filterMyTasks && user) {
            filtered = filtered.filter((t) => t.assignee_id === user.id);
        }
        return filtered.sort((a, b) => a.position - b.position);
    };

    const handleDragEnd = async (result: DropResult) => {
        if (!result.destination) return;

        const taskId = Number(result.draggableId);
        const destStageId = Number(result.destination.droppableId);
        const destIndex = result.destination.index;

        // optimistic update
        setTasks((prev) =>
            prev.map((t) => (t.id === taskId ? { ...t, stage_id: destStageId, position: destIndex } : t))
        );

        try {
            await taskApi.move(taskId, { stage_id: destStageId, position: destIndex });
        } catch {
            fetchBoard(); // revert on failure
        }
    };

    const handleAddTask = async (stageId: number, e: FormEvent) => {
        e.preventDefault();
        if (!newTaskTitle.trim()) return;
        try {
            const res = await taskApi.create(pid, {
                title: newTaskTitle,
                stage_id: stageId,
                assignee_id: newTaskAssignee
            });
            if (res.data.status === "success" && res.data.data) {
                setTasks((prev) => [...prev, res.data.data]);
            }
            setNewTaskTitle("");
            setNewTaskAssignee(undefined);
            setShowAddTask(null);
        } catch {
            setError("failed to create task");
        }
    };

    const handleDeleteTask = async (taskId: number) => {
        try {
            await taskApi.delete(taskId);
            setTasks((prev) => prev.filter((t) => t.id !== taskId));
        } catch {
            setError("failed to delete task");
        }
    };

    const handleAddUser = async (email: string) => {
        try {
            const res = await memberApi.add(pid, { email, role: inviteRole });
            if (res.data.status === "success") {
                fetchBoard();
            }
        } catch (err: any) {
            setError(err.response?.data?.message || "failed to add member");
        }
    };

    const handleRemoveMember = async (targetUserId: number) => {
        if (!window.confirm("Are you sure you want to remove this member?")) return;
        try {
            const res = await memberApi.remove(pid, targetUserId);
            if (res.data.status === "success") {
                fetchBoard();
            }
        } catch (err: any) {
            setError(err.response?.data?.message || "failed to remove member");
        }
    };

    if (loading) {
        return (
            <div className="page-loading">
                <div className="spinner" />
            </div>
        );
    }

    if (!project) {
        return (
            <div className="page-loading">
                <p>Project not found</p>
            </div>
        );
    }

    const stages = project.stages || [];
    const filteredUsers = allUsers.filter(u =>
        (u.full_name.toLowerCase().includes(userSearch.toLowerCase()) ||
            u.email.toLowerCase().includes(userSearch.toLowerCase())) &&
        !members.some(m => m.user_id === u.id)
    );

    return (
        <div className="board-page">
            <header className="board-header">
                <div className="header-left">
                    <button className="btn-ghost" onClick={() => navigate("/")}>
                        ← Back
                    </button>
                    <h1>{project.name}</h1>
                    <div className="header-filters">
                        <button
                            className={`btn-sm ${filterMyTasks ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setFilterMyTasks(!filterMyTasks)}
                        >
                            {filterMyTasks ? 'Showing My Tasks' : 'Filter My Tasks'}
                        </button>
                    </div>
                </div>
                <div className="header-right">
                    <button className="btn-secondary" onClick={() => setShowInvite(true)}>
                        Add Members
                    </button>
                    <span className="user-name">{user?.full_name}</span>
                    <button className="btn-ghost" onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            {error && <div className="error-banner" onClick={() => setError(null)}>{error}</div>}

            <div className="board-container">
                <DragDropContext onDragEnd={handleDragEnd}>
                    <div className="board-columns">
                        {stages
                            .sort((a, b) => a.position - b.position)
                            .map((stage) => (
                                <div key={stage.id} className="board-column">
                                    <div className="column-header">
                                        <h3>{stage.name}</h3>
                                        <span className="task-count">{getTasksForStage(stage.id).length}</span>
                                    </div>

                                    <Droppable droppableId={String(stage.id)}>
                                        {(provided, snapshot) => (
                                            <div
                                                ref={provided.innerRef}
                                                {...provided.droppableProps}
                                                className={`column-body ${snapshot.isDraggingOver ? "dragging-over" : ""}`}
                                            >
                                                {getTasksForStage(stage.id).map((task, index) => (
                                                    <Draggable key={task.id} draggableId={String(task.id)} index={index}>
                                                        {(provided, snapshot) => (
                                                            <div
                                                                ref={provided.innerRef}
                                                                {...provided.draggableProps}
                                                                {...provided.dragHandleProps}
                                                                className={`task-card ${snapshot.isDragging ? "dragging" : ""}`}
                                                            >
                                                                <div className="task-card-header">
                                                                    <span className="task-title">{task.title}</span>
                                                                    <button
                                                                        className="btn-icon"
                                                                        onClick={(e) => {
                                                                            e.stopPropagation();
                                                                            handleDeleteTask(task.id);
                                                                        }}
                                                                        title="Delete task"
                                                                    >
                                                                        ✕
                                                                    </button>
                                                                </div>
                                                                {task.description && (
                                                                    <p className="task-desc">{task.description}</p>
                                                                )}
                                                                <div className="task-card-footer">
                                                                    <select
                                                                        className="assignee-select-mini"
                                                                        value={task.assignee_id || ""}
                                                                        onChange={(e) => {
                                                                            const val = e.target.value ? Number(e.target.value) : null;
                                                                            taskApi.update(task.id, { assignee_id: val }).then(() => fetchBoard());
                                                                        }}
                                                                    >
                                                                        <option value="">No one</option>
                                                                        {members.filter(m => m.status === 'accepted').map(m => (
                                                                            <option key={m.user_id} value={m.user_id}>
                                                                                {m.user?.full_name?.split(' ')[0]}
                                                                            </option>
                                                                        ))}
                                                                    </select>
                                                                </div>

                                                            </div>
                                                        )}
                                                    </Draggable>
                                                ))}
                                                {provided.placeholder}
                                            </div>
                                        )}
                                    </Droppable>

                                    {showAddTask === stage.id ? (
                                        <form className="add-task-form" onSubmit={(e) => handleAddTask(stage.id, e)}>
                                            <input
                                                type="text"
                                                value={newTaskTitle}
                                                onChange={(e) => setNewTaskTitle(e.target.value)}
                                                placeholder="Task title..."
                                                autoFocus
                                                required
                                            />
                                            <select
                                                className="assignee-select"
                                                value={newTaskAssignee || ""}
                                                onChange={(e) => setNewTaskAssignee(e.target.value ? Number(e.target.value) : undefined)}
                                            >
                                                <option value="">No Assignee</option>
                                                {members.map(m => (
                                                    <option key={m.user_id} value={m.user_id}>
                                                        {m.user?.full_name}
                                                    </option>
                                                ))}
                                            </select>
                                            <div className="add-task-actions">
                                                <button type="submit" className="btn-sm btn-primary">
                                                    Add
                                                </button>
                                                <button
                                                    type="button"
                                                    className="btn-sm btn-ghost"
                                                    onClick={() => {
                                                        setShowAddTask(null);
                                                        setNewTaskTitle("");
                                                        setNewTaskAssignee(undefined);
                                                    }}
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </form>
                                    ) : (
                                        <button
                                            className="add-task-btn"
                                            onClick={() => setShowAddTask(stage.id)}
                                        >
                                            + Add task
                                        </button>
                                    )}
                                </div>
                            ))}
                    </div>
                </DragDropContext>
            </div>

            {/* invite modal */}
            {showInvite && (
                <div className="modal-overlay" onClick={() => setShowInvite(false)}>
                    <div className="modal-content wide-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Invite Members</h2>
                            <button className="btn-ghost" onClick={() => setShowInvite(false)}>✕</button>
                        </div>

                        <div className="invite-controls">
                            <input
                                type="text"
                                placeholder="Search users by name or email..."
                                value={userSearch}
                                onChange={(e) => setUserSearch(e.target.value)}
                                className="search-input"
                            />
                            <select
                                value={inviteRole}
                                onChange={(e) => setInviteRole(e.target.value)}
                                className="role-select"
                            >
                                <option value="member">Member</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>

                        <div className="user-selection-list">
                            {filteredUsers.length === 0 ? (
                                <p className="empty-text">No users found to invite.</p>
                            ) : (
                                filteredUsers.map(u => (
                                    <div key={u.id} className="user-invite-row">
                                        <div className="user-info">
                                            <span className="user-name">{u.full_name}</span>
                                            <span className="user-email">{u.email}</span>
                                        </div>
                                        <button
                                            className="btn-sm btn-primary"
                                            onClick={() => handleAddUser(u.email)}
                                        >
                                            Add
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>

                        {/* current members list */}
                        {members.length > 0 && (
                            <div className="members-list">
                                <h3>Current Members</h3>
                                <div className="members-scroll">
                                    {members.map((m) => (
                                        <div key={m.id} className="member-row">
                                            <div className="member-info">
                                                <span className="name">{m.user?.full_name || m.user?.email || `User #${m.user_id}`}</span>
                                                <span className="email">{m.user?.email}</span>
                                            </div>
                                            <div className="member-status">
                                                <span className="role-badge">{m.role}</span>
                                                {user?.id !== m.user_id && m.role !== 'owner' && (
                                                    <button
                                                        className="btn-sm btn-danger"
                                                        onClick={() => handleRemoveMember(m.user_id)}
                                                        title="Remove from project"
                                                    >
                                                        Remove
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

