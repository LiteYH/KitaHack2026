"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { LogOut, User, Mail, ChevronDown } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useAuth } from "@/contexts/AuthContext";

export function UserProfileDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  const handleLogout = async () => {
    try {
      await logout();
      router.push("/");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  // Get user initials for avatar fallback
  const getUserInitials = () => {
    if (!user?.email) return "U";
    const email = user.email;
    return email.charAt(0).toUpperCase();
  };

  // Get display name or email
  const getDisplayName = () => {
    if (user?.displayName) return user.displayName;
    if (user?.email) return user.email.split("@")[0];
    return "User";
  };

  if (!user) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Profile Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg p-1.5 transition-colors hover:bg-secondary"
        aria-label="User menu"
      >
        <Avatar className="h-8 w-8">
          <AvatarImage src={user.photoURL || undefined} alt={getDisplayName()} />
          <AvatarFallback className="bg-primary text-primary-foreground text-xs">
            {getUserInitials()}
          </AvatarFallback>
        </Avatar>
        <ChevronDown
          className={`h-4 w-4 text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-72 rounded-lg border border-border bg-card shadow-lg animate-in fade-in slide-in-from-top-2 z-50">
          {/* User Info Section */}
          <div className="border-b border-border p-4">
            <div className="flex items-center gap-3">
              <Avatar className="h-12 w-12">
                <AvatarImage src={user.photoURL || undefined} alt={getDisplayName()} />
                <AvatarFallback className="bg-primary text-primary-foreground text-sm">
                  {getUserInitials()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 overflow-hidden">
                <p className="font-semibold text-foreground truncate">
                  {getDisplayName()}
                </p>
                <p className="text-sm text-muted-foreground truncate">{user.email}</p>
              </div>
            </div>
          </div>

          {/* Account Details */}
          <div className="p-2">
            <div className="rounded-md p-3 hover:bg-secondary/50 transition-colors">
              <div className="flex items-center gap-2 text-sm">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Email:</span>
              </div>
              <p className="mt-1 text-sm font-medium text-foreground truncate">
                {user.email}
              </p>
            </div>

            <div className="rounded-md p-3 hover:bg-secondary/50 transition-colors">
              <div className="flex items-center gap-2 text-sm">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">Account Type:</span>
              </div>
              <p className="mt-1 text-sm font-medium text-foreground">
                {user.emailVerified ? "Verified" : "Unverified"}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="border-t border-border p-2">
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
