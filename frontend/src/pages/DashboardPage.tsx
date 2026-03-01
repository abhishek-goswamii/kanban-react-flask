import { useState, useEffect, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { projectApi } from "../api/services";
import type { Project } from "../types";

export default function DashboardPage() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [projects, setProjects] = useState<Project[]>([]);
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
            const projRes = await projectApi.list();
            if (projRes.data.status === "success") setProjects(projRes.data.data || []);
        } catch {
            setError("failed to load projects");
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
