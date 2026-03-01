import { useState, useEffect, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { projectApi, memberApi } from "../api/services";
import type { Project, ProjectMember } from "../types";

export default function DashboardPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [projects, setProjects] = useState<Project[]>([]);
    const [invitations, setInvitations] = useState<ProjectMember[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // create project modal
    const [showCreate, setShowCreate] = useState(false);
    const [newName, setNewName] = useState("");
    const [newDesc, setNewDesc] = useState("");
    const [creating, setCreating] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [projRes, invRes] = await Promise.all([
                projectApi.list(),
                memberApi.invitations(),
            ]);
            if (projRes.data.status === "success") setProjects(projRes.data.data || []);
            if (invRes.data.status === "success") setInvitations(invRes.data.data || []);
        } catch {
            setError("failed to load data");
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: FormEvent) => {
        e.preventDefault();
        setCreating(true);
        try {
            const res = await projectApi.create({ name: newName, description: newDesc });
            if (res.data.status === "success") {
                setShowCreate(false);
                setNewName("");
                setNewDesc("");
                fetchData();
            }
        } catch {
            setError("failed to create project");
        } finally {
            setCreating(false);
        }
    };

    const handleAccept = async (id: number) => {
        try {
            await memberApi.accept(id);
            fetchData();
        } catch {
            setError("failed to accept invitation");
        }
    };

    const handleReject = async (id: number) => {
        try {
            await memberApi.reject(id);
            fetchData();
        } catch {
            setError("failed to reject invitation");
        }
    };

    if (loading) {
        return (
            <div className="page-loading">
                <div className="spinner" />
            </div>
        );
    }

    return (
        <div className="dashboard-page">
            <header className="dashboard-header">
                <div className="header-left">
                    <h1 className="logo">Kanban</h1>
                </div>
                <div className="header-right">
                    <span className="user-name">{user?.full_name}</span>
                    <button className="btn-ghost" onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            <main className="dashboard-main">
                {error && <div className="error-banner">{error}</div>}

                {/* invitations */}
                {invitations.length > 0 && (
                    <section className="invitations-section">
                        <h2>Pending Invitations</h2>
                        <div className="invitation-list">
                            {invitations.map((inv) => (
                                <div key={inv.id} className="invitation-card">
                                    <div className="invitation-info">
                                        <span className="invitation-project">{inv.project_name}</span>
                                        <span className="invitation-role">{inv.role}</span>
                                    </div>
                                    <div className="invitation-actions">
                                        <button className="btn-sm btn-success" onClick={() => handleAccept(inv.id)}>
                                            Accept
                                        </button>
                                        <button className="btn-sm btn-danger" onClick={() => handleReject(inv.id)}>
                                            Reject
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* projects */}
                <section className="projects-section">
                    <div className="section-header">
                        <h2>My Projects</h2>
                        <button className="btn-primary" onClick={() => setShowCreate(true)}>
                            + New Project
                        </button>
                    </div>

                    {projects.length === 0 ? (
                        <div className="empty-state">
                            <p>No projects yet. Create your first one!</p>
                        </div>
                    ) : (
                        <div className="project-grid">
                            {projects.map((project) => (
                                <div
                                    key={project.id}
                                    className="project-card"
                                    onClick={() => navigate(`/project/${project.id}`)}
                                >
                                    <h3>{project.name}</h3>
                                    <p>{project.description || "No description"}</p>
                                    <div className="project-meta">
                                        <span className="role-badge">{project.role}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </main>

            {/* create project modal */}
            {showCreate && (
                <div className="modal-overlay" onClick={() => setShowCreate(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Create Project</h2>
                        <form onSubmit={handleCreate}>
                            <div className="form-group">
                                <label htmlFor="project_name">Project Name</label>
                                <input
                                    id="project_name"
                                    type="text"
                                    value={newName}
                                    onChange={(e) => setNewName(e.target.value)}
                                    placeholder="My Project"
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="project_desc">Description</label>
                                <textarea
                                    id="project_desc"
                                    value={newDesc}
                                    onChange={(e) => setNewDesc(e.target.value)}
                                    placeholder="Describe your project..."
                                    rows={3}
                                />
                            </div>
                            <div className="modal-actions">
                                <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn-primary" disabled={creating}>
                                    {creating ? "Creating..." : "Create"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
