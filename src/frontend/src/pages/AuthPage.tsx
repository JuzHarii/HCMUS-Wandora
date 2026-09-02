import { useEffect, useState, type FormEvent } from "react";
import {
  ArrowRight,
  ChevronLeft,
  CircleAlert,
  LogIn,
  LoaderCircle,
  UserPlus,
} from "lucide-react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router";

import { useAuth } from "@/auth";
import { FormField } from "@/components/forms/FormField";

export function AuthPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, isLoading, login, signUp } = useAuth();
  const initialMode =
    searchParams.get("mode") === "signup" ? "signup" : "login";
  const [mode, setMode] = useState<"login" | "signup">(initialMode);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const nextPath = searchParams.get("next") || "/home";

  useEffect(() => setMode(initialMode), [initialMode]);
  if (!isLoading && user) return <Navigate replace to={nextPath} />;

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    if (mode === "signup" && fullName.trim().length < 2)
      return setError("Enter your name using at least 2 characters.");
    if (!email.includes("@")) return setError("Enter a valid email address.");
    if (password.length < 8)
      return setError("Password must contain at least 8 characters.");
    if (mode === "signup" && password !== confirmPassword)
      return setError("Password confirmation does not match.");
    setIsSubmitting(true);
    try {
      if (mode === "signup")
        await signUp({ full_name: fullName.trim(), email, password });
      else await login({ email, password });
      navigate(nextPath);
    } catch (authError) {
      setError(
        authError instanceof Error
          ? authError.message
          : "Could not authenticate this account.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  const isSignUp = mode === "signup";
  return (
    <main className="auth-page">
      <header className="flow-header">
        <Link className="wordmark" to="/">
          Wandora
        </Link>
        <Link className="back-link" to="/">
          <ChevronLeft aria-hidden="true" /> Back to landing
        </Link>
      </header>
      <section className="auth-grid" aria-labelledby="auth-title">
        <aside className="auth-intro">
          <p className="eyebrow">
            {isSignUp ? (
              <UserPlus aria-hidden="true" />
            ) : (
              <LogIn aria-hidden="true" />
            )}{" "}
            Your shared planning space
          </p>
          <h1 id="auth-title">
            {isSignUp
              ? "Start with your travel circle."
              : "Pick up the plan where you left it."}
          </h1>
          <p>
            Your account keeps each workspace private to its members, from the
            first AI draft to every revision that follows.
          </p>
        </aside>
        <div className="auth-card">
          <div className="auth-switch" aria-label="Authentication mode">
            <button
              className={mode === "login" ? "is-selected" : ""}
              type="button"
              onClick={() => setMode("login")}
            >
              Sign in
            </button>
            <button
              className={mode === "signup" ? "is-selected" : ""}
              type="button"
              onClick={() => setMode("signup")}
            >
              Create account
            </button>
          </div>
          <form onSubmit={submit} noValidate>
            {isSignUp && (
              <FormField label="Full name">
                <input
                  data-testid="signup-name"
                  autoComplete="name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  placeholder="Your name"
                />
              </FormField>
            )}
            <FormField label="Email address">
              <input
                data-testid="auth-email"
                autoComplete="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
              />
            </FormField>
            <FormField label="Password">
              <input
                data-testid="auth-password"
                autoComplete={isSignUp ? "new-password" : "current-password"}
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="At least 8 characters"
              />
            </FormField>
            {isSignUp && (
              <FormField label="Confirm password">
                <input
                  data-testid="signup-confirm-password"
                  autoComplete="new-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  placeholder="Repeat your password"
                />
              </FormField>
            )}
            {error && (
              <div className="flow-error" role="alert">
                <CircleAlert aria-hidden="true" />
                {error}
              </div>
            )}
            <button
              data-testid={isSignUp ? "signup-submit" : "login-submit"}
              className="flow-submit"
              disabled={isSubmitting}
              type="submit"
            >
              {isSubmitting ? (
                <>
                  <LoaderCircle className="spin" aria-hidden="true" /> Please
                  wait…
                </>
              ) : isSignUp ? (
                <>
                  Create account <ArrowRight aria-hidden="true" />
                </>
              ) : (
                <>
                  Sign in <ArrowRight aria-hidden="true" />
                </>
              )}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
