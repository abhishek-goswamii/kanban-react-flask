import { useState, useEffect, type FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { DragDropContext, Droppable, Draggable, type DropResult } from "@hello-pangea/dnd";
import { useAuth } from "../context/AuthContext";
import { projectApi, taskApi, memberApi } from "../api/services";
import type { Project, Stage, Task, ProjectMember } from "../types";

export default function BoardPage() {
    const { projectId } = useParams<{ projectId: string }>();
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const pid = Number(projectId);

    const [project, setProject] = useState<Project | null>(null);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [members, setMembers] = useState<ProjectMember[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // create task form
    const [showAddTask, setShowAddTask] = useState<number | null>(null);
    const [newTaskTitle, setNewTaskTitle] = useState("");

    // invite modal
    const [showInvite, setShowInvite] = useState(false);
    const [inviteEmail, setInviteEmail] = useState("");
    const [inviteRole, setInviteRole] = useState("member");

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

    const getTasksForStage = (stageId: number) =>
        tasks.filter((t) => t.stage_id === stageId).sort((a, b) => a.position - b.position);

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
            const res = await taskApi.create(pid, { title: newTaskTitle, stage_id: stageId });
            if (res.data.status === "success" && res.data.data) {
                setTasks((prev) => [...prev, res.data.data]);
            }
            setNewTaskTitle("");
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

    const handleInvite = async (e: FormEvent) => {
        e.preventDefault();
        try {
            const res = await memberApi.invite(pid, { email: inviteEmail, role: inviteRole });
            if (res.data.status === "success") {
                setShowInvite(false);
                setInviteEmail("");
                fetchBoard();
            }
        } catch (err: any) {
            setError(err.response?.data?.message || "failed to invite");
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

    return (
        <div className="board-page">
            <header className="board-header">
                <div className="header-left">
                    <button className="btn-ghost" onClick={() => navigate("/")}>
                        ← Back
                    </button>
                    <h1>{project.name}</h1>
                </div>
                <div className="header-right">
                    <button className="btn-secondary" onClick={() => setShowInvite(true)}>
                        Invite
                    </button>
                    <span className="user-name">{user?.full_name}</span>
                    <button className="btn-ghost" onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            {error && <div className="error-banner">{error}</div>}

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
                                            />
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
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Invite Member</h2>
                        <form onSubmit={handleInvite}>
                            <div className="form-group">
                                <label htmlFor="invite_email">Email</label>
                                <input
                                    id="invite_email"
                                    type="email"
                                    value={inviteEmail}
                                    onChange={(e) => setInviteEmail(e.target.value)}
                                    placeholder="colleague@example.com"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="invite_role">Role</label>
                                <select
                                    id="invite_role"
                                    value={inviteRole}
                                    onChange={(e) => setInviteRole(e.target.value)}
                                >
                                    <option value="member">Member</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                            <div className="modal-actions">
                                <button type="button" className="btn-ghost" onClick={() => setShowInvite(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn-primary">
                                    Send Invite
                                </button>
                            </div>
                        </form>

                        {/* members list */}
                        {members.length > 0 && (
                            <div className="members-list">
                                <h3>Members</h3>
                                {members.map((m) => (
                                    <div key={m.id} className="member-row">
                                        <span>{m.user?.full_name || m.user?.email || `User #${m.user_id}`}</span>
                                        <span className="role-badge">{m.role}</span>
                                        <span className={`status-badge ${m.status}`}>{m.status}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
