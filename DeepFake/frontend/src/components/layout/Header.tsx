"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Menu, X, Shield, Moon, Sun, LogOut, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { authService } from "@/lib/auth";
import type { User as UserType } from "@/types";

const Header: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [user, setUser] = useState<UserType | null>(null);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    // Check auth status on component mount
    const currentUser = authService.getUser();
    setUser(currentUser);
  }, [pathname]); // Re-check on route change

  const navigation = [
    { name: "Home", href: "/", authRequired: false },
    { name: "Detect", href: "/detect", authRequired: true },
    { name: "About", href: "/about", authRequired: false },
    { name: "History", href: "/history", authRequired: true },
    { name: "Contact", href: "/contact", authRequired: false },
  ];

  // Filter navigation based on auth status
  const visibleNav = navigation.filter((item) => !item.authRequired || user);

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    router.push("/");
  };

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
    // Here you would typically also update the document class or a global state
    document.documentElement.classList.toggle("dark");
  };

  return (
    <header className="bg-white dark:bg-gray-900 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
          >
            <Shield className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-900 dark:text-white">
              DeepDetect
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-4">
            {visibleNav.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "px-3 py-2 text-sm font-medium rounded-md transition-colors",
                  pathname === item.href
                    ? "text-primary-600 bg-primary-50 dark:bg-primary-900/20 dark:text-primary-400"
                    : "text-gray-700 dark:text-gray-300 hover:text-primary-600 hover:bg-gray-50 dark:hover:bg-gray-800 dark:hover:text-primary-400",
                )}
              >
                {item.name}
              </Link>
            ))}

            {/* Auth Buttons */}
            {user ? (
              <div className="flex items-center space-x-3 ml-4 pl-4 border-l border-gray-300 dark:border-gray-600">
                <span className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                  <User size={16} className="mr-1" />
                  {user.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                >
                  <LogOut size={16} className="mr-1" />
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 ml-4 pl-4 border-l border-gray-300 dark:border-gray-600">
                <Link
                  href="/login"
                  className="px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-primary-600 hover:bg-gray-50 dark:hover:bg-gray-800 dark:hover:text-primary-400 rounded-md transition-colors"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="px-3 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </nav>

          {/* Dark Mode Toggle & Mobile Menu Button */}
          <div className="flex items-center space-x-2">
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle dark mode"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Toggle mobile menu"
            >
              {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 dark:border-gray-700 py-4">
            <div className="flex flex-col space-y-2">
              {visibleNav.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={cn(
                    "px-3 py-2 text-base font-medium rounded-md transition-colors",
                    pathname === item.href
                      ? "text-primary-600 bg-primary-50 dark:bg-primary-900/20 dark:text-primary-400"
                      : "text-gray-700 dark:text-gray-300 hover:text-primary-600 hover:bg-gray-50 dark:hover:bg-gray-800 dark:hover:text-primary-400",
                  )}
                >
                  {item.name}
                </Link>
              ))}

              {/* Mobile Auth Buttons */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-2">
                {user ? (
                  <>
                    <div className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 flex items-center">
                      <User size={16} className="mr-2" />
                      Logged in as{" "}
                      <span className="font-medium ml-1">{user.username}</span>
                    </div>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsMobileMenuOpen(false);
                      }}
                      className="w-full flex items-center px-3 py-2 text-base font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                    >
                      <LogOut size={16} className="mr-2" />
                      Logout
                    </button>
                  </>
                ) : (
                  <div className="space-y-2">
                    <Link
                      href="/login"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="block w-full px-3 py-2 text-center text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md transition-colors"
                    >
                      Login
                    </Link>
                    <Link
                      href="/register"
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="block w-full px-3 py-2 text-center text-base font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
                    >
                      Sign Up
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
