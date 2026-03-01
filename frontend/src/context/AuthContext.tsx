import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { User } from "../types";
import { authApi } from "../api/services";

interface AuthContextType {
    user: User | null;
    loading: boolean;
    error: string | null;
    login: (email: string, password: string) => Promise<string | null>;
    register: (email: string, fullName: string, password: string) => Promise<string | null>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // check session on mount
    useEffect(() => {
        authApi
            .me()
            .then((res) => {
                if (res.data.status === "success" && res.data.data) {
                    setUser(res.data.data);
                }
            })
            .catch(() => setUser(null))
            .finally(() => setLoading(false));
    }, []);

    const login = async (email: string, password: string): Promise<string | null> => {
        try {
            const res = await authApi.login({ email, password });
            if (res.data.status === "success") {
                const meRes = await authApi.me();
                if (meRes.data.status === "success" && meRes.data.data) {
                    setUser(meRes.data.data);
                }
                return null;
            }
            return res.data.message || "login failed";
        } catch (err: any) {
            return err.response?.data?.message || "login failed";
        }
    };

    const register = async (email: string, fullName: string, password: string): Promise<string | null> => {
        try {
            const res = await authApi.register({ email, full_name: fullName, password });
            if (res.data.status === "success") {
                return null;
            }
            return res.data.message || "registration failed";
        } catch (err: any) {
            return err.response?.data?.message || "registration failed";
        }
    };

    const logout = async () => {
        try {
            await authApi.logout();
        } catch {
            // ignore
        }
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, error, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error("useAuth must be used within AuthProvider");
    return ctx;
}
